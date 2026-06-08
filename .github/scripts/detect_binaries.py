#!/usr/bin/env python3
"""
detect_binaries.py

Scans for binary files being added in a pull request.
If any are found, formats a friendly markdown comment explaining how to configure
them via blobs.json, and writes the comment to .github/detected_binaries_comment.md.
Also sets GITHUB_OUTPUT binaries_found=true/false.
"""

import os
import sys
import subprocess


def is_binary_file(filepath: str) -> bool:
    """
    Checks if a file is binary by looking for a null byte in its first 8192 bytes.
    """
    if not os.path.exists(filepath):
        return False
    if os.path.islink(filepath):
        return False
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception as e:
        print(f"Warning: Could not read file {filepath}: {e}", file=sys.stderr)
        return False


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
        print(f"Warning: Error scanning directory for templates: {e}", file=sys.stderr)
    return sorted(templates)


def get_template_and_relative_path(filepath: str, templates: list) -> tuple:
    """
    Returns the template directory and the relative path of the file within that template,
    or (None, filepath) if the file is not within a template directory.
    """
    normalized_path = os.path.normpath(filepath)
    parts = normalized_path.split(os.sep)
    if parts and parts[0] in templates:
        template = parts[0]
        # Get path relative to the template directory
        rel_path = os.path.join(*parts[1:]) if len(parts) > 1 else ""
        return template, rel_path
    return None, normalized_path


def run_git_command(args: list) -> str:
    """
    Runs a git command and returns its stdout, or empty string on failure.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Warning: git command failed: {' '.join(e.cmd)}. Error: {e.stderr}", file=sys.stderr)
        return ""


def main():
    # 1. Determine the base branch
    # Typically passed as an argument or from the environment
    base_branch = "main"
    if len(sys.argv) > 1:
        base_branch = sys.argv[1]
    elif os.getenv("GITHUB_BASE_REF"):
        base_branch = os.getenv("GITHUB_BASE_REF")

    print(f"Comparing HEAD against origin/{base_branch} to find added files...")

    # 2. Get list of files added in the PR/branch
    # We use git diff --name-only --diff-filter=A
    # First we check with origin/{base_branch}
    diff_target = f"origin/{base_branch}"
    
    # Let's verify if origin/{base_branch} exists, otherwise fallback to local base_branch or HEAD~1
    check_ref = run_git_command(["rev-parse", "--verify", diff_target])
    if not check_ref:
        print(f"Warning: {diff_target} not found, checking local {base_branch}...")
        diff_target = base_branch
        check_ref = run_git_command(["rev-parse", "--verify", diff_target])
        if not check_ref:
            print("Warning: Base branch ref not found. Falling back to HEAD~1...")
            diff_target = "HEAD~1"

    added_files_str = run_git_command(["diff", "--name-only", "--diff-filter=A", f"{diff_target}...HEAD"])
    if not added_files_str:
        # Fallback to direct diff if triple-dot comparison is not possible or returns empty
        added_files_str = run_git_command(["diff", "--name-only", "--diff-filter=A", diff_target, "HEAD"])

    added_files = [f.strip() for f in added_files_str.split("\n") if f.strip()]

    print(f"Found {len(added_files)} added files in this pull request.")

    # 3. Check for binary files
    binary_files = []
    templates = find_templates()

    for filepath in added_files:
        if is_binary_file(filepath):
            binary_files.append(filepath)

    # 4. Handle result
    github_output = os.getenv("GITHUB_OUTPUT")

    if not binary_files:
        print("No added binary files detected. Great job!")
        if github_output:
            with open(github_output, "a") as f:
                f.write("binaries_found=false\n")
        sys.exit(0)

    print(f"Detected {len(binary_files)} binary files checked in directly:")
    for bf in binary_files:
        print(f"  - {bf}")

    # Set output variable
    if github_output:
        with open(github_output, "a") as f:
            f.write("binaries_found=true\n")

    # 5. Generate friendly markdown comment
    comment_lines = [
        "### ⚠️ Direct Binary File Uploads Detected",
        "",
        "Hi! It looks like you've added some binary files directly to this pull request. "
        "To keep the repository lightweight and comply with licensing terms, **binary files (including PDFs) "
        "and assets of unclear licensing must not be checked directly into this git repository.**",
        "",
        "Instead, please configure these reference assets using `blobs.json` so they can be downloaded dynamically.",
        "",
        "#### Detected Binary Files:",
        "| File Path | Action Required |",
        "| :--- | :--- |"
    ]

    for bf in binary_files:
        template, rel_path = get_template_and_relative_path(bf, templates)
        if template:
            comment_lines.append(
                f"| `{bf}` | Move to `{template}/blobs.json` under key `{rel_path}` |"
            )
        else:
            comment_lines.append(
                f"| `{bf}` | This file is in the root directory. Please place it inside a template directory and configure it via `blobs.json`. |"
            )

    comment_lines.extend([
        "",
        "---",
        "",
        "#### How to Fix This:",
        "",
        "1. **Remove the binary files from your git commit:**",
        "   ```bash",
    ])

    for bf in binary_files:
        comment_lines.append(f"   git rm --cached {bf}")

    comment_lines.extend([
        "   git commit --amend --no-edit # Or create a new commit removing them",
        "   ```",
        "",
        "2. **Add the assets to `blobs.json`:**",
        "   For each file, open the corresponding `blobs.json` file (e.g., `bifurcation/blobs.json`) and map the filename (relative to the template folder) to its public download URL. For example:",
        "   ```json",
        "   {",
    ])

    # Show a customized example based on the first detected binary file
    example_bf = binary_files[0]
    example_template, example_rel = get_template_and_relative_path(example_bf, templates)
    if not example_template:
        example_template = "template_name"
        example_rel = os.path.basename(example_bf)
    
    comment_lines.extend([
        f'     "{example_rel}": "https://example.com/path/to/{example_rel}"',
        "   }",
        "   ```",
        "",
        "3. **Test downloading the files locally:**",
        f"   ```bash",
        f"   python3 download_blobs.py {example_template if example_template != 'template_name' else ''}",
        f"   ```",
        "",
        "4. **Push your updated branch:**",
        "   ```bash",
        "   git push --force-with-lease",
        "   ```",
        "",
        "Thank you for helping us keep the repository lightweight! 🚀"
    ])

    # Write comment to file
    os.makedirs(".github", exist_ok=True)
    comment_file_path = os.path.join(".github", "detected_binaries_comment.md")
    with open(comment_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(comment_lines) + "\n")

    print(f"PR comment written to {comment_file_path}")


if __name__ == "__main__":
    main()
