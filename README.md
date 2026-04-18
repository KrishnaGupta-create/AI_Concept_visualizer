# AI Concepts Visual Dataset

A structured dataset of 24 AI/ML concepts with annotated infographics, designed for LLM training data pipelines.

Each entry includes:
- A concept summary
- A hand-crafted visual explainer description (linked to Canva designs)
- A quality annotation label (`good` / `bad` / `pending`)
- Metadata: complexity, related concepts, source citation

---

## Project Structure

```
ai-concepts-dataset/
├── data/
│   ├── concepts.json          # Master dataset (24 entries)
│   └── concepts_flat.csv      # Auto-generated flat export (run extract_metadata.py)
├── scripts/
│   ├── validate.py            # Schema validation + integrity checks
│   ├── extract_metadata.py    # Metadata report + CSV export
│   └── add_concept.py         # Interactive CLI to add new entries
├── frontend/
│   ├── index.html             # Main app entry point
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── data.js            # Inlined dataset for browser
│       └── app.js             # UI logic
├── docs/
│   └── metadata_report.md     # Auto-generated report (run extract_metadata.py)
└── README.md
```

---

## Dataset Schema

Each entry in `concepts.json` follows this schema:

```json
{
  "id": "001",
  "title": "Attention Mechanism",
  "category": "Architecture",
  "label": "good",
  "summary": "One-sentence plain-language description.",
  "tags": ["transformer", "QKV"],
  "visual_description": "Description of the infographic design.",
  "visual_file": "attention_mechanism.png",
  "metadata": {
    "complexity": "intermediate",
    "related_concepts": ["002", "012"],
    "source": "Vaswani et al. 2017"
  }
}
```

### Field Reference

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✓ | Zero-padded 3-digit string, e.g. `"007"` |
| `title` | string | ✓ | Concept name |
| `category` | string | ✓ | One of: `Foundations`, `Architecture`, `Training`, `Alignment`, `Inference` |
| `label` | string | ✓ | One of: `good`, `bad`, `pending` |
| `summary` | string | ✓ | 20–300 characters |
| `tags` | array | ✓ | At least one tag |
| `visual_description` | string | ✓ | Description of the infographic; prefix with `BAD DESIGN:` or `PENDING:` accordingly |
| `visual_file` | string or null | — | Filename of the Canva export (place in `data/visuals/`) |
| `metadata.complexity` | string | ✓ | One of: `beginner`, `intermediate`, `advanced` |
| `metadata.related_concepts` | array | — | List of related entry IDs |
| `metadata.source` | string | — | Paper or source citation |
| `metadata.annotation_notes` | string | — | Required for `bad` and `pending` labels |

---

## Categories

| Category | Description |
|---|---|
| Foundations | Core mathematical and conceptual building blocks |
| Architecture | Model design patterns and components |
| Training | Learning algorithms and optimization techniques |
| Alignment | Safety, RLHF, and value alignment methods |
| Inference | Decoding strategies and runtime optimizations |

---

## Scripts

### Validate the dataset

Run before every commit to catch schema errors, duplicate IDs, and broken cross-references.

```bash
python scripts/validate.py
```

With auto-fix suggestions:
```bash
python scripts/validate.py --fix
```

### Extract metadata report

Generates `docs/metadata_report.md` and `data/concepts_flat.csv`.

```bash
python scripts/extract_metadata.py
```

Custom output path:
```bash
python scripts/extract_metadata.py --output docs/my_report.md
```

### Add a new concept

Interactive CLI that validates input and auto-assigns the next available ID.

```bash
python scripts/add_concept.py
```

Or pass a JSON string directly:
```bash
python scripts/add_concept.py --json '{"title": "RoPE", "category": "Architecture", ...}'
```

---

## Frontend

Open `frontend/index.html` in any browser — no build step required.

Features:
- Browse all entries in a responsive card grid
- Search by title, summary, or tag
- Filter by category, label, or sort order
- Click any card to view full metadata and visual description
- Relabel entries (good / bad / pending) directly in the UI
- Copy any entry as JSON
- Navigate related concepts

> **Note:** `frontend/js/data.js` is a static copy of the dataset for the browser. After editing `data/concepts.json`, sync it by copying the array into `data.js`, or run the extract script and paste the output.

---

## Adding Visual Files

1. Create your infographic in Canva following the visual description in each entry.
2. Export as PNG and place in `data/visuals/`.
3. Set `"visual_file": "your_file.png"` in `concepts.json`.
4. Run `python scripts/validate.py` to confirm consistency.

---

## Tech Stack

- **Python 3.8+** — dataset scripts (no external dependencies)
- **JSON** — single-source-of-truth dataset
- **Vanilla HTML/CSS/JS** — zero-dependency frontend
- **Canva** — infographic production

---

## Contributing

1. Fork the repo
2. Add or update entries using `python scripts/add_concept.py`
3. Run `python scripts/validate.py` — it must pass with zero errors
4. Run `python scripts/extract_metadata.py` to update docs and CSV
5. Open a pull request

---

## License

MIT
