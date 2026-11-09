# pdf-to-text-transcribe

Transcribe scanned documents (handwritten or printed) into structured JSON using an LLM.
You describe each job in a YAML **task file**: what the document is, which fields to extract,
any special rules, checks, and an optional table layout. The code itself knows nothing
about any particular document.

## Setup

```
pip install -r requirements.txt
```

`pdf2image` also needs **poppler**:
- Ubuntu/Debian: `sudo apt install poppler-utils`
- macOS: `brew install poppler`
- Windows: download poppler and add its `bin` folder to `PATH`

Create a `.env` file in the project folder:

```
API_KEY=your-gemini-api-key
MODEL=gemini-3.5-flash-lite
```

## Usage

Transcribe one file first to check the output:

```
python -m transcriber.cli --task tasks/is021_q1.yaml --input exam_pdfs/paper_001.pdf
```

Then a whole folder:

```
python -m transcriber.cli --task tasks/is021_q1.yaml --input exam_pdfs
```

Each document gets one result file at `results/<task name>/<file name>.json`, holding the
extracted items and any problems the checks found.

Re-running skips documents that are already done. A document is redone automatically if the
file, the prompt, the fields, the page range or the model changed. Use `--force` to redo everything.

Optional flags: `--out` (results folder), `--provider` (default `gemini`), `--model`.

### Export to a table (optional)

If the task file has a `table:` section:

```
python -m transcriber.export --task tasks/is021_q1.yaml --results results/is021_q1 --out data/dataset
```

This writes `data/dataset.csv` and/or `data/dataset.xlsx`. No LLM calls are made, so you can
re-export as often as you like.

## Writing a task file

See `tasks/is021_q1.yaml` for a full example.

| Key | Required | What it does |
|---|---|---|
| `name` | yes | Name of the job; also the results subfolder |
| `document` | yes | Plain description of the document, sent to the model |
| `item` | yes | `label` (what one returned object is), `id_field`, optional `expected_ids` |
| `fields` | yes | List of `name`, `type` (`str`, `float`, `int`, `bool`), `description` |
| `input` | no | `pages` (e.g. `"1-5"`, default all) and `dpi` (default 200) |
| `task_rules` | no | Extra instructions for this job only, added to the prompt |
| `checks` | no | `range` and `total` rules run on every result |
| `table` | no | `formats`, `constants`, `doc_id_regex`, and `columns` for export |

Every item also gets `needs_review` and `review_note` automatically.

General transcription rules (copy exactly, keep crossings-out, `[illegible]`, LaTeX for math,
`[DIAGRAM: ...]` for drawings) are built in, in `transcriber/prompt.py`.

### Table columns

- Fixed text: `question_type: independent`
- One value, keeping its type: `awarded_mark: "{awarded_mark}"`
- Mixed text: `response_id: "{doc_id}_{exam_id}_{sub_q}"`

You can use item fields, `constants`, `doc_id` (from `doc_id_regex`, or the file name) and `source`.

## Extending

- **New file type:** write a function in `transcriber/loaders.py` that returns a list of page
  images and add it to `LOADERS`.
- **New LLM provider:** add a class in `transcriber/providers/` with a
  `transcribe(pages, system, prompt, item_model) -> list[dict]` method, and add it to
  `get_provider` in `transcriber/providers/__init__.py`.
- **New check:** write a function in `transcriber/checks.py` and add it to `CHECKS`.

## Notes

- Results are machine transcriptions. Review the items with `needs_review = true` and any
  reported problems before using the data.
- Only Gemini is supported for now.