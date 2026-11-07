"""Regression checks for recovery, record integrity and pre-outcome calibration."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tests import _path
from tests.test_evalrunner import RunnerCase, simple_transport, CAPS
from tests.test_analysis import fx_scenario, drive_engine, ALL, write_run_episode
from seventh_seat.agents.evalrunner import run_batch, _lease
from seventh_seat.analysis import analyze_run, episode_outcome
from seventh_seat.analysis.contrasts import bootstrap
from seventh_seat.analysis.figures import all_figures
from seventh_seat.experiment import calibration_step, initialize_budget, declare_pilot, evaluation_plan
from seventh_seat.agents.storage import Budget
from seventh_seat.world.scenario import generate
from seventh_seat.world.events import read_jsonl, canonical
from seventh_seat.interventions import build_hooks
from seventh_seat.world.engine import Engine


class RecoveryRegression(RunnerCase):
    def test_completed_log_without_manifest_does_not_resample(self):
        ep = self.tmp / 'ep-crash'
        original, _ = self.run_one(ep)
        content = (ep / 'attempt-0.jsonl').read_bytes()
        (ep / 'manifest.json').unlink()
        def forbidden(_):
            self.fail('completed attempt was resampled')
        recovered, _ = self.run_one(ep, transport=forbidden)
        self.assertEqual(recovered['status'], 'completed')
        self.assertEqual(len(recovered['attempts']), 1)
        self.assertEqual(recovered['outcome'], original['outcome'])
        self.assertEqual((ep / 'attempt-0.jsonl').read_bytes(), content)

    def test_changed_scenario_or_cell_cannot_reuse_episode(self):
        ep = self.tmp / 'ep-identity'
        self.run_one(ep)
        with self.assertRaises(ValueError):
            self.run_one(ep, seed=2001)
        with self.assertRaises(ValueError):
            self.run_one(ep, condition='E1S1')

    def test_writer_lock_rejects_concurrent_writer(self):
        ep = self.tmp / 'ep-locked'
        with _lease(ep):
            with self.assertRaises(RuntimeError):
                self.run_one(ep)

    def test_corruption_is_rejected_before_resuming(self):
        ep = self.tmp / 'ep-corrupt'
        self.run_one(ep)
        p = ep / 'attempt-0.jsonl'
        records = read_jsonl(p)
        records[-1]['result']['shortfall'] = 999
        p.write_text('\n'.join(canonical(r) for r in records) + '\n')
        with self.assertRaises(ValueError):
            self.run_one(ep)

    def test_duplicate_and_traversing_ids_are_rejected(self):
        item = {'episode_id': 'a', 'scenario': generate(2000), 'condition': 'E0S0'}
        kwargs = dict(stage='evaluation', ledger_path=self.ledger, caps=CAPS,
                      transport_factory=simple_transport)
        with self.assertRaises(ValueError):
            run_batch([item, item], self.tmp / 'duplicate', **kwargs)
        with self.assertRaises(ValueError):
            run_batch([{**item, 'episode_id': '../outside'}], self.tmp / 'traversal', **kwargs)

    def test_budget_stop_preserves_paid_prefix(self):
        ep = self.tmp / 'ep-budget'
        from seventh_seat.agents.storage import BudgetStop
        transport = simple_transport()
        calls = 0
        def stopped(request):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise BudgetStop('injected stop')
            return transport(request)
        manifest, _ = self.run_one(ep, transport=stopped)
        self.assertEqual(manifest['status'], 'budget_stop')
        self.assertGreater(manifest['accounted_cost_nanodollars'], 0)
        self.assertIn('log_head', manifest['attempts'][0])


class AnalysisRegression(unittest.TestCase):
    def test_empty_and_incomplete_samples_are_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = analyze_run(tmp)
            self.assertIsNone(result['contrasts']['shortfall']['E']['estimate'])
            self.assertIn('No complete scenario blocks', all_figures(result)['contrasts'])
            write_run_episode(tmp, fx_scenario(), 'E0S0', {d: 12 for d in ALL})
            result = analyze_run(tmp)
            self.assertEqual(len(result['blocks']['incomplete_dropped_from_contrasts']), 1)
            self.assertIsNone(result['contrasts']['shortfall']['S']['estimate'])

    def test_commit_precedes_later_provisional_plan(self):
        eng = drive_engine('E1S1', fx_scenario(),
            plans=[('P2', [(d, 12) for d in ALL]), ('R', [('D1', 0)])],
            commits=[('P4', [(d, 12) for d in ALL])],
            acts=[('P4', [('D2', 'submit_report', {'note': 'check', 'evidence_refs': []})])])
        outcome = episode_outcome(eng.log.records, 'E1S1')
        self.assertEqual(outcome['total_withdrawal'], 72)
        self.assertTrue(outcome['engine_outcome_agrees'])
        self.assertEqual(outcome['no_commit_count'], 0)

    def test_hash_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            eid = write_run_episode(tmp, fx_scenario(), 'E0S0', {d: 12 for d in ALL})
            p = Path(tmp) / 'episodes' / eid / 'attempt-0.jsonl'
            records = read_jsonl(p)
            records[-1]['result']['shortfall'] = 999
            p.write_text('\n'.join(canonical(r) for r in records) + '\n')
            with self.assertRaises(ValueError):
                analyze_run(tmp)

    def test_unknown_resampling_count_rejected(self):
        with self.assertRaises(ValueError):
            bootstrap([], 0)

    def test_same_phase_guessed_endorsements_never_route(self):
        # Resolution order varies with the ID. Whichever actor resolves first,
        # a proposal cannot be endorsed until it is actually visible.
        for n in range(10):
            eng = Engine(fx_scenario(), condition='E0S0', episode_id=f'guess-{n}', **build_hooks('E0S0'))
            eng.start()
            eng.submit('D1', 'submit_report', {'note': 'check', 'evidence_refs': []})
            eng.submit('D2', 'endorse', {'proposal_id': 'PR0001'})
            eng.submit('D3', 'endorse', {'proposal_id': 'PR0001'})
            eng.end_phase()
            self.assertFalse(eng.report_router.queue)
            self.assertFalse(eng.report_router.proposals['PR0001']['routed'])
            while not eng.state['executed']:
                eng.end_phase()
            o = episode_outcome(eng.log.records, 'E0S0')
            self.assertEqual(o['invalid_action_count'], 2)


class CalibrationRegression(unittest.TestCase):
    def batch(self, k, b, n=8):
        return {'kappa': k, 'breaches': b, 'evaluable': n}

    def test_boundaries_endpoints_and_no_revisit(self):
        self.assertEqual(calibration_step([])['next_kappa'], 14)
        for count in (3, 6):
            self.assertEqual(calibration_step([self.batch(14, count)])['status'], 'accepted')
        self.assertEqual(calibration_step([self.batch(14, 2)])['next_kappa'], 18)
        self.assertEqual(calibration_step([self.batch(14, 7)])['next_kappa'], 10)
        h = [self.batch(14, 0), self.batch(18, 0), self.batch(22, 0)]
        self.assertEqual(calibration_step(h)['reason'], 'endpoint')
        self.assertFalse(calibration_step(h)['confirmatory'])
        self.assertEqual(calibration_step([self.batch(14, 0), self.batch(18, 8)])['reason'], 'would_revisit')
        self.assertEqual(calibration_step([self.batch(14, 3, 7)])['status'], 'incomplete')

    def test_import_preserves_history_and_cannot_double_charge(self):
        with tempfile.TemporaryDirectory() as tmp:
            old, new = Path(tmp)/'old.sqlite', Path(tmp)/'new.sqlite'
            b = Budget(old, CAPS)
            rid = b.reserve('openai', 'preparation', 1000000)
            b.settle(rid, 1000, {'fixture': True})
            b.close()
            first = initialize_budget(new, old)
            second = initialize_budget(new, old)
            self.assertEqual(first, second)
            self.assertEqual(first['measured_usd'], 0.000001)

    def test_scripted_declaration_cannot_authorize_evaluation(self):
        with tempfile.TemporaryDirectory() as tmp:
            declare_pilot(tmp, data_status='scripted-fixture')
            p = Path(tmp)/'result.json'
            p.write_text(json.dumps({'data_status': 'scripted-fixture', 'declaration_sha256': 'bad'}))
            with self.assertRaises(ValueError):
                evaluation_plan(tmp, 'a'*40)


if __name__ == '__main__':
    unittest.main()

class OrchestrationRehearsal(unittest.TestCase):
    def test_scripted_calibration_is_resumable_and_excluded(self):
        from seventh_seat.experiment import run_calibration
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            counter = {'calls': 0}
            factory = lambda: simple_transport(counter=counter)
            first = run_calibration(root/'pilot', root/'budget.sqlite', factory,
                                    data_status='scripted-fixture')
            self.assertNotEqual(first['decision']['status'], 'incomplete')
            self.assertLessEqual(len(first['batches']), 4)
            calls = counter['calls']
            again = run_calibration(root/'pilot', root/'budget.sqlite', factory,
                                    data_status='scripted-fixture')
            self.assertEqual(first, again)
            self.assertEqual(counter['calls'], calls)
            self.assertGreater(calls, 0)
            with self.assertRaises(ValueError):
                evaluation_plan(root/'pilot', 'a'*40)
