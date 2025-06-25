import re
from functools import lru_cache
from pathlib import Path

import yaml

def clean_tagged_line(text: str) -> str:
    """Clean a tagged line by removing all periods and normalizing spacing.

    - Removes all `.` characters
    - Removes space before commas
    - Normalizes comma spacing
    - Collapses multiple spaces
    """
    text = text.replace(".", "")               # remove all periods
    text = re.sub(r"\s+,", ",", text)          # remove space before commas
    text = re.sub(r",\s+", ", ", text)         # normalize comma spacing
    text = re.sub(r"\s{2,}", " ", text)        # collapse extra spaces
    return text.strip()



@lru_cache(maxsize=1)
def load_event_phrase_map(filepath: str | Path = "ab_event_mapping.yaml") -> dict[str, str]:
    """Load and flatten YAML-based AB event mapping phrases into sorted (longest-first) dict."""
    raw = yaml.safe_load(Path(filepath).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{filepath!r} must contain a top-level mapping")

    flat = {
        key: " ".join(val.splitlines()).strip().replace("  ", " ")
        for key, val in raw.items()
    }
    return dict(sorted(flat.items(), key=lambda kv: len(kv[0]), reverse=True))


def replace_ab_raw_events(text: str) -> str:
    """Replace 'ab_raw=...' phrases with mapped event tags using longest-match lookup."""
    mapping = load_event_phrase_map()
    updated_lines = []

    for line in text.splitlines():
        if "ab_raw=" not in line:
            updated_lines.append(clean_tagged_line(line))
            continue

        match = re.search(r"ab_raw=([^,]+)", line)
        if not match:
            updated_lines.append(clean_tagged_line(line))
            continue

        raw_text = match.group(1).strip()
        enriched = raw_text

        for phrase, replacement in mapping.items():
            if phrase in enriched:
                enriched = enriched.replace(phrase, replacement + " ")

        # Remove ab_raw=... from line
        line = re.sub(r",?\s*ab_raw=[^,]+", "", line)

        # Append enriched tags to line
        updated_lines.append(clean_tagged_line(f"{line}, {enriched}"))

    return "\n".join(updated_lines)
