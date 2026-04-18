"""
add_concept.py
--------------
Interactive CLI to add a new concept entry to concepts.json.
Validates input before writing and auto-assigns the next available ID.

Usage:
    python scripts/add_concept.py
    python scripts/add_concept.py --json '{"title": "...", ...}'
"""

import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "concepts.json"

VALID_CATEGORIES = ["Foundations", "Architecture", "Training", "Alignment", "Inference"]
VALID_LABELS = ["good", "bad", "pending"]
VALID_COMPLEXITIES = ["beginner", "intermediate", "advanced"]


def load():
    with open(DATA_FILE) as f:
        return json.load(f)


def save(concepts):
    with open(DATA_FILE, "w") as f:
        json.dump(concepts, f, indent=2)
    print(f"Saved {len(concepts)} entries to {DATA_FILE}")


def next_id(concepts):
    ids = [int(c["id"]) for c in concepts if c.get("id", "").isdigit()]
    return str(max(ids) + 1).zfill(3) if ids else "001"


def prompt(label, options=None, required=True):
    while True:
        if options:
            display = f"{label} [{'/'.join(options)}]: "
        else:
            display = f"{label}: "
        val = input(display).strip()
        if not val and not required:
            return None
        if not val and required:
            print("  This field is required.")
            continue
        if options and val not in options:
            print(f"  Must be one of: {options}")
            continue
        return val


def interactive_add(concepts):
    print("\nAdd a new concept entry\n" + "-" * 30)
    new_id = next_id(concepts)
    print(f"Auto-assigned ID: {new_id}\n")

    title = prompt("Title")
    category = prompt("Category", VALID_CATEGORIES)
    label = prompt("Label", VALID_LABELS)
    summary = prompt("Summary (one sentence, 20–300 chars)")
    tags_raw = prompt("Tags (comma-separated)")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    visual_description = prompt("Visual description")
    complexity = prompt("Complexity", VALID_COMPLEXITIES)
    source = prompt("Source / paper citation", required=False) or ""
    related_raw = prompt("Related concept IDs (comma-separated, e.g. 001,003)", required=False) or ""
    related = [r.strip().zfill(3) for r in related_raw.split(",") if r.strip()]

    annotation_notes = None
    if label in ("bad", "pending"):
        annotation_notes = prompt("Annotation notes (reason for bad/pending label)", required=False)

    entry = {
        "id": new_id,
        "title": title,
        "category": category,
        "label": label,
        "summary": summary,
        "tags": tags,
        "visual_description": visual_description,
        "visual_file": None,
        "metadata": {
            "complexity": complexity,
            "related_concepts": related,
            "source": source,
        }
    }
    if annotation_notes:
        entry["metadata"]["annotation_notes"] = annotation_notes

    print("\nEntry preview:")
    print(json.dumps(entry, indent=2))
    confirm = input("\nAdd this entry? [y/N]: ").strip().lower()
    if confirm == "y":
        concepts.append(entry)
        save(concepts)
        print(f"✓ Entry '{title}' added with ID {new_id}.")
    else:
        print("Aborted.")


def json_add(concepts, raw):
    try:
        entry = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        sys.exit(1)

    entry["id"] = next_id(concepts)
    concepts.append(entry)
    save(concepts)
    print(f"✓ Entry added with ID {entry['id']}.")


def main():
    parser = argparse.ArgumentParser(description="Add a new concept to the dataset")
    parser.add_argument("--json", help="JSON string for the new entry (skips interactive mode)")
    args = parser.parse_args()

    concepts = load()

    if args.json:
        json_add(concepts, args.json)
    else:
        interactive_add(concepts)


if __name__ == "__main__":
    main()
