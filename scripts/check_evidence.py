#!/usr/bin/env python3
"""Check a review evidence index against the applicable workflow milestone."""
import argparse
import json
from pathlib import Path

ASTRA_MODEL = "gpt-6.2-astra"
ASTRA_EFFORT = "xhigh"
SOL_MODEL = "gpt-6.2-sol"
SOL_EFFORTS = ("medium", "high", "xhigh", "max")
MAX_ROUNDS = 2


def require(condition, message):
    if not condition:
        raise ValueError(message)


def present(value):
    return isinstance(value, str) and bool(value.strip())


def references(value):
    return isinstance(value, list) and bool(value) and all(map(present, value))


def index_records(records, field, label):
    require(isinstance(records, list), f"{label} must be a list")
    indexed = {}
    for record in records:
        require(isinstance(record, dict) and present(record.get(field)),
                f"Each {label} record needs a nonempty {field}")
        key = record[field]
        require(key not in indexed, f"Duplicate {label} record: {key}")
        indexed[key] = record
    return indexed


def check_agent(agents, agent, model, efforts, label):
    config = agents.get(agent, {})
    require(config.get("effective_model") == model
            and config.get("effective_effort") in efforts
            and references(config.get("configuration_evidence")),
            f"{label} needs effective {model}/{'|'.join(efforts)} and host evidence for {agent}")


def check_astra(record, revision, agents, excluded_agents, label):
    require(isinstance(record, dict), f"Missing {label} record")
    agent = record.get("agent_id")
    require(present(agent) and agent not in excluded_agents,
            f"{label} needs its own agent")
    require(record.get("revision") == revision, f"{label} uses a stale revision")
    check_agent(agents, agent, ASTRA_MODEL, (ASTRA_EFFORT,), label)
    require(references(record.get("evidence")), f"{label} needs a report reference")


def check_review(record, agents):
    baseline = record.get("baseline")
    require(present(baseline), "Missing review baseline")
    reviewers = index_records(record.get("reviews"), "agent_id", "review")
    require(len(reviewers) >= 2, "At least two distinct first-pass reviewers are required")
    for reviewer, report in reviewers.items():
        require(report.get("revision") == baseline and references(report.get("evidence")),
                f"Review by {reviewer} needs a report at the review baseline")
        check_agent(agents, reviewer, SOL_MODEL, SOL_EFFORTS, "First-pass review")

    adjudication = record.get("adjudication")
    check_astra(adjudication, baseline, agents, reviewers, "Astra adjudication")
    covered_reviewers = adjudication.get("reviewer_ids")
    require(references(covered_reviewers) and set(covered_reviewers) == reviewers.keys(),
            "Astra adjudication must reference all first-pass reviews")

    coverage = index_records(record.get("coverage"), "requirement_id", "coverage")
    require(coverage, "Missing requirements coverage")
    incomplete = []
    for requirement, entry in coverage.items():
        require(entry.get("revision") == baseline, f"Stale coverage for {requirement}")
        require(type(entry.get("critical")) is bool, f"Mark criticality for {requirement}")
        status = entry.get("status")
        require(status in ("checked", "unchecked", "blocked", "failed"),
                f"Unknown coverage state for {requirement}")
        if status == "checked":
            require(references(entry.get("evidence")), f"Missing coverage evidence for {requirement}")
        elif entry["critical"]:
            incomplete.append(requirement)

    findings = index_records(record.get("findings"), "id", "finding")
    repairs = {}
    for finding, entry in findings.items():
        disposition = entry.get("disposition")
        require(disposition in ("repair", "optimize", "unverified", "dismissed"),
                f"Unknown Astra disposition for {finding}")
        if disposition == "repair":
            requirements = entry.get("requirement_ids")
            require(references(requirements) and set(requirements) <= coverage.keys(),
                    f"Confirmed finding {finding} needs a known requirement or criterion")
            require(references(entry.get("evidence")), f"Missing evidence for {finding}")
            repairs[finding] = set(requirements)
    return baseline, repairs, sorted(incomplete)


def repair_scope(record, confirmed):
    authorization = record.get("repair_authorization")
    require(isinstance(authorization, dict) and references(authorization.get("evidence")),
            "Missing explicit repair authorization evidence")
    ids = authorization.get("finding_ids")
    require(references(ids) and set(ids) <= confirmed.keys(),
            "Repair authorization must identify Astra-confirmed findings")
    return set(ids)


def check_repair_coverage(findings, confirmed, incomplete):
    for finding in findings:
        gaps = confirmed[finding].intersection(incomplete)
        require(not gaps, f"Repair {finding} has incomplete critical coverage: {', '.join(sorted(gaps))}")


