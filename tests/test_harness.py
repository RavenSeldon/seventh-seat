"""Wednesday G1/G2/G6/GA: adversarial wire fixtures, never model qualification."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from tests import _path  # noqa: F401
from seventh_seat.agents.providers import Adapter, InfrastructureError
from seventh_seat.agents.runtime import Caller, cost, drive, no_hazard_scenario, reservation, run_with_recovery
from seventh_seat.agents.storage import Budget, BudgetStop, CacheMiss, ResponseCache, dollars
from seventh_seat.agents.tools import definitions, dispatch
from seventh_seat.world.engine import Engine
from seventh_seat.world.events import verify_records


def wire(provider, calls=(), stop=None):
    if provider == "openai":
        return {"id": "resp_fixture", "model": "gpt-6-luna", "status": stop or "completed",
                "output": [{"type": "reasoning", "id": "rs_fixture", "summary": [], "encrypted_content": "OPAQUE"}] +
                [{"type": "function_call", "id": f"fc{i}", "call_id": f"c{i}", "name": n,
                  "arguments": json.dumps(a)} for i, (n, a) in enumerate(calls)],
                "usage": {"input_tokens": 100, "output_tokens": 20, "input_tokens_details": {"cached_tokens": 10}}}
    return {"id": "msg_fixture", "model": "claude-haiku-5-5", "stop_reason": stop or ("tool_use" if calls else "end_turn"),
            "content": [{"type": "thinking", "thinking": "", "signature": "OPAQUE"}] +
            [{"type": "tool_use", "id": f"c{i}", "name": n, "input": a} for i, (n, a) in enumerate(calls)],
            "usage": {"input_tokens": 100, "output_tokens": 20}}


def fixture_transport(provider):
    def transport(request):
        history = request.get("input", request.get("messages"))
        # Fixture policy reads only the permitted observation; no engine access.
        obs = next(json.loads(m["content"]) for m in reversed(history)
                   if m.get("role") == "user" and isinstance(m.get("content"), str))
        last = history[-1]
        is_observation = last.get("role") == "user" and isinstance(last.get("content"), str)
        if not is_observation:
            return wire(provider)
        phase = obs["phase"]
        if phase in ("P2", "P4"):
            return wire(provider, [("commit" if phase == "P4" else "plan", {"river": 8, "alt": 0})])
        return wire(provider, [("read_ledger", {})])
    return transport


class AdapterTests(unittest.TestCase):
    def test_config_and_world_tool_allowlist(self):
        for provider in ("openai", "anthropic"):
            a = Adapter(provider); a.observe("observation")
            r = a.request()
            self.assertEqual(len(r["tools"]), 9)
            self.assertEqual({t["name"] for t in r["tools"]}, {t["name"] for t in definitions()})
            self.assertTrue(all(k not in r for k in ("temperature", "top_p", "top_k")))
            self.assertEqual(r.get("reasoning", r.get("output_config"))["effort"], "medium")

    def test_sequential_parallel_and_phase_continuity(self):
        for provider in ("openai", "anthropic"):
            a = Adapter(provider); a.observe("phase one")
            for calls in ([('read_ledger', {})], [('read_ledger', {}), ('post', {'text': 'hello'})]):
                before = copy.deepcopy(a.history)
                raw = wire(provider, calls); saved = copy.deepcopy(raw)
                reply = a.receive(raw)
                self.assertEqual(a.history[:len(before)], before)
                a.results([(c['id'], {'ok': True, 'result': 'queued'}) for c in reply.calls])
                self.assertEqual(raw, saved)
                self.assertIn('OPAQUE', json.dumps(a.request()))
                if provider == "anthropic":
                    self.assertEqual(len(a.history[-1]['content']), len(calls))
                else:
                    self.assertEqual([x['call_id'] for x in a.history[-len(calls):]], [c['id'] for c in reply.calls])
            before = copy.deepcopy(a.history); a.observe("phase two")
            self.assertEqual(a.history[:len(before)], before)
            request = a.request(); request.get('input', request.get('messages')).clear()
            self.assertTrue(a.history)

    def test_refusal_and_truncation_categories(self):
        a = Adapter('anthropic')
        r = wire('anthropic', stop='refusal'); r['stop_details'] = {'category': 'test'}
        self.assertEqual(a.receive(r).details, {'category': 'test'})
        self.assertEqual(a.receive(wire('anthropic', stop='max_tokens')).category, 'truncation')
        a = Adapter('openai')
        r = wire('openai');r['output'].append({'type':'message','content':[{'type':'refusal','refusal':'No'}]})
        self.assertEqual(a.receive(r).category, 'provider_refusal')
        self.assertEqual(a.receive(wire('openai', stop='incomplete')).category, 'truncation')

    def test_no_cross_agent_history(self):
        a, b = Adapter('anthropic'), Adapter('anthropic')
        a.observe('PRIVATE'); a.receive(wire('anthropic'))
        self.assertNotIn('PRIVATE', json.dumps(b.request()))
        self.assertNotIn('OPAQUE', json.dumps(b.request()))


class ContainmentTests(unittest.TestCase):
    def setUp(self):
        self.e = Engine(no_hazard_scenario()); self.e.start()

    def test_hostile_tools_and_identity_cannot_execute(self):
        for name, args in [('shell', {'command':'touch /tmp/seventh-should-not-exist'}),
                           ('read_ledger', {'actor_id':'D2'}), ('__import__', {'name':'os'})]:
            self.assertFalse(dispatch(self.e,'D1',name,args)['ok'])
        self.assertEqual(self.e.attention['D1'],3)
        self.assertEqual(self.e.attention['D2'],0)
        self.assertEqual(self.e.queue, [])
        self.assertEqual([r['actor_id'] for r in self.e.log.records[-3:]], ['D1']*3)

    def test_invalid_json_bool_nan_extra_keys_consume_budget(self):
        for raw in ('{', {'river':True,'alt':0}, {'river':2,'alt':0,'extra':1}):
            self.assertFalse(dispatch(self.e,'D1','plan',raw)['ok'])
        self.assertEqual(self.e.attention['D1'],3)
        self.assertFalse(dispatch(self.e,'D2','offer',{'to':'D3','units':1,'price':float('nan')})['ok'])

    def test_parallel_overrun_logged_without_mutation(self):
        for i in range(5):
            result=dispatch(self.e,'D1','post',{'text':str(i)})
            self.assertEqual(result['ok'], i < 3)
        self.assertEqual(self.e.attention['D1'],3)
        self.e.end_phase()
        self.assertEqual(len(self.e.state['board']),3)
        rejected=[r for r in self.e.log.records if r['authorized'] is False]
        self.assertEqual(len(rejected),2)
        self.assertTrue(all(r['attention_left']==0 for r in rejected))

    def test_snapshots_and_private_concerns_do_not_leak(self):
        dispatch(self.e,'D1','post',{'text':'next phase'})
        dispatch(self.e,'D1','submit_concern',{'note':'PRIVATE','evidence_refs':[]})
        self.assertNotIn('next phase', json.dumps(self.e.view('D2')))
        self.e.end_phase()
        self.assertIn('next phase', json.dumps(self.e.view('D2')))
        self.assertNotIn('PRIVATE', json.dumps(self.e.view('D2')))


class BudgetTests(unittest.TestCase):
    def test_reservations_persist_and_unknown_usage_stays_charged(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'budget.sqlite'
            b=Budget(p, {'total':2,'preparation':2,'openai':1})
            rid=b.reserve('openai','preparation',dollars('.8')); b.uncertain(rid,{'timeout':True}); b.close()
            b=Budget(p, {'total':2,'preparation':2,'openai':1})
            with self.assertRaises(BudgetStop): b.reserve('openai','preparation',dollars('.3'))
            self.assertEqual(b.summary()['unresolved_requests'],1);b.close()

    def test_settlement_releases_unused_reservation_and_double_settle_fails(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b', {'openai':1})
            rid=b.reserve('openai','preparation',dollars('.9')); b.settle(rid,dollars('.1'),{})
            b.reserve('openai','preparation',dollars('.9'))
            with self.assertRaises(ValueError): b.settle(rid,0,{})
            b.close()

    def test_concurrent_reservations_cannot_overspend(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'b'; caps={'openai':1}
            Budget(p,caps).close()
            def task(_):
                b=Budget(p,caps)
                try: b.reserve('openai','preparation',dollars('.6'));return True
                except BudgetStop:return False
                finally:b.close()
            with ThreadPoolExecutor(2) as pool: self.assertEqual(sum(pool.map(task, range(2))),1)

    def test_protocol_caps_and_invalid_values(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError): Budget(Path(td)/'b', {'total':101})
        for x in ('NaN','Infinity',-1):
            with self.assertRaises(ValueError): dollars(x)

    def test_usage_and_full_context_reservation(self):
        self.assertEqual(cost('openai',wire('openai')),90*125+10*10+20*500)
        self.assertEqual(cost('anthropic',wire('anthropic')),100*100+20*500)
        for p in ('openai','anthropic'):
            self.assertGreater(reservation(p,2048),cost(p,wire(p)))
        r=wire('openai');r['usage']['input_tokens_details']['cached_tokens']=101
        with self.assertRaises(ValueError):cost('openai',r)


class ReplayTests(unittest.TestCase):
    def test_complete_episodes_replay_identical_hash_chain_both_providers(self):
        for p in ('openai','anthropic'):
            with self.subTest(provider=p), tempfile.TemporaryDirectory() as td:
                cache=ResponseCache(Path(td)/'cache'); b=Budget(Path(td)/'b', {p:2})
                a=Engine(no_hazard_scenario(),episode_id='test')
                drive(a,Caller(p,cache,b,fixture_transport(p)))
                spend=b.summary()
                z=Engine(no_hazard_scenario(),episode_id='test')
                drive(z,Caller(p,cache,replay=True))
                self.assertEqual(a.state_hashes(),z.state_hashes());self.assertEqual(a.log.head,z.log.head)
                self.assertEqual(verify_records(a.log.records),(True,None))
                self.assertEqual(a.outcome['demand_met'],48)
                self.assertEqual(b.summary(),spend)
                self.assertNotIn('OPAQUE',json.dumps(a.log.records));b.close()

    def test_cache_miss_and_tampering_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            cache=ResponseCache(td); c=Caller('openai',cache,replay=True)
            with self.assertRaises(CacheMiss):c.call({'model':'test'},{})
            key=cache.key('openai',{},{});cache.put(key,{'response':'x'})
            path=Path(td)/(key+'.json');data=json.loads(path.read_text());data['payload']['response']='forged';path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):cache.get(key)

    def test_fixed_retry_backoff_identical_payload_and_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b',{'openai':2});seen=[];delays=[]
            def transport(r):
                seen.append(copy.deepcopy(r))
                if len(seen)<3:raise InfrastructureError('rate_limit',429)
                return wire('openai')
            c=Caller('openai',ResponseCache(Path(td)/'cache'),b,transport,sleep=delays.append)
            a=Adapter('openai');a.observe('hello');before=copy.deepcopy(a.history)
            _, payload=c.call(a.request(),{})
            self.assertEqual(delays,[2,2]);self.assertEqual(seen,[seen[0]]*3)
            self.assertEqual(a.history,before);self.assertEqual(len(payload['attempts']),3)
            self.assertEqual(b.summary()['unresolved_requests'],2);b.close()

    def test_refusal_truncation_abstention_are_no_action_and_not_retried(self):
        for p,stop in [('anthropic','refusal'),('anthropic','max_tokens'),('openai','incomplete'),('openai','completed')]:
            with self.subTest(provider=p,stop=stop),tempfile.TemporaryDirectory() as td:
                b=Budget(Path(td)/'b',{p:2}); calls=[]
                def transport(r):calls.append(r);return wire(p,stop=stop)
                e=Engine(no_hazard_scenario());drive(e,Caller(p,ResponseCache(Path(td)/'c'),b,transport))
                self.assertEqual(len(calls),24);self.assertEqual(e.outcome['no_commit_count'],6)
                self.assertEqual(e.outcome['total_withdrawal'],0);b.close()

    def test_one_episode_rerun_same_seed_then_missing(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b',{'openai':3});calls=[]
            def fail(r):calls.append(r);raise InfrastructureError('network')
            c=Caller('openai',ResponseCache(Path(td)/'cache'),b,fail,sleep=lambda _:None)
            s=run_with_recovery(c,Path(td)/'run')
            self.assertEqual(s['status'],'missing');self.assertEqual(len(calls),6)
            self.assertEqual(calls,[calls[0]]*6)
            replay=run_with_recovery(Caller('openai',c.cache,replay=True),Path(td)/'replay')
            self.assertEqual(s,replay);b.close()

    def test_budget_stop_prevents_transport(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b',{'openai':.01});calls=[]
            c=Caller('openai',ResponseCache(Path(td)/'cache'),b,lambda r:calls.append(r))
            s=run_with_recovery(c,Path(td)/'run')
            self.assertEqual(s['status'],'budget_stop');self.assertFalse(calls);b.close()

    def test_missing_usage_keeps_reservation_and_halts(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b',{'openai':1})
            c=Caller('openai',ResponseCache(Path(td)/'cache'),b,lambda r:{'output':[]})
            with self.assertRaises(BudgetStop):c.call(Adapter('openai').request(),{})
            self.assertEqual(b.summary()['unresolved_requests'],1);b.close()


class EdgeCaseTests(unittest.TestCase):
    def test_cache_write_rates_are_itemized_when_available(self):
        r=wire('openai')
        r['usage']['input_tokens_details']['cache_write_tokens']=20
        self.assertEqual(cost('openai',r),70*100+20*125+10*10+20*500)
        r=wire('anthropic')
        r['usage'].update(cache_creation_input_tokens=20,
                          cache_creation={'ephemeral_5m_input_tokens':15,'ephemeral_1h_input_tokens':5})
        self.assertEqual(cost('anthropic',r),100*100+15*125+5*200+20*500)

    def test_overrun_persistently_blocks_future_scheduling(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'b';b=Budget(path,{'openai':2})
            rid=b.reserve('openai','preparation',1)
            with self.assertRaises(BudgetStop):b.settle(rid,2,{})
            b.close();b=Budget(path,{'openai':2})
            with self.assertRaises(BudgetStop):b.reserve('openai','preparation',1)
            b.close()

    def test_content_filter_is_explicit_refusal(self):
        r=wire('openai',stop='incomplete');r['incomplete_details']={'reason':'content_filter'}
        self.assertEqual(Adapter('openai').receive(r).category,'provider_refusal')

    def test_complete_tool_inside_truncation_is_not_executed(self):
        for provider in ('openai','anthropic'):
            with tempfile.TemporaryDirectory() as td:
                b=Budget(Path(td)/'b',{provider:2})
                def transport(request):
                    return wire(provider,[('post',{'text':'MUST NOT EXECUTE'})],
                                stop='incomplete' if provider=='openai' else 'max_tokens')
                e=Engine(no_hazard_scenario())
                drive(e,Caller(provider,ResponseCache(Path(td)/'cache'),b,transport))
                self.assertEqual(e.state['board'],[])
                self.assertEqual(sum(e.attention.values()),0)
                self.assertTrue(all(r['result']['category']=='truncation' for r in e.log.records if r['action']=='model_call'))
                b.close()

    def test_invalid_call_result_reaches_agent_within_existing_budget(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b',{'openai':2});requests=[]
            def transport(request):
                requests.append(copy.deepcopy(request))
                if len(requests)==1:
                    return wire('openai',[('shell',{'cmd':'no'}),('read_ledger',{})])
                return wire('openai')
            e=Engine(no_hazard_scenario())
            drive(e,Caller('openai',ResponseCache(Path(td)/'cache'),b,transport))
            results=[r for r in requests[1]['input'] if r.get('type')=='function_call_output']
            self.assertEqual(len(results),2)
            self.assertFalse(json.loads(results[0]['output'])['ok'])
            self.assertTrue(json.loads(results[1]['output'])['ok'])
            self.assertEqual([r for r in e.log.records if r['action']=='shell'][0]['attention_spent'],1)
            b.close()

    def test_episode_recovery_success_preserves_first_failure(self):
        with tempfile.TemporaryDirectory() as td:
            b=Budget(Path(td)/'b',{'openai':3});calls=[];fixture=fixture_transport('openai')
            def transport(request):
                calls.append(request)
                if len(calls)<=3:raise InfrastructureError('network')
                return fixture(request)
            c=Caller('openai',ResponseCache(Path(td)/'cache'),b,transport,sleep=lambda _:None)
            result=run_with_recovery(c,Path(td)/'live')
            self.assertEqual([a['status'] for a in result['attempts']],['infrastructure_error','completed'])
            replay=run_with_recovery(Caller('openai',c.cache,replay=True),Path(td)/'replay')
            self.assertEqual(result,replay)
            self.assertEqual(calls[0],calls[3]);b.close()

    def test_cache_namespace_separates_subjects_and_attempts(self):
        with tempfile.TemporaryDirectory() as td:
            c=ResponseCache(td);request=Adapter('openai').request()
            self.assertNotEqual(c.key('openai',request,{'actor':'D1'}),c.key('openai',request,{'actor':'D2'}))
            self.assertNotEqual(c.key('openai',request,{'episode_attempt':0}),c.key('openai',request,{'episode_attempt':1}))
