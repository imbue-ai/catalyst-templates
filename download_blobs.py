#!/usr/bin/env python3
"""
download_blobs.py

Downloads binary blobs and templates from external sources.
Specifically used to retrieve large reference materials that are excluded from git.
"""

import argparse
import os
import sys
import urllib.request
import urllib.error

# Map of template names to their associated binary files (target path relative to template folder -> source URL)
BLOBS = {
    "learning_mechanics": {
        "there_will_be_a_scientific_theory_of_deep_learning.pdf": "https://arxiv.org/pdf/2604.21691",
    },
    "bifurcation": {
        "there_will_be_a_scientific_theory_of_deep_learning.pdf": "https://arxiv.org/pdf/2604.21691",
    }
}


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
        # Some CDNs or websites block default Python user-agents (e.g. 403 Forbidden).
        # We specify a standard browser user-agent to ensure robust downloads.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
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
    parser = argparse.ArgumentParser(
        description="Download binary reference blobs for the catalyst templates."
    )
    parser.add_argument(
        "template",
        nargs="?",
        choices=list(BLOBS.keys()),
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
        templates_to_process = list(BLOBS.keys())

    success = True
    if args.clean:
        for template in templates_to_process:
            print(f"Cleaning blobs for template: {template}")
            for target, _ in BLOBS[template].items():
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
            print(f"Processing template: {template}")
            for target, url in BLOBS[template].items():
                # Standardize path formatting for current OS, prepending template directory
                normalized_target = os.path.normpath(os.path.join(template, target))
                if not download_file(url, normalized_target):
                    success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
