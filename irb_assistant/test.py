#!/usr/bin/env python3
"""
test_jsonschemas.py

Scan the jsonschema_specifications package for any malformed JSON files, BOM markers, or stray non-JSON files and report them.
"""
import json
import importlib.metadata
from pathlib import Path


def main():
    # Locate the jsonschema-specifications install location
    try:
        dist = importlib.metadata.distribution('jsonschema-specifications')
        base = Path(dist.locate_file(''))
        schemas_dir = base / 'jsonschema_specifications' / 'schemas'
    except importlib.metadata.PackageNotFoundError:
        print("jsonschema-specifications not installed.")
        return

    errors = False
    # Iterate through all files under schemas/
    for file in schemas_dir.rglob('*'):
        if not file.is_file():
            continue
        rel = file.relative_to(schemas_dir)
        suffix = file.suffix.lower()
        if suffix == '.json':
            # Check for UTF-8 BOM (0xEF 0xBB 0xBF)
            raw = file.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                print(f"❌ BOM found in {rel}")
                errors = True
                text = raw.decode('utf-8-sig')
            else:
                text = raw.decode('utf-8')
            # Validate JSON
            try:
                json.loads(text.lstrip())
            except Exception as e:
                print(f"❌ JSON error in {rel}: {e}")
                errors = True
        else:
            # Non-JSON file detected
            print(f"⚠️ Non-JSON file found in schemas: {rel}")
            errors = True

    if not errors:
        print("✅ All .json files parse cleanly and no stray files detected.")


if __name__ == "__main__":
    main()
