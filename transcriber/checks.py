"""
Each of the tasks contains a checks field, including the validations or verifications that should be done after transcribing.
This functions implements those checks.
"""

def check_ids(items: list[dict], task: dict) -> list[str]:
    """Missing or duplicated IDs, if the task lists expected_ids."""
    expected = [str(x) for x in task["item"].get("expected_ids", [])]
    if not expected:
        return []
    id_field = task["item"]["id_field"]
    found = [str(it[id_field]).strip().lower() for it in items]
    problems = []
    missing = [x for x in expected if x not in found]
    if missing:
        problems.append(f"missing {id_field}: {', '.join(missing)}")
    dupes = sorted({x for x in found if found.count(x) > 1})
    if dupes:
        problems.append(f"duplicate {id_field}: {', '.join(dupes)}")
    return problems


def check_range(items: list[dict], rule: dict, id_field: str) -> list[str]:
    field, allowed = rule["field"], rule.get("allowed_extra", [])
    problems = []
    for it in items:
        value = it[field]
        if value in allowed:
            continue
        if "min" in rule and value < rule["min"] or "max" in rule and value > rule["max"]:
            problems.append(f"({it[id_field]}) {field} = {value} is outside {rule.get('min')}..{rule.get('max')}")
    return problems


def check_total(items: list[dict], rule: dict, id_field: str) -> list[str]:
    field, ignore = rule["field"], rule.get("ignore", [])
    total = sum(it[field] for it in items if it[field] not in ignore)
    if total > rule["max"]:
        return [f"{field} adds up to {total}, more than {rule['max']}"]
    return []


CHECKS = {"range": check_range, "total": check_total}


def run_checks(items: list[dict], task: dict) -> list[str]:
    id_field = task["item"]["id_field"]
    problems = check_ids(items, task)
    for rule in task["checks"]:
        problems += CHECKS[rule["type"]](items, rule, id_field)
    return problems