"""
Module for assigning unique ABIDs (at-bat IDs) to pairs of `entry=atbat` lines.
Each pair is converted into a structured event and outcome with a shared ABID.
"""

from itertools import zip_longest
from pathlib import Path


def generate_abid() -> str:
    """Generate a zero-padded, incrementing at-bat ID from a counter file."""
    counter_file = Path("atbat_counter_ids.txt")
    current = int(counter_file.read_text().strip()) if counter_file.exists() else 0
    current += 1
    counter_file.write_text(str(current))
    return f"{current:09d}"


def tag_abid_block(atbat_lines: list[str]) -> list[str]:
    """
    Convert pairs of `entry=atbat` lines into structured `entry=atbat_events` and
    `entry=atbat_outcome` lines with a shared ABID.
    """
    tagged = []
    for first, second in zip_longest(*[iter(atbat_lines)] * 2):
        abid = generate_abid()
        if first:
            stripped = first.removeprefix("entry=atbat").lstrip(", ")
            tagged.append(f"entry=atbat_events, abid={abid}, {stripped}")
        if second:
            stripped = second.removeprefix("entry=atbat").lstrip(", ")
            tagged.append(f"entry=atbat_outcome, abid={abid}, {stripped}")
    return tagged


def insert_abids(text: str) -> str:
    """
    Scan the full text and replace `entry=atbat` lines with ABID-tagged event/outcome pairs.
    Preserves `entry=inning` and other lines while grouping and tagging at-bat lines.
    """
    lines = text.splitlines()
    output = []
    current_block = []

    for line in lines:
        if line.startswith("entry=inning"):
            output.extend(tag_abid_block(current_block))
            current_block.clear()
            output.append(line)
        elif line.startswith("entry=atbat"):
            current_block.append(line)
        else:
            output.extend(tag_abid_block(current_block))
            current_block.clear()
            output.append(line)

    output.extend(tag_abid_block(current_block))  # final block
    return "\n".join(output)
