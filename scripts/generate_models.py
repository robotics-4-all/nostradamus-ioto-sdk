#!/usr/bin/env python3
"""Script to generate Pydantic models from OpenAPI specification."""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Generate Pydantic models from OpenAPI spec."""
    project_root = Path(__file__).parent.parent
    openapi_file = project_root / "ioto-api.json"
    output_file = project_root / "nostradamus_ioto_sdk" / "models" / "_generated.py"

    if not openapi_file.exists():
        print(f"Error: OpenAPI spec not found at {openapi_file}")
        sys.exit(1)

    print(f"Generating models from {openapi_file}...")
    print(f"Output file: {output_file}")

    # Use datamodel-code-generator to generate models
    cmd = [
        "datamodel-codegen",
        "--input",
        str(openapi_file),
        "--output",
        str(output_file),
        "--input-file-type",
        "openapi",
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--target-python-version",
        "3.8",
        "--use-standard-collections",
        "--use-schema-description",
        "--field-constraints",
        "--strict-nullable",
        "--use-default",
        "--enum-field-as-literal",
        "one",
        "--collapse-root-models",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Models generated successfully!")
        print(result.stdout)

        # Display some stats
        with open(output_file) as f:
            lines = f.readlines()
            print(f"\nGenerated {len(lines)} lines of code")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating models: {e}")
        print(e.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
