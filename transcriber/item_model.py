"""
Build the pydantic models necessary for configurations at runtime using the tasks/<task-config-file-name>.yml
"""

from pydantic import Field, create_model

TYPE_NAMES = {"str": str, "float": float, "int": int, "bool": bool}

ALWAYS_INCLUDED = {
    "needs_review": (bool, Field(description="True if anything was uncertain.")),
    "review_note": (str, Field(description="Short reason when needs_review is true, else empty.")),
}

def build_item_model(task: dict):
    fields = {
        f["name"]: (TYPE_NAMES[f["type"]], Field(description=f["description"]))
        for f in task["fields"]
    }
    fields.update(ALWAYS_INCLUDED)
    return create_model("TranscribedItem", **fields)