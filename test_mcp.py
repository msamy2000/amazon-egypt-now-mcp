import unittest
import json
import subprocess
from pathlib import Path

SERVER_SCRIPT = Path(__file__).parent / "server.py"

class TestMCPProtocol(unittest.TestCase):
    def setUp(self):
        self.proc = subprocess.Popen(
            ["python3", str(SERVER_SCRIPT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

    def tearDown(self):
        self.proc.terminate()
        self.proc.wait()

    def rpc_call(self, method, params=None, req_id=1):
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line)

    def test_initialize(self):
        res = self.rpc_call("initialize")
        self.assertIn("result", res)
        self.assertEqual(res["result"]["serverInfo"]["name"], "grocery-profile-ctx")

    def test_tools_list(self):
        res = self.rpc_call("tools/list")
        tools = [t["name"] for t in res["result"]["tools"]]
        self.assertIn("lookup_grocery_item", tools)
        self.assertIn("check_substitutions", tools)
        self.assertIn("record_order_event", tools)
        self.assertIn("list_configured_staples", tools)

    def test_lookup_milk(self):
        res = self.rpc_call("tools/call", {
            "name": "lookup_grocery_item",
            "arguments": {"query": "buy 2 bottles of milk"}
        })
        content = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(content["status"], "resolved")
        self.assertEqual(content["primary"]["brand"], "Juhayna")
        self.assertEqual(content["quantity"], 2)

    def test_check_substitutions(self):
        res = self.rpc_call("tools/call", {
            "name": "check_substitutions",
            "arguments": {"category": "milk"}
        })
        content = json.loads(res["result"]["content"][0]["text"])
        self.assertEqual(content["status"], "success")
        self.assertGreaterEqual(len(content["alternates"]), 1)

if __name__ == "__main__":
    unittest.main()
