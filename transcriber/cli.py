import argparse, json, os, sys
from pathlib import Path
from dotenv import load_dotenv

from transcriber.item_model import build_item_model
from transcriber.loaders import LOADERS, load_pages
from transcriber.prompt import SYSTEM_INSTRUCTION, build_prompt
from transcriber.providers import get_provider
from transcriber.task import load_task
from transcriber.checks import run_checks
from transcriber.store import fingerprint, load_result, save_result


def find_documents(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    return sorted(p for p in input_path.iterdir() if p.suffix.lower() in LOADERS)


def main(argv=None) -> int:
    load_dotenv()
    p = argparse.ArgumentParser(description="Transcribe documents with an LLM.")
    p.add_argument("--task", type=Path, required=True, help="task YAML file")
    p.add_argument("--input", type=Path, required=True, help="a file or a folder")
    p.add_argument("--out", type=Path, default=Path("results"))
    p.add_argument("--provider", default="gemini")
    p.add_argument("--model", default=os.getenv("MODEL", "gemini-3.5-flash-lite"))
    p.add_argument("--force", action="store_true", help="redo documents already done")
    args = p.parse_args(argv)

    task = load_task(args.task)
    item_model = build_item_model(task)
    prompt = build_prompt(task)
    schema_text = json.dumps(item_model.model_json_schema(), sort_keys=True)
    provider = get_provider(args.provider, args.model, os.getenv("API_KEY"))

    docs = find_documents(args.input)
    out_dir = args.out / task["name"]
    for i, doc in enumerate(docs, start=1):
        result_path = out_dir / f"{doc.stem}.json"
        fp = fingerprint(doc, SYSTEM_INSTRUCTION, prompt, schema_text, args.model)
        saved = load_result(result_path)
        if not args.force and saved and saved["fingerprint"] == fp:
            items, status = saved["items"], "already done"
        else:
            try:
                pages = load_pages(doc, task)
                items = provider.transcribe(pages, SYSTEM_INSTRUCTION, prompt, item_model)
            except Exception as exc:  # keep the batch going
                print(f"[{i}/{len(docs)}] {doc.name}: FAILED: {exc}", file=sys.stderr)
                continue
            status = "transcribed"

        problems = run_checks(items, task)  # cheap, so run every time (even in reruns)
        save_result(result_path, {"source": doc.name, "model": args.model,
                                  "fingerprint": fp, "items": items, "problems": problems})
        flagged = sum(1 for it in items if it["needs_review"])
        print(f"[{i}/{len(docs)}] {doc.name}: {status}, {len(items)} items, {flagged} flagged")
        for problem in problems:
            print(f"    ! {problem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())