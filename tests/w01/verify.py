import json
from artifact import total

checks = [
    ("zero", 0, "return", 0),
    ("one", 1, "return", 10),
    ("positive", 7, "return", 70),
    ("large_integer", 10**30, "return", 10**31),
    ("negative", -1, "ValueError", None),
    ("true", True, "ValueError", None),
    ("false", False, "ValueError", None),
    ("integral_float", 1.0, "ValueError", None),
    ("zero_float", 0.0, "ValueError", None),
    ("string", "1", "ValueError", None),
    ("none", None, "ValueError", None),
    ("list", [], "ValueError", None),
]
results=[]
for name, value, expected_kind, expected_value in checks:
    try:
        actual = total(value)
        kind = "return"
    except Exception as exc:
        kind = type(exc).__name__
        actual = str(exc)
    passed = kind == expected_kind and (kind != "return" or actual == expected_value)
    results.append({"name": name, "input_repr": repr(value), "expected_kind": expected_kind, "expected_value": expected_value, "actual_kind": kind, "actual_value": actual, "passed": passed})
print(json.dumps({"checks":results,"passed":sum(r["passed"] for r in results),"total":len(results)},ensure_ascii=False,indent=2))
raise SystemExit(0 if all(r["passed"] for r in results) else 1)
