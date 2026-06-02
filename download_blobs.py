#!/usr/bin/env python3
"""
download_blobs.py

Downloads binary blobs and templates from external sources.
Specifically used to retrieve large reference materials that are excluded from git.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def find_templates() -> list:
    """
    Scans the repository root for template directories.
    A template is any directory that doesn't start with '.' and is not '__pycache__'.
    """
    templates = []
    try:
        for entry in os.listdir("."):
            if os.path.isdir(entry) and not entry.startswith(".") and entry != "__pycache__":
                templates.append(entry)
    except Exception as e:
        print(f"Error scanning directory for templates: {e}", file=sys.stderr)
    return sorted(templates)


def load_blobs() -> dict:
    """
    Loads blob configurations dynamically from each template's blobs.json file.
    If a template does not contain a blobs.json file, it is treated as empty.
    """
    blobs = {}
    for template in find_templates():
        json_path = os.path.join(template, "blobs.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    blobs[template] = json.load(f)
            except Exception as e:
                print(f"Error parsing JSON file {json_path}: {e}", file=sys.stderr)
                blobs[template] = {}
        else:
            blobs[template] = {}
    return blobs


def download_file(url: str, target_path: str) -> bool:
    """
    Downloads a file from a URL to target_path atomically.
    Ensures directories are created, and cleans up temporary files on failure.
    """
    # Ensure parent directories exist
    target_dir = os.path.dirname(target_path)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)

    # Check if target already exists
    if os.path.exists(target_path):
        print(f"File already exists: {target_path} (skipping)")
        return True

    print(f"Downloading {url} -> {target_path}...")
    tmp_path = target_path + ".tmp"
    try:
        with urllib.request.urlopen(url) as response:
            with open(tmp_path, "wb") as f:
                # Read in chunks of 64KB for memory efficiency and robustness
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        
        # Atomically rename the temp file to the final destination
        os.replace(tmp_path, target_path)
        print(f"Successfully downloaded: {target_path}")
        return True

    except Exception as e:
        print(f"Error downloading {url} to {target_path}: {e}", file=sys.stderr)
        # Clean up temporary file if it was created
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return False


def main():
    # Load blobs dynamically from templates
    blobs = load_blobs()

    parser = argparse.ArgumentParser(
        description="Download binary reference blobs for the catalyst templates."
    )
    parser.add_argument(
        "template",
        nargs="?",
        choices=list(blobs.keys()),
        help="Specific template name to process blobs for (options: %(choices)s). If omitted, processes blobs for all templates.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete previously downloaded blobs instead of downloading them.",
    )
    
    args = parser.parse_args()

    # Determine which templates to process
    if args.template:
        templates_to_process = [args.template]
    else:
        # Filter out templates that have no blobs configured
        templates_to_process = [t for t, files in blobs.items() if files]

    success = True
    if args.clean:
        for template in templates_to_process:
            if not blobs[template]:
                continue
            print(f"Cleaning blobs for template: {template}")
            for target, _ in blobs[template].items():
                normalized_target = os.path.normpath(os.path.join(template, target))
                if os.path.exists(normalized_target):
                    try:
                        os.remove(normalized_target)
                        print(f"Deleted: {normalized_target}")
                    except Exception as e:
                        print(f"Error deleting {normalized_target}: {e}", file=sys.stderr)
                        success = False
                else:
                    print(f"Already clean: {normalized_target}")
    else:
        for template in templates_to_process:
            if not blobs[template]:
                continue
            print(f"Processing template: {template}")
            for target, url in blobs[template].items():
                # Standardize path formatting for current OS, prepending template directory
                normalized_target = os.path.normpath(os.path.join(template, target))
                if not download_file(url, normalized_target):
                    success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
