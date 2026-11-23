"""Evidence workflow checks with synthetic records, without contacting any model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_evidence.py"
sys.path.insert(0, str(SCRIPT.parent))
from check_evidence import check_evidence


def astra(agent, revision):
    return {"agent_id": agent, "revision": revision, "evidence": ["reports/astra.md"]}


def agent_config(agent, model="gpt-6.2-sol", effort="high"):
    return {"agent_id": agent, "effective_model": model, "effective_effort": effort,
            "configuration_evidence": [f"host-event:{agent}"]}


def repair_round(number, finding, before, after, *, status="passed"):
    return {"number": number, "before": before, "after": after, "fixes": [
        {"finding_id": finding, "agent_ids": ["fixer"], "evidence": ["changes.md"],
         "focused_review_required": False},
    ], "checks": [
        {"finding_id": finding, "agent_id": "verifier", "revision": after,
         "status": status, "evidence": ["checks.md"]},
    ]}


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.record = {
            "format": 1,
            "baseline": "base",
            "agents": [agent_config(agent) for agent in
                       ("review_a", "review_b", "fixer", "first-fixer", "verifier")]
                      + [agent_config("astra", "gpt-6.2-astra", "xhigh")],
            "reviews": [
                {"agent_id": agent, "revision": "base", "evidence": [f"reports/{agent}.md"]}
                for agent in ("review_a", "review_b")
            ],
            "coverage": [
                {"requirement_id": "R1", "revision": "base", "critical": True,
                 "status": "checked", "evidence": ["reports/review_a.md"]},
            ],
            "adjudication": {**astra("astra", "base"), "reviewer_ids": ["review_a", "review_b"]},
            "findings": [
                {"id": finding, "disposition": "repair", "requirement_ids": ["R1"],
                 "evidence": ["reports/astra.md"]}
                for finding in ("F1", "F2")
            ],
            "repair_authorization": {"evidence": ["user-turn:12"], "finding_ids": ["F1"]},
            "rounds": [],
        }

    def test_review_only_keeps_pending_findings_without_repair_permission(self):
        del self.record["repair_authorization"]
        result = check_evidence(self.record, "review", "base")
        self.assertEqual(result["pending_repairs"], ["F1", "F2"])

    def test_critical_gap_blocks_complete_review_but_does_not_block_scoped_fix(self):
        self.record["coverage"].append(
            {"requirement_id": "R2", "revision": "base", "critical": True, "status": "blocked"}
        )
        with self.assertRaisesRegex(ValueError, "Critical coverage"):
            check_evidence(self.record, "review", "base")
        repair = check_evidence(self.record, "repair", "base", ["F1"])
        self.assertEqual(repair["incomplete_critical_coverage"], ["R2"])
        self.record["findings"][0]["requirement_ids"].append("R2")
        with self.assertRaisesRegex(ValueError, "Repair F1 has incomplete critical coverage: R2"):
            check_evidence(self.record, "repair", "base", ["F1"])
        self.record["rounds"] = [repair_round(1, "F1", "base", "fix-v1")]
        with self.assertRaisesRegex(ValueError, "Repair F1 has incomplete critical coverage: R2"):
            check_evidence(self.record, "accept", "fix-v1")

    def test_wrong_model_or_missing_effective_evidence_blocks_adjudication(self):
        adjudication = next(agent for agent in self.record["agents"] if agent["agent_id"] == "astra")
        for field, value in (("effective_model", "gpt-6-astra"), ("effective_effort", "max"),
                             ("configuration_evidence", [])):
            with self.subTest(field=field):
                original = adjudication[field]
                adjudication[field] = value
                with self.assertRaisesRegex(ValueError, "needs effective"):
                    check_evidence(self.record, "review", "base")
                adjudication[field] = original

    def test_adjudication_is_separate_and_covers_all_first_pass_reviewers(self):
        adjudication = self.record["adjudication"]
        adjudication["agent_id"] = "review_a"
        with self.assertRaisesRegex(ValueError, "needs its own agent"):
            check_evidence(self.record, "review", "base")
        adjudication["agent_id"] = "astra"
        adjudication["reviewer_ids"] = ["review_a"]
        with self.assertRaisesRegex(ValueError, "reference all"):
            check_evidence(self.record, "review", "base")
        self.record["reviews"][1]["agent_id"] = "review_a"
        with self.assertRaisesRegex(ValueError, "Duplicate review"):
            check_evidence(self.record, "review", "base")

    def test_sol_roles_require_supported_configurations_with_evidence(self):
        review_agent = self.record["agents"][0]
        review_agent["effective_model"] = "gpt-6.1-sol"
        with self.assertRaisesRegex(ValueError, "First-pass review needs effective gpt-6.2-sol"):
            check_evidence(self.record, "review", "base")
        review_agent["effective_model"] = "gpt-6.2-sol"
        self.record["rounds"] = [repair_round(1, "F1", "base", "fix-v1")]
        fixer = next(agent for agent in self.record["agents"] if agent["agent_id"] == "fixer")
        fixer["configuration_evidence"] = []
        with self.assertRaisesRegex(ValueError, "Repair needs effective gpt-6.2-sol"):
            check_evidence(self.record, "accept", "fix-v1")
        fixer["configuration_evidence"] = ["host-event:fixer"]
        verifier = next(agent for agent in self.record["agents"] if agent["agent_id"] == "verifier")
        verifier["effective_effort"] = "low"
        with self.assertRaisesRegex(ValueError, "Verification of F1 needs effective gpt-6.2-sol"):
            check_evidence(self.record, "accept", "fix-v1")
        verifier["effective_effort"] = "max"
        self.assertEqual(check_evidence(self.record, "accept", "fix-v1")["accepted_findings"], ["F1"])

    def test_current_revision_and_repair_authority_are_checked(self):
        with self.assertRaisesRegex(ValueError, "differs from the review baseline"):
            check_evidence(self.record, "review", "user-edited")
        with self.assertRaisesRegex(ValueError, "specifically authorized"):
            check_evidence(self.record, "repair", "base", ["F2"])
        del self.record["repair_authorization"]
        with self.assertRaisesRegex(ValueError, "explicit repair authorization"):
            check_evidence(self.record, "repair", "base", ["F1"])

    def test_failed_first_round_leaves_exactly_one_retry_and_is_not_accepted(self):
        first = repair_round(1, "F1", "base", "fix-v1", status="failed")
        second = repair_round(2, "F1", "fix-v1", "fix-v2")
        self.record["rounds"] = [first]
        with self.assertRaisesRegex(ValueError, "Unresolved verification"):
            check_evidence(self.record, "accept", "fix-v1")
        self.assertEqual(check_evidence(self.record, "repair", "fix-v1", ["F1"])["rounds_used"], 1)
        self.record["rounds"].append(second)
        accepted = check_evidence(self.record, "accept", "fix-v2")
        self.assertEqual(accepted["accepted_findings"], ["F1"])
        self.assertEqual(accepted["pending_repairs"], ["F2"])
        with self.assertRaisesRegex(ValueError, "No repair rounds remain"):
            check_evidence(self.record, "repair", "fix-v2", ["F1"])

    def test_verifier_must_differ_from_all_repairers_for_the_finding(self):
        first = repair_round(1, "F1", "base", "fix-v1", status="failed")
        second = repair_round(2, "F1", "fix-v1", "fix-v2")
        first["fixes"][0]["agent_ids"] = ["first-fixer"]
        second["checks"][0]["agent_id"] = "first-fixer"
        self.record["rounds"] = [first, second]
        with self.assertRaisesRegex(ValueError, "different agent from every repairer"):
            check_evidence(self.record, "accept", "fix-v2")

    def test_focused_review_requires_exact_model_and_current_revision(self):
        attempt = repair_round(1, "F1", "base", "fix-v1")
        attempt["fixes"][0]["focused_review_required"] = True
        self.record["rounds"] = [attempt]
        with self.assertRaisesRegex(ValueError, "Missing Focused Astra"):
            check_evidence(self.record, "accept", "fix-v1")
        attempt["checks"][0]["focused_review"] = astra("astra", "base")
        with self.assertRaisesRegex(ValueError, "stale revision"):
            check_evidence(self.record, "accept", "fix-v1")
        attempt["checks"][0]["focused_review"]["revision"] = "fix-v1"
        self.assertEqual(check_evidence(self.record, "accept", "fix-v1")["accepted_findings"], ["F1"])

    def test_ordinary_verifier_cannot_reuse_its_id_as_focused_astra(self):
        attempt = repair_round(1, "F1", "base", "fix-v1")
        attempt["fixes"][0]["focused_review_required"] = True
        attempt["checks"][0]["focused_review"] = astra("verifier", "fix-v1")
        self.record["rounds"] = [attempt]
        with self.assertRaisesRegex(ValueError, "Focused Astra review of F1 needs effective gpt-6.2-astra/xhigh"):
            check_evidence(self.record, "accept", "fix-v1")
        self.record["agents"].append(agent_config("verifier", "gpt-6.2-astra", "xhigh"))
        with self.assertRaisesRegex(ValueError, "Duplicate agent registry record: verifier"):
            check_evidence(self.record, "accept", "fix-v1")

    def test_earlier_pass_needs_evidence_of_applicability_to_current_revision(self):
        self.record["repair_authorization"]["finding_ids"].append("F2")
        self.record["rounds"] = [repair_round(1, "F1", "base", "fix-v1"),
                                 repair_round(2, "F2", "fix-v1", "fix-v2")]
        with self.assertRaisesRegex(ValueError, "fresh check or bounded reuse"):
            check_evidence(self.record, "accept", "fix-v2")
        self.record["reused_checks"] = [
            {"finding_id": "F1", "from_revision": "fix-v1", "revision": "fix-v2",
             "evidence": ["verification-impact.md"]},
        ]
        self.assertEqual(check_evidence(self.record, "accept", "fix-v2")["accepted_findings"], ["F1", "F2"])
        with self.assertRaisesRegex(ValueError, "differs from the last recorded revision"):
            check_evidence(self.record, "accept", "user-edited")

    def test_current_round_may_independently_recheck_an_earlier_fix(self):
        self.record["repair_authorization"]["finding_ids"].append("F2")
        first = repair_round(1, "F1", "base", "fix-v1")
        second = repair_round(2, "F2", "fix-v1", "fix-v2")
        recheck = {**first["checks"][0], "revision": "fix-v2", "evidence": ["fresh-F1.md"]}
        second["checks"].append(recheck)
        self.record["rounds"] = [first, second]
        result = check_evidence(self.record, "accept", "fix-v2")
        self.assertEqual(result["accepted_findings"], ["F1", "F2"])
        recheck["agent_id"] = "fixer"
        with self.assertRaisesRegex(ValueError, "different agent from every repairer"):
            check_evidence(self.record, "accept", "fix-v2")

    def test_cli_reports_bad_json_and_does_not_change_input(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "index.json"
            path.write_text("{bad json", encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path), "--phase",
                                     "review", "--revision", "base"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["ready"])
            self.assertEqual(path.read_text(encoding="utf-8"), "{bad json")


if __name__ == "__main__":
    unittest.main()
