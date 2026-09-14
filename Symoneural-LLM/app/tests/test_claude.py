import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from symoneural_llm.backend import FakeBackend
from symoneural_llm.inference import InferenceService
from symoneural_llm.claude import ClaudeAdapter, ProtocolError, build_prompt, parse_output


class ClaudeAdapterTest(unittest.TestCase):
    def setUp(self):
        self.ad = ClaudeAdapter(InferenceService(FakeBackend()))

    def test_text_message(self):
        r = self.ad.messages({"model": "fake-1", "max_tokens": 64, "messages": [{"role": "user", "content": "hello world"}]})
        self.assertEqual(r["type"], "message"); self.assertEqual(r["role"], "assistant")
        self.assertEqual(r["content"][0]["type"], "text"); self.assertEqual(r["stop_reason"], "end_turn")
        self.assertIn("input_tokens", r["usage"])

    def test_validation(self):
        with self.assertRaises(ProtocolError) as cm: self.ad.messages({"max_tokens": 1, "messages": [{"role": "user", "content": "x"}]})
        self.assertEqual(cm.exception.status, 400)
        with self.assertRaises(ProtocolError): self.ad.messages({"model": "fake-1", "messages": [{"role": "user", "content": "x"}]})
        with self.assertRaises(ProtocolError): self.ad.messages({"model": "fake-1", "max_tokens": 1, "messages": [{"role": "system", "content": "x"}]})

    def test_model_restriction(self):
        ad = ClaudeAdapter(InferenceService(FakeBackend()), allowed_models=frozenset({"other"}))
        with self.assertRaises(ProtocolError) as cm: ad.messages({"model": "fake-1", "max_tokens": 1, "messages": [{"role": "user", "content": "x"}]})
        self.assertEqual(cm.exception.status, 403)

    def test_prompt_assembly_with_system_tools_and_tool_result(self):
        p = build_prompt({"system": "be terse", "tools": [{"name": "get_time", "input_schema": {"type": "object"}}], "tool_choice": {"type": "any"},
                          "messages": [{"role": "user", "content": "what time"},
                                       {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "get_time", "input": {}}]},
                                       {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": "12:00"}]}]})
        self.assertIn("[system]\nbe terse", p); self.assertIn('"name": "get_time"', p); self.assertIn('[tool_choice] {"type": "any"}', p)
        self.assertIn("<tool_call>", p); self.assertIn("<tool_result id='t1'>12:00</tool_result>", p); self.assertTrue(p.endswith("[assistant]\n"))

    def test_tool_call_parsing(self):
        blocks = parse_output('Sure. <tool_call>{"name": "get_time", "input": {"tz": "UTC"}}</tool_call>')
        self.assertEqual([b["type"] for b in blocks], ["text", "tool_use"])
        self.assertEqual(blocks[1]["name"], "get_time"); self.assertEqual(blocks[1]["input"], {"tz": "UTC"}); self.assertTrue(blocks[1]["id"].startswith("toolu_"))
        self.assertEqual(parse_output("plain")[0], {"type": "text", "text": "plain"})

    def test_streaming_events(self):
        events = list(self.ad.messages_stream({"model": "fake-1", "max_tokens": 64, "stream": True, "messages": [{"role": "user", "content": "a b"}]}))
        names = [e.split("\n")[0].split(": ")[1] for e in events]
        self.assertEqual(names[:2], ["message_start", "content_block_start"]); self.assertEqual(names[-3:], ["content_block_stop", "message_delta", "message_stop"])
        deltas = [json.loads(e.split("data: ")[1]) for e in events if e.startswith("event: content_block_delta")]
        # streaming and non-streaming must produce the same text for the same request
        req = {"model": "fake-1", "max_tokens": 64, "messages": [{"role": "user", "content": "a b"}]}
        self.assertEqual("".join(d["delta"]["text"] for d in deltas), self.ad.messages(req)["content"][0]["text"])
        self.assertTrue(deltas)


if __name__ == "__main__":
    unittest.main()
