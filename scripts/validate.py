"""
validate.py
-----------
Validates the concepts.json dataset for schema compliance, duplicate detection,
broken references, and annotation completeness. Run before any commit.

Usage:
    python scripts/validate.py
    python scripts/validate.py --fix   # auto-correct fixable issues
"""

import json
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "concepts.json"

REQUIRED_FIELDS = ["id", "title", "category", "label", "summary", "tags", "visual_description", "metadata"]
VALID_CATEGORIES = {"Foundations", "Architecture", "Training", "Alignment", "Inference"}
VALID_LABELS = {"good", "bad", "pending"}
VALID_COMPLEXITIES = {"beginner", "intermediate", "advanced"}

errors = []
warnings = []


def err(msg): errors.append(f"  [ERROR] {msg}")
def warn(msg): warnings.append(f"  [WARN]  {msg}")


def validate(concepts, fix=False):
    ids_seen = set()

    for i, c in enumerate(concepts):
        loc = f"Entry #{i} (id={c.get('id', '?')})"

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in c:
                err(f"{loc}: missing required field '{field}'")

        # ID format and uniqueness
        cid = c.get("id", "")
        if not isinstance(cid, str) or not cid.isdigit() or len(cid) != 3:
            err(f"{loc}: id must be a zero-padded 3-digit string like '007'")
        if cid in ids_seen:
            err(f"{loc}: duplicate id '{cid}'")
        ids_seen.add(cid)

        # Category
        cat = c.get("category", "")
        if cat not in VALID_CATEGORIES:
            err(f"{loc}: invalid category '{cat}'. Must be one of {VALID_CATEGORIES}")

        # Label
        label = c.get("label", "")
        if label not in VALID_LABELS:
            err(f"{loc}: invalid label '{label}'. Must be one of {VALID_LABELS}")

        # Summary length
        summary = c.get("summary", "")
        if len(summary) < 20:
            err(f"{loc}: summary too short ({len(summary)} chars, min 20)")
        if len(summary) > 300:
            warn(f"{loc}: summary is long ({len(summary)} chars, recommended max 300)")

        # Tags
        tags = c.get("tags", [])
        if not isinstance(tags, list) or len(tags) == 0:
            err(f"{loc}: 'tags' must be a non-empty list")

        # Visual description
        vis = c.get("visual_description", "")
        if not vis or len(vis) < 10:
            err(f"{loc}: visual_description is missing or too short")
        if label == "bad" and "BAD DESIGN" not in vis:
            warn(f"{loc}: label is 'bad' but visual_description doesn't start with 'BAD DESIGN:'")
        if label == "pending" and "PENDING" not in vis:
            warn(f"{loc}: label is 'pending' but visual_description doesn't start with 'PENDING:'")

        # Metadata
        meta = c.get("metadata", {})
        if not isinstance(meta, dict):
            err(f"{loc}: 'metadata' must be an object")
        else:
            if meta.get("complexity") not in VALID_COMPLEXITIES:
                err(f"{loc}: metadata.complexity must be one of {VALID_COMPLEXITIES}")
            if not isinstance(meta.get("related_concepts", []), list):
                err(f"{loc}: metadata.related_concepts must be a list")
            if not meta.get("source"):
                warn(f"{loc}: metadata.source is empty")

    # Cross-reference related_concepts
    for c in concepts:
        for ref in c.get("metadata", {}).get("related_concepts", []):
            if ref not in ids_seen:
                err(f"Entry id={c['id']}: related_concept '{ref}' references unknown id")


def main():
    parser = argparse.ArgumentParser(description="Validate AI Concepts Dataset")
    parser.add_argument("--fix", action="store_true", help="Auto-fix fixable issues")
    args = parser.parse_args()

    print(f"Loading {DATA_FILE}...")
    try:
        with open(DATA_FILE) as f:
            concepts = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[FATAL] JSON parse error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"[FATAL] File not found: {DATA_FILE}")
        sys.exit(1)

    print(f"Validating {len(concepts)} entries...\n")
    validate(concepts, fix=args.fix)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(w)
        print()

    if errors:
        print("Errors:")
        for e in errors:
            print(e)
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s). Validation FAILED.")
        sys.exit(1)
    else:
        print(f"✓ Validation passed. {len(concepts)} entries, {len(warnings)} warning(s).")


if __name__ == "__main__":
    main()
