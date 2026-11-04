import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from bridge.agents import AgentBridge, configured_agent, INSTRUCTIONS
from bridge.gateway import Store, handle_update


class MockTelegram:
    def __init__(self):
        self.sent=[]

    def send(self, who, body):
        self.sent.append((who,body))


class FakeAgent:
    def __init__(self):
        self.calls=[]

    def answer(self, role, text, key):
        self.calls.append((role,text,key))
        return "Resposta fictícia"


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=Store(str(Path(self.temp.name)/"test.sqlite"))
        self.now=datetime(2026,11,4,12,tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def bridge(self, max_per_day=30):
        return AgentBridge("fake-key","fake-model",self.store,max_per_day=max_per_day)

    def test_disabled_by_default(self):
        with patch.dict("os.environ",{},clear=True):
            self.assertIsNone(configured_agent(self.store))

    def test_text_only_and_store_false(self):
        agent=self.bridge()
        with patch.object(agent,"_request_response",return_value={
            "status":"completed",
            "output":[{"type":"message","content":[{"type":"output_text","text":"Explicação clara."}]}]
        }) as mock:
            answer=agent.answer("tutor","Explique o tópico","tutor:100",now=self.now)
        self.assertEqual(answer,"Explicação clara.")
        sent=mock.call_args[0][0]
        self.assertIs(sent["store"],False)
        self.assertNotIn("tools",sent)
        self.assertIn("Tutor UFMS",sent["instructions"])
        self.assertIn("Explique",sent["input"][0]["content"])

    def test_role_separation(self):
        self.assertIn("autorregulação",INSTRUCTIONS["coach"])
        self.assertIn("recuperar",INSTRUCTIONS["tutor"])
        with self.assertRaises(PermissionError):
            self.bridge().answer("admin","algo","admin:7",now=self.now)

    def test_request_replay_suppresses_duplicate_cost(self):
        agent=self.bridge()
        with patch.object(agent,"_request_response",return_value={
            "output":[{"type":"message","content":[{"type":"output_text","text":"ok"}]}]
        }) as call:
            self.assertEqual(agent.answer("coach","Oi","coach:123",now=self.now),"ok")
            self.assertIn("já foi processada",
                          agent.answer("coach","Oi","coach:123",now=self.now))
        self.assertEqual(call.call_count,1)

    def test_global_daily_budget(self):
        agent=self.bridge(max_per_day=1)
        with patch.object(agent,"_request_response",return_value={
            "output":[{"type":"message","content":[{"type":"output_text","text":"ok"}]}]
        }) as call:
            self.assertEqual(agent.answer("tutor","Oi","tutor:1",now=self.now),"ok")
            self.assertIn("Limite diário",
                          agent.answer("coach","Oi","coach:2",now=self.now))
        self.assertEqual(call.call_count,1)

    def test_overlong_message_never_hits_network(self):
        agent=self.bridge()
        with patch.object(agent,"_request_response") as call:
            self.assertIn("2.500",agent.answer("tutor","a"*2600,"tutor:1",now=self.now))
        call.assert_not_called()

    def test_non_response_or_error_does_not_fabricate(self):
        agent=self.bridge()
        self.assertRaises(RuntimeError,agent.extract_text,{"status":"incomplete","output":[]})
        self.assertRaises(RuntimeError,agent.extract_text,{"output":[]})

    def test_unauthorized_telegram_does_not_call_agent(self):
        tg=MockTelegram()
        agent=FakeAgent()
        update={"update_id":10,"message":{
            "from":{"id":999},"chat":{"id":999,"type":"private"},"text":"Bom dia"}}
        handle_update("coach",update,self.store,tg,123,agent=agent,now=self.now)
        self.assertEqual(agent.calls,[])
        self.assertEqual(tg.sent,[])

    def test_authorized_telegram_routes_role_correctly(self):
        tg=MockTelegram()
        agent=FakeAgent()
        update={"update_id":11,"message":{
            "from":{"id":123},"chat":{"id":123,"type":"private"},"text":"Como estudar?"}}
        handle_update("coach",update,self.store,tg,123,agent=agent,now=self.now)
        self.assertEqual(agent.calls,[("coach","Como estudar?","coach:11")])
        self.assertEqual(tg.sent,[(123,"Resposta fictícia")])

    def test_commands_never_become_model_calls(self):
        tg=MockTelegram()
        agent=FakeAgent()
        update={"update_id":12,"message":{
            "from":{"id":123},"chat":{"id":123,"type":"private"},"text":"/nao_existe"}}
        handle_update("tutor",update,self.store,tg,123,agent=agent,now=self.now)
        self.assertEqual(agent.calls,[])
        self.assertIn("comando desconhecido",tg.sent[-1][1])


if __name__=="__main__":
    unittest.main()