def check_rounds(rounds, baseline, allowed, confirmed, incomplete, agents):
    require(isinstance(rounds, list) and len(rounds) <= MAX_ROUNDS,
            f"At most {MAX_ROUNDS} repair–verification rounds are allowed")
    revision = baseline
    repairers = {}
    focused_reviews = {}
    results = {}
    for number, attempt in enumerate(rounds, 1):
        require(isinstance(attempt, dict)
                and type(attempt.get("number")) is int and attempt["number"] == number,
                "Repair rounds must be numbered consecutively from 1")
        after = attempt.get("after")
        require(attempt.get("before") == revision and present(after),
                f"Round {number} needs before and after revisions in sequence")
        fixes = index_records(attempt.get("fixes"), "finding_id", f"round {number} fix")
        require(fixes and fixes.keys() <= allowed, f"Round {number} fixes must be authorized")
        check_repair_coverage(fixes, confirmed, incomplete)
        for finding, fix in fixes.items():
            fixer_ids = fix.get("agent_ids")
            require(references(fixer_ids) and references(fix.get("evidence")),
                    f"Round {number} fix {finding} needs repairer IDs and evidence")
            for fixer in fixer_ids:
                check_agent(agents, fixer, SOL_MODEL, SOL_EFFORTS, "Repair")
            repairers.setdefault(finding, set()).update(fixer_ids)
            focused = fix.get("focused_review_required")
            require(type(focused) is bool, f"Mark whether {finding} needs focused Astra review")
            focused_reviews[finding] = focused_reviews.get(finding, False) or focused
        checks = index_records(attempt.get("checks"), "finding_id", f"round {number} check")
        require(fixes.keys() <= checks.keys() <= repairers.keys(),
                f"Round {number} needs a result for every fix and may recheck earlier fixes")
        for finding, check in checks.items():
            require(check.get("revision") == after, f"Stale verification for {finding}")
            verifier = check.get("agent_id")
            require(present(verifier) and verifier not in repairers[finding],
                    f"Verification of {finding} needs a different agent from every repairer")
            check_agent(agents, verifier, SOL_MODEL, SOL_EFFORTS, f"Verification of {finding}")
            status = check.get("status")
            require(status in ("passed", "failed", "not_run", "blocked")
                    and references(check.get("evidence")),
                    f"Verification of {finding} needs a check result and evidence or limitation")
            if status == "passed" and focused_reviews[finding]:
                check_astra(check.get("focused_review"), after, agents, repairers[finding],
                            f"Focused Astra review of {finding}")
            results[finding] = check
        revision = after
    return revision, results


def check_evidence(record, phase, revision, planned=()):
    require(isinstance(record, dict) and type(record.get("format")) is int and record["format"] == 1,
            "Expected an evidence index with format 1")
    require(phase in ("review", "repair", "accept") and present(revision),
            "A workflow phase and independently checked revision are required")
    require(phase == "repair" or not planned, "Planned findings apply only to the repair phase")
    agents = index_records(record.get("agents"), "agent_id", "agent registry")
    baseline, confirmed, incomplete = check_review(record, agents)
    rounds = record.get("rounds", [])
    if phase == "review":
        require(revision == baseline, "Project revision differs from the review baseline")
        require(not incomplete, f"Critical coverage is incomplete: {', '.join(incomplete)}")
        return {"rounds_used": 0, "pending_repairs": sorted(confirmed)}

    allowed = repair_scope(record, confirmed)
    latest, results = check_rounds(rounds, baseline, allowed, confirmed, incomplete, agents)
    require(revision == latest, "Project revision differs from the last recorded revision")
    if phase == "repair":
        require(len(rounds) < MAX_ROUNDS, "No repair rounds remain")
        require(planned and set(planned) <= allowed,
                "Specify the planned Astra-confirmed, specifically authorized findings")
        check_repair_coverage(planned, confirmed, incomplete)
        return {"rounds_used": len(rounds), "planned_repairs": sorted(set(planned)),
                "incomplete_critical_coverage": incomplete}

    require(results, "No repair results to accept")
    reused = index_records(record.get("reused_checks", []), "finding_id", "reused check")
    require(reused.keys() <= results.keys(), "Reused checks must refer to recorded verification")
    for finding, result in results.items():
        require(result["status"] == "passed", f"Unresolved verification of {finding}")
        if result["revision"] == revision:
            continue
        scope = reused.get(finding, {})
        require(scope.get("from_revision") == result["revision"] and scope.get("revision") == revision
                and references(scope.get("evidence")),
                f"Verification of {finding} needs a fresh check or bounded reuse at the current revision")
    return {"rounds_used": len(rounds), "accepted_findings": sorted(results),
            "pending_repairs": sorted(confirmed.keys() - results.keys()),
            "incomplete_critical_coverage": incomplete}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--phase", choices=("review", "repair", "accept"), required=True)
    parser.add_argument("--revision", required=True, help="Independently checked project revision")
    parser.add_argument("--finding", action="append", default=[], help="Planned finding for repair; repeat as needed")
    args = parser.parse_args()
    try:
        record = json.loads(args.evidence.read_text(encoding="utf-8"))
        result = check_evidence(record, args.phase, args.revision, args.finding)
    except (OSError, ValueError) as error:
        print(json.dumps({"ready": False, "phase": args.phase, "error": str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ready": True, "phase": args.phase, **result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
