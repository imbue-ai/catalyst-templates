# Research Environment Templates for the Catalyst AI Scientist

This repository is used by [Catalyst](https://github.com/imbue-ai/catalyst/) and contains research environment templates for different research areas.

## Binary Blobs & Licensing Guidelines

To keep the repository lightweight and ensure compliance with licensing terms, **binary files (including PDFs) and assets of unclear licensing must not be checked directly into this git repository.**

### The `blobs.json` Convention

Each template folder remains self-contained. To configure binary reference assets for a template, create a `blobs.json` file inside that template's folder (e.g., `bifurcation/blobs.json`).

The `blobs.json` file must contain a flat JSON key-value mapping from the target filename (relative to the template directory) to its source URL:
```json
{
  "there_will_be_a_scientific_theory_of_deep_learning.pdf": "https://arxiv.org/pdf/2604.21691"
}
```

The root [`download_blobs.py`](download_blobs.py) script dynamically scans the repository for templates, parses these `blobs.json` configuration files, and downloads or manages the assets.

### Usage

To download the binary assets for all templates:
```bash
python3 download_blobs.py
```

To download assets for a specific template (e.g., `bifurcation`):
```bash
python3 download_blobs.py bifurcation
```

To clean up and delete all downloaded binary assets:
```bash
python3 download_blobs.py --clean
```
