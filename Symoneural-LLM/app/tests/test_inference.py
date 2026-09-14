import sys, threading, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from symoneural_llm.backend import FakeBackend, GenerateParams, Cancelled
from symoneural_llm.inference import InferenceService


class InferenceTest(unittest.TestCase):
    def setUp(self):
        self.b = FakeBackend(); self.svc = InferenceService(self.b)

    def test_capabilities_and_models(self):
        c = self.svc.capabilities()
        self.assertEqual(c["models"][0]["model_id"], "fake-1"); self.assertTrue(c["streaming"] and c["cancellation"])
        with self.assertRaises(KeyError): self.svc.model("nope")

    def test_session_generate_and_accounting(self):
        s = self.svc.open_session("fake-1")
        self.assertIn("load:fake-1", self.b.calls)
        c = self.svc.generate(s.session_id, "hello brave new world")
        self.assertEqual(c.text, "olleh evarb wen dlrow"); self.assertEqual(c.stop_reason, "end_turn")
        self.assertEqual((c.input_tokens, c.output_tokens), (4, 4))
        self.svc.close_session(s.session_id)
        with self.assertRaises(KeyError): self.svc.session(s.session_id)

    def test_max_tokens_and_stop(self):
        s = self.svc.open_session("fake-1")
        c = self.svc.generate(s.session_id, "a b c d e", GenerateParams(max_tokens=2))
        self.assertEqual((c.text, c.stop_reason), ("a b", "max_tokens"))
        c = self.svc.generate(s.session_id, "a b c d e", GenerateParams(stop=(" d",)))
        self.assertEqual((c.text, c.stop_reason), ("a b c", "stop_sequence"))

    def test_cancel(self):
        s = self.svc.open_session("fake-1")
        got = []
        it = self.svc.stream(s.session_id, "one two three four five")
        got.append(next(it)); self.svc.cancel(s.session_id)
        with self.assertRaises(Cancelled): list(it)
        self.assertEqual(got, ["eno"])

    def test_no_filesystem_paths_in_api(self):
        import inspect; src = inspect.getsource(sys.modules["symoneural_llm.inference"])
        self.assertNotIn("open(", src); self.assertNotIn("os.path", src)


if __name__ == "__main__":
    unittest.main()
