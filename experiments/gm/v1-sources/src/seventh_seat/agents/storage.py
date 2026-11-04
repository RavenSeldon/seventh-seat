"""Content-addressed responses and transactional persistent USD reservations."""
import json
import os
from pathlib import Path
import sqlite3
import uuid
from decimal import Decimal, ROUND_CEILING

from ..world.events import canonical, sha256_hex

NANO = 1_000_000_000


def dollars(value):
    d = Decimal(str(value))
    if not d.is_finite() or d < 0:
        raise ValueError("budget must be a finite nonnegative USD amount")
    return int((d * NANO).to_integral_value(rounding=ROUND_CEILING))


class BudgetStop(RuntimeError):
    pass


class Budget:
    def __init__(self, path, caps):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        os.chmod(self.path, 0o600)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS caps (scope TEXT PRIMARY KEY, amount INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS charges (id TEXT PRIMARY KEY, provider TEXT, stage TEXT,
          reserved INTEGER NOT NULL, actual INTEGER, status TEXT NOT NULL, detail TEXT);
        ''')
        limits = {"total": 100, "preparation": 20, **caps}
        if dollars(limits["total"]) > dollars(100) or dollars(limits["preparation"]) > dollars(20):
            raise ValueError("E-010 ceiling cannot be increased")
        with self.transaction():
            for scope, amount in limits.items():
                value = dollars(amount)
                old = self.db.execute("SELECT amount FROM caps WHERE scope=?", (scope,)).fetchone()
                if old and old[0] != value:
                    raise ValueError("existing budget caps are immutable; reuse the recorded caps")
                self.db.execute("INSERT OR IGNORE INTO caps VALUES (?,?)", (scope, value))

    def transaction(self):
        from contextlib import contextmanager
        @contextmanager
        def tx():
            self.db.execute("BEGIN IMMEDIATE")
            try:
                yield
            except BaseException:
                self.db.rollback()
                raise
            else:
                self.db.commit()
        return tx()

    def reserve(self, provider, stage, amount):
        if stage not in ("preparation", "evaluation") or provider not in ("openai", "anthropic"):
            raise ValueError("unknown budget scope")
        if type(amount) is not int or amount <= 0:
            raise ValueError("reservation must be positive integer nanodollars")
        rid = uuid.uuid4().hex
        with self.transaction():
            if self.db.execute("SELECT 1 FROM charges WHERE status='overrun' LIMIT 1").fetchone():
                raise BudgetStop("ledger contains an overrun; reconcile before scheduling")
            for scope, where, args in (("total", "1=1", ()),
                                       (provider, "provider=?", (provider,)),
                                       (stage, "stage=?", (stage,))):
                cap = self.db.execute("SELECT amount FROM caps WHERE scope=?", (scope,)).fetchone()
                if not cap:
                    if scope == "evaluation":
                        continue
                    raise BudgetStop("provider cap must be configured")
                used = self.db.execute(f"SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM charges WHERE {where}", args).fetchone()[0]
                if used + amount > cap[0]:
                    raise BudgetStop(f"insufficient reserved headroom: {scope}")
            self.db.execute("INSERT INTO charges VALUES (?,?,?,?,NULL,'pending',NULL)", (rid, provider, stage, amount))
        return rid

    def settle(self, rid, actual, detail):
        if type(actual) is not int or actual < 0:
            raise ValueError("invalid charge")
        with self.transaction():
            row = self.db.execute("SELECT reserved,status FROM charges WHERE id=?", (rid,)).fetchone()
            if not row or row[1] != "pending":
                raise ValueError("reservation missing or already settled")
            self.db.execute("UPDATE charges SET actual=?,status=?,detail=? WHERE id=?",
                            (actual, "overrun" if actual > row[0] else "settled", canonical(detail), rid))
        if actual > row[0]:
            raise BudgetStop("usage exceeded reservation; halt and audit pricing")

    def uncertain(self, rid, detail):
        # Lost responses may have been billed. Keep the entire reservation charged.
        with self.transaction():
            self.db.execute("UPDATE charges SET status='uncertain',detail=? WHERE id=? AND status='pending'", (canonical(detail), rid))

    def summary(self):
        return {"accounted_usd": self.db.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM charges").fetchone()[0] / NANO,
                "measured_usd": self.db.execute("SELECT COALESCE(SUM(actual),0) FROM charges").fetchone()[0] / NANO,
                "unresolved_requests": self.db.execute("SELECT COUNT(*) FROM charges WHERE actual IS NULL").fetchone()[0]}

    def close(self):
        self.db.close()


class CacheMiss(RuntimeError):
    pass


class ResponseCache:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)

    def key(self, provider, request, namespace):
        # Namespace separates agents/episodes/attempts with identical prompts.
        return sha256_hex(canonical({"version": 1, "provider": provider, "request": request, "namespace": namespace}))

    def get(self, key):
        path = self.root / (key + ".json")
        if not path.exists():
            return None
        item = json.loads(path.read_text())
        if item.get("key") != key or item.get("hash") != sha256_hex(canonical(item["payload"])):
            raise ValueError("response cache integrity failure")
        return item["payload"]

    def put(self, key, payload):
        item = {"key": key, "payload": payload, "hash": sha256_hex(canonical(payload))}
        path = self.root / (key + ".json")
        # Atomic publication; no partially written cache hit after interruption.
        tmp = self.root / (uuid.uuid4().hex + ".tmp")
        fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(canonical(item)); f.flush(); os.fsync(f.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            if self.get(key) != payload:
                raise ValueError("conflicting cache entry")
        finally:
            tmp.unlink()
