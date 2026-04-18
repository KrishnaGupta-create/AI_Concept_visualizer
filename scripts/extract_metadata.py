"""
extract_metadata.py
-------------------
Extracts and summarizes metadata from concepts.json.
Outputs a Markdown report and a flat metadata CSV.

Usage:
    python scripts/extract_metadata.py
    python scripts/extract_metadata.py --output docs/metadata_report.md
"""

import json
import csv
import argparse
from pathlib import Path
from collections import Counter
from datetime import datetime

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "concepts.json"
CSV_OUT = ROOT / "data" / "concepts_flat.csv"


def load():
    with open(DATA_FILE) as f:
        return json.load(f)


def stats(concepts):
    labels = Counter(c["label"] for c in concepts)
    cats = Counter(c["category"] for c in concepts)
    complexity = Counter(c["metadata"].get("complexity", "unknown") for c in concepts)
    all_tags = [t for c in concepts for t in c.get("tags", [])]
    top_tags = Counter(all_tags).most_common(10)
    return labels, cats, complexity, top_tags


def write_csv(concepts):
    fieldnames = [
        "id", "title", "category", "label", "complexity",
        "tags", "source", "related_concepts", "has_visual"
    ]
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for c in concepts:
            meta = c.get("metadata", {})
            w.writerow({
                "id": c["id"],
                "title": c["title"],
                "category": c["category"],
                "label": c["label"],
                "complexity": meta.get("complexity", ""),
                "tags": "|".join(c.get("tags", [])),
                "source": meta.get("source", ""),
                "related_concepts": "|".join(meta.get("related_concepts", [])),
                "has_visual": "yes" if c.get("visual_file") else "no",
            })
    print(f"CSV written → {CSV_OUT}")


def write_report(concepts, out_path):
    labels, cats, complexity, top_tags = stats(concepts)
    total = len(concepts)
    lines = [
        "# AI Concepts Visual Dataset — Metadata Report",
        f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n",
        "## Summary",
        f"- **Total entries**: {total}",
        f"- **Good design**: {labels.get('good', 0)} ({labels.get('good', 0)/total*100:.0f}%)",
        f"- **Bad design**: {labels.get('bad', 0)} ({labels.get('bad', 0)/total*100:.0f}%)",
        f"- **Pending review**: {labels.get('pending', 0)} ({labels.get('pending', 0)/total*100:.0f}%)",
        "\n## By Category",
    ]
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        lines.append(f"- {cat}: {count}")

    lines += ["\n## By Complexity"]
    for level in ["beginner", "intermediate", "advanced"]:
        lines.append(f"- {level.capitalize()}: {complexity.get(level, 0)}")

    lines += ["\n## Top Tags"]
    for tag, count in top_tags:
        lines.append(f"- `{tag}`: {count}")

    lines += ["\n## Entries Pending Visual", ""]
    pending = [c for c in concepts if not c.get("visual_file")]
    if pending:
        for c in pending:
            lines.append(f"- [{c['id']}] **{c['title']}** — {c['visual_description']}")
    else:
        lines.append("All entries have visual files.")

    lines += ["\n## Bad Design Entries (for review)", ""]
    bad = [c for c in concepts if c["label"] == "bad"]
    for c in bad:
        notes = c.get("metadata", {}).get("annotation_notes", "No notes")
        lines.append(f"- [{c['id']}] **{c['title']}**: {notes}")

    report = "\n".join(lines)

    path = Path(out_path) if out_path else ROOT / "docs" / "metadata_report.md"
    path.parent.mkdir(exist_ok=True)
    with open(path, "w") as f:
        f.write(report)
    print(f"Report written → {path}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Extract metadata from concepts dataset")
    parser.add_argument("--output", help="Path for Markdown report output")
    parser.add_argument("--no-csv", action="store_true", help="Skip CSV export")
    args = parser.parse_args()

    concepts = load()
    print(f"Loaded {len(concepts)} concepts.\n")

    if not args.no_csv:
        write_csv(concepts)

    report = write_report(concepts, args.output)
    print("\n--- Report Preview ---")
    print("\n".join(report.split("\n")[:20]))
    print("...")


if __name__ == "__main__":
    main()
