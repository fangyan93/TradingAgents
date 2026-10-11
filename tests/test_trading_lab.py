import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from trading_lab.codex_runner import CodexRunError, _parse_json, run_role
from trading_lab.data_packet import MarketDataUnavailableError, _discard_malformed_cache, _instrument_snapshot
from trading_lab.prompts import analyst_prompt, reviewer_prompt, risk_judge_prompt
from trading_lab.run_research import _load_or_run


class TradingLabTests(unittest.TestCase):
    def test_parse_json_accepts_a_markdown_fence(self):
        self.assertEqual(_parse_json("```json\n{\"status\": \"ok\"}\n```"), {"status": "ok"})

    def test_parse_json_rejects_non_json(self):
        with self.assertRaises(CodexRunError):
            _parse_json("not json")

    def test_role_prompts_remain_research_only(self):
        packet = {"as_of": "2026-09-11", "instruments": []}
        analyst = analyst_prompt(packet)
        reviewer = reviewer_prompt(packet, {"summary": "test"})
        judge = risk_judge_prompt(packet, {"summary": "test"}, {"bull_case": []})
        for prompt in (analyst, reviewer, judge):
            self.assertIn("Do not give personalized investment advice", prompt)
            self.assertIn("Do not use tools", prompt)

    def test_invalid_upstream_cache_is_removed_but_valid_cache_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            invalid = directory / "QQQ-YFin-data-invalid.csv"
            valid = directory / "QQQ-YFin-data-valid.csv"
            invalid.write_text("index,Close\n", encoding="utf-8")
            valid.write_text("Date,Close\n2026-09-11,100\n", encoding="utf-8")

            _discard_malformed_cache("QQQ", directory)

            self.assertFalse(invalid.exists())
            self.assertTrue(valid.exists())

    @patch("trading_lab.data_packet.load_ohlcv", side_effect=KeyError("Date"))
    def test_market_data_failure_has_a_clear_recovery_message(self, _mock_load):
        with self.assertRaisesRegex(MarketDataUnavailableError, "Check the network connection and retry"):
            _instrument_snapshot("QQQ", "2026-10-09")

    @patch("trading_lab.codex_runner.subprocess.run")
    def test_runner_forces_read_only_codex_and_removes_api_key(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            schema = directory / "role.json"
            schema.write_text("{}", encoding="utf-8")
            (directory / "role.response.json").write_text(json.dumps({"status": "ok"}), encoding="utf-8")
            result = run_role(prompt="test", schema_path=schema, workdir=directory)

        self.assertEqual(result.payload, {"status": "ok"})
        command = mock_run.call_args.kwargs["args"] if "args" in mock_run.call_args.kwargs else mock_run.call_args.args[0]
        environment = mock_run.call_args.kwargs["env"]
        self.assertIn("--ephemeral", command)
        self.assertIn("read-only", command)
        self.assertNotIn("OPENAI_API_KEY", environment)
        self.assertNotIn("CODEX_API_KEY", environment)

    def test_resume_reuses_existing_role_report(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            report = directory / "analyst.json"
            report.write_text(json.dumps({"summary": "existing"}), encoding="utf-8")
            with patch("trading_lab.run_research.run_role") as mocked:
                result = _load_or_run(
                    report_path=report,
                    prompt="unused",
                    schema_path=directory / "schema.json",
                    run_dir=directory,
                )
            self.assertEqual(result, {"summary": "existing"})
            mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
