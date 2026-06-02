# Research Environment Templates for the Catalyst AI Scientist

This repository is used by [Catalyst](https://github.com/imbue-ai/catalyst/) and contains research environment templates for different research areas.

## Binary Blobs & Licensing Guidelines

To keep the repository lightweight and ensure compliance with licensing terms, **binary files (including PDFs) and assets of unclear licensing must not be checked directly into this git repository.**

Instead, please register any such files in the central `BLOBS` registry within the root [`download_blobs.py`](download_blobs.py) script. This allows research agents and contributors to download them dynamically on demand.

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
