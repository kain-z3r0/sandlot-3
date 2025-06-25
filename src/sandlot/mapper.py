from collections.abc import Callable
from functools import partial
from typing import TypedDict

from pattern_handler import PatternHandler, compile_pattern
from uid_generator import generate_uid

# --- Data Contracts ---


class Metadata(TypedDict):
    players: tuple[str, ...]
    filtered_lines: tuple[str, ...]
    team_info: tuple[str, ...]
    innings: tuple[str, ...]
    positions: tuple[str, ...]


class MappedData(TypedDict, total=False):
    players: dict[str, str]
    filtered_lines: dict[str, str]
    team_info: dict[str, str]
    innings: dict[str, str]
    positions: dict[str, str]


# --- Tagger Functions ---


def tag_inning(line: str) -> str:
    """Convert inning description into a structured tag line."""
    half = PatternHandler("inning_half").search(line).group("half").lower()
    num = PatternHandler("inning_num").search(line).group("num")
    return f"entry=inning,half={half},number={num},"


def tag_position(_: str) -> str:
    """Placeholder for future position tagging logic."""
    return ""


def tag_filtered_line(_: str) -> str:
    """Stub tagger for filtered lines."""
    return ""


# --- Tagger Registry ---

tagger_registry: dict[str, Callable[[str], str] | None] = {
    "players": partial(generate_uid, entity="player"),
    "filtered_lines": tag_filtered_line,
    "team_info": partial(generate_uid, entity="team"),
    "innings": tag_inning,
    "positions": None,
}


# --- Mapping Logic ---


def build_mapping(metadata: Metadata) -> MappedData:
    """Apply taggers to each metadata group to build a mapped data dictionary."""
    mapping: MappedData = {}
    for key, values in metadata.items():
        tagger = tagger_registry.get(key)
        if tagger is None:
            continue
        mapping[key] = {value: tagger(value) for value in values}
    return mapping


# --- Replacement Logic ---


def apply_tag_replacements(text: str, mapping: MappedData) -> str:
    """Apply compiled regex replacements using tag mappings."""
    for group, replacements in mapping.items():
        for original, replacement in replacements.items():
            is_line_mode = group == "filtered_lines"
            pattern = compile_pattern(
                original,
                use_boundaries=not is_line_mode,
                entire_line=is_line_mode,
            )
            text = pattern.sub(replacement, text)
    return "\n".join(line for line in text.splitlines() if line.strip())
