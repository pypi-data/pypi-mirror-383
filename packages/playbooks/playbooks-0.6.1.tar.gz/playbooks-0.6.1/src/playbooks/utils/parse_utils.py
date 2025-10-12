"""
Example input with both metadata and description --
metadata:
  framework: GAAP
  specialization:
    - accounting
    - tax
  author: John Doe
---
This is an accountant agent that can help with accounting tasks.

Example input with only description --
This is an accountant agent that can help with accounting tasks.

Example input with only metadata --
metadata:
  framework: GAAP
  specialization:
    - accounting
    - tax
  author: John Doe

Also, input can be empty.
"""

import yaml


def parse_metadata_and_description(input: str) -> tuple[dict, str]:
    """Parse the input into a metadata and description."""
    if not input or not input.strip():
        return {}, ""

    if input.startswith("metadata:"):
        parts = input.split("---", maxsplit=1)
        if len(parts) == 1:
            metadata_text = parts[0]
            description_text = ""
        else:
            metadata_text = parts[0]
            description_text = parts[1]
        metadata = yaml.safe_load(metadata_text)["metadata"] or {}
        description = description_text.strip()
    else:
        metadata = {}
        description = input.strip()

    return metadata, description
