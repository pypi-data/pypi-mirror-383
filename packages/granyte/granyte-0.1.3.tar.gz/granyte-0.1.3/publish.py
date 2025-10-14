#!/usr/bin/env python3
"""Bump version, commit, tag, and push"""

import re
import subprocess
import sys
from pathlib import Path


def run(cmd):
    """Run shell command"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def get_current_version():
    """Read version from pyproject.toml"""
    pyproject = Path("pyproject.toml").read_text()
    match = re.search(r'version = "([^"]+)"', pyproject)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)
    return match.group(1)


def bump_version(version, part="patch"):
    """Bump version (major.minor.patch)"""
    major, minor, patch = map(int, version.split("."))
    
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def update_file(filepath, old_version, new_version):
    """Update version in file"""
    content = Path(filepath).read_text()
    updated = content.replace(old_version, new_version)
    Path(filepath).write_text(updated)
    print(f"Updated {filepath}")


def main():
    # Get bump type from argument or default to patch
    bump_type = sys.argv[1] if len(sys.argv) > 1 else "patch"
    
    if bump_type not in ["major", "minor", "patch"]:
        print("Usage: python bump.py [major|minor|patch]")
        print("Default: patch")
        sys.exit(1)
    
    # Get current version
    current = get_current_version()
    print(f"Current version: {current}")
    
    # Bump version
    new = bump_version(current, bump_type)
    print(f"New version: {new}")
    
    # Confirm
    response = input(f"Bump from {current} to {new}? [y/N] ")
    if response.lower() != 'y':
        print("Aborted")
        sys.exit(0)
    
    # Update files
    update_file("pyproject.toml", current, new)
    update_file("granyte/__init__.py", current, new)
    
    # Git operations
    run("git add pyproject.toml granyte/__init__.py")
    run(f'git commit -m "Bump version to {new}"')
    run(f"git tag v{new}")
    run("git push")
    run("git push --tags")
    
    print(f"\n✓ Released version {new}")
    print(f"Check GitHub Actions: https://github.com/UlfBissbort/granyte-python/actions")


if __name__ == "__main__":
    main()