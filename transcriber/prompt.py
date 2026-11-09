"""
Build the prompt using the config settings for the given task plus add system instructions
"""

SYSTEM_INSTRUCTION = (
    "You are a meticulous transcription assistant. You transcribe handwritten "
    "and printed text exactly as written. You never correct, complete, or improve "
    "the writer's work. You output only the requested structured data."
)

GENERAL_RULES = """\
## General transcription rules
- Copy text EXACTLY as written. Do not fix spelling, grammar, terms, numbers or reasoning.
- Do not complete unfinished sentences or fill in missing steps.
- Crossed-out text: keep it as ~~struck text~~ (e.g. "~~False~~ True").
- Unreadable words: write [illegible]. Never guess.
- Math: write it as LaTeX between single dollar signs, keeping the writer's own numbers.
- Drawings: do not describe them in prose. Write them as [DIAGRAM: A -> D, B -> E].
  Use LaTeX for describing complex diagrams.
  If a drawing cannot be written that way, write [DIAGRAM: unclear].
- Content may continue across a page break. Join it into one item.
- Set needs_review = true with a short review_note whenever you are unsure of anything.
  Over-flagging is cheap; missing a bad item is not."""


def build_prompt(task: dict) -> str:
    item = task["item"]
    parts = [
        "## The document\n" + task["document"].strip(),
        f"## What to return\nReturn one object per {item['label']} you can find, in order.",
    ]
    if item.get("expected_ids"):
        ids = ", ".join(str(x) for x in item["expected_ids"])
        parts.append(f"Expected values of {item['id_field']}: {ids}.")
    parts.append(GENERAL_RULES)
    if task["task_rules"]:
        parts.append(task["task_rules"].strip())
    return "\n\n".join(parts)