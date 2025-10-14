#!/usr/bin/env python3
"""
Script to help build and publish the corebrum package to PyPI.
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main function to build and publish the package."""
    print("🚀 Corebrum Package Builder and Publisher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("setup.py"):
        print("❌ Error: setup.py not found. Please run this script from the package root directory.")
        sys.exit(1)
    
    # Clean previous builds
    if not run_command("rm -rf build/ dist/ *.egg-info/", "Cleaning previous builds"):
        print("⚠️  Warning: Could not clean previous builds")
    
    # Install build tools
    if not run_command("pip install --upgrade build twine", "Installing build tools"):
        print("❌ Failed to install build tools")
        sys.exit(1)
    
    # Build the package
    if not run_command("python -m build", "Building package"):
        print("❌ Failed to build package")
        sys.exit(1)
    
    # Check the build
    if not run_command("python -m twine check dist/*", "Checking package"):
        print("❌ Package check failed")
        sys.exit(1)
    
    print("\n🎉 Package built successfully!")
    print("\nNext steps:")
    print("1. Test the package locally:")
    print("   pip install dist/corebrum-0.1.0-py3-none-any.whl")
    print("\n2. Upload to TestPyPI (recommended first):")
    print("   python -m twine upload --repository testpypi dist/*")
    print("\n3. Upload to PyPI:")
    print("   python -m twine upload dist/*")
    print("\nNote: You'll need to create accounts on PyPI and TestPyPI if you haven't already.")
    print("Also, make sure to update the version number in corebrum/__init__.py and pyproject.toml")
    print("before publishing a new version.")


if __name__ == "__main__":
    main()
