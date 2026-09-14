import json, os, sys, unittest, io, contextlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from symoneural_llm import main as m


class MainTest(unittest.TestCase):
    def test_request_in_process_with_fake_backend(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = m.main(["request", "--fake", "--model", "fake-1", "--prompt", "hello brave new world", "--max-tokens", "8"])
        self.assertEqual(rc, 0)
        out = json.loads(buf.getvalue())
        # the adapter prompts with the documented transcript ([user] ... [assistant]); the fake
        # backend echoes the last words reversed, markers included
        self.assertEqual(out["type"], "message"); self.assertIn("olleh evarb wen dlrow", out["content"][0]["text"])
        self.assertEqual(out["stop_reason"], "end_turn"); self.assertGreaterEqual(out["usage"]["output_tokens"], 4)

    def test_request_model_policy(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = m.main(["request", "--fake", "--allowed-models", "other", "--model", "fake-1", "--prompt", "x"])
        self.assertEqual(rc, 1); self.assertEqual(json.loads(buf.getvalue())["error"]["type"], "invalid_request_error")

    def test_request_unknown_model_is_json_not_traceback(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = m.main(["request", "--fake", "--model", "nope", "--prompt", "x"])
        self.assertEqual(rc, 1); self.assertEqual(json.loads(buf.getvalue())["error"]["type"], "not_found_error")

    def test_capabilities(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(m.main(["capabilities", "--fake"]), 0)
        caps = json.loads(buf.getvalue())
        self.assertEqual(caps["unit"], "chat"); self.assertTrue(caps["streaming"]); self.assertIn("anthropic-messages/2023-06-01", caps["protocols"])

    def test_serve_refuses_without_token(self):
        env = dict(os.environ); os.environ.pop(m.TOKEN_ENV, None)
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = m.main(["serve", "--fake", "--port", "0"])
            self.assertEqual(rc, m.EX_CONFIG); self.assertIn("unconfigured", err.getvalue())
        finally:
            os.environ.clear(); os.environ.update(env)

    def test_no_client_paths_reach_the_backend(self):
        import inspect
        src = inspect.getsource(m)
        # a request body is only ever passed to the adapter; no open() of anything a client sent
        self.assertNotIn("open(req", src); self.assertNotIn("subprocess", src); self.assertNotIn("os.system", src)


if __name__ == "__main__":
    unittest.main()
