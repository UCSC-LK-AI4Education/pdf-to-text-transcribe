"""
Later if needed the results can be exported to a CSV file.
"""


import argparse, csv, json, re
from pathlib import Path

from transcriber.task import load_task

SINGLE_FIELD = re.compile(r"^\{(\w+)\}$")
EXCEL_BAD_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def fill(template, values: dict):
    """'{x}' alone keeps x's real type (numbers stay numbers); anything else becomes text."""
    if not isinstance(template, str):
        return template
    match = SINGLE_FIELD.match(template)
    if match:
        return values[match.group(1)]
    return template.format(**values)


def doc_id_for(source: str, table: dict) -> str:
    stem = Path(source).stem
    pattern = table.get("doc_id_regex")
    if pattern:
        match = re.search(pattern, stem)
        if match:
            return match.group(1)
    return stem


def build_rows(results_dir: Path, task: dict) -> list[dict]:
    table = task["table"]
    rows = []
    for path in sorted(results_dir.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        doc_values = {"source": record["source"], "doc_id": doc_id_for(record["source"], table)}
        for item in record["items"]:
            values = {**table.get("constants", {}), **doc_values, **item}
            rows.append({col: fill(tpl, values) for col, tpl in table["columns"].items()})
    return rows


def write_csv(rows: list[dict], path: Path):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_xlsx(rows: list[dict], path: Path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.append(list(rows[0]))
    for cell in ws[1]:
        cell.font = Font(bold=True)
    review_fill = PatternFill("solid", fgColor="F8CBAD")
    for row in rows:
        ws.append([EXCEL_BAD_CHARS.sub("", v) if isinstance(v, str) else v for v in row.values()])
        if row.get("needs_review") is True:
            for cell in ws[ws.max_row]:
                cell.fill = review_fill
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "B2"
    wb.save(path)


WRITERS = {"csv": write_csv, "xlsx": write_xlsx}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Export saved results to tables.")
    p.add_argument("--task", type=Path, required=True)
    p.add_argument("--results", type=Path, required=True, help="folder of result JSON files")
    p.add_argument("--out", type=Path, required=True, help="output path without extension")
    args = p.parse_args(argv)

    task = load_task(args.task)
    if "table" not in task:
        raise SystemExit("This task file has no `table:` section.")
    rows = build_rows(args.results, task)
    if not rows:
        raise SystemExit(f"No results found in {args.results}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    for fmt in task["table"].get("formats", ["csv"]):
        target = args.out.with_suffix("." + fmt)
        WRITERS[fmt](rows, target)
        print(f"{len(rows)} rows -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())