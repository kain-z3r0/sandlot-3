"""
uid_generator.py

Provides functions to generate unique IDs for players and teams,
tagged with 'PLAYER_' or 'TEAM_' prefixes.
"""

from functools import cache
from collections.abc import Callable

__all__ = ["generate_uid"]

VOWELS = frozenset("AEIOUY")


def _normalize_name(name: str) -> str:
    """
    Uppercases and strips non-alphanumeric characters from a name.

    Args:
        name: The input name string.

    Returns:
        A normalized uppercase string with only letters and digits.
    """
    return "".join(char.lower() for char in name if char.isalnum())


def _normalize_split_name(name: str) -> tuple[str, str]:
    """
    Normalizes a name and splits it into a prefix and remaining characters.

    Args:
        name: The input name string.

    Returns:
        A tuple of (prefix, remaining_characters).
    """
    prefix_len = 2
    normalized_name = _normalize_name(name)
    prefix = normalized_name[:prefix_len]
    core_name = normalized_name[prefix_len:]
    return prefix, core_name


def _split_chars_by_vowel_type(core_name: str):
    """
    Splits characters into vowels and non-vowels, preserving their order.

    Args:
        core_name: The string to split.

    Returns:
        A tuple of (non_vowels, vowels), each as a list of (index, char).
    """
    non_vowels = []
    vowels = []
    for idx, char in enumerate(core_name):
        (vowels if char in VOWELS else non_vowels).append((idx, char))
    return non_vowels, vowels


def _select_chars(non_vowels, vowels, chars_needed: int) -> str:
    """
    Selects characters in order: non-vowels first, then vowels if needed.

    Args:
        non_vowels: List of (index, char) non-vowel tuples.
        vowels: List of (index, char) vowel tuples.
        chars_needed: Total number of characters to select.

    Returns:
        A string of selected characters in original order.
    """
    selected_chars = non_vowels[:chars_needed]
    vowel_count = max(0, chars_needed - len(selected_chars))
    selected_chars += vowels[:vowel_count]
    ordered_chars = "".join(char for _, char in sorted(selected_chars, key=lambda x: x[0]))
    return ordered_chars


def _build_team_uid(name: str) -> str:
    """
    Builds a team UID with a 'team_at_bat=' prefix.

    Args:
        name: The team name.

    Returns:
        A team UID string of fixed length.
    """
    id_length: int = 7
    prefix, remaining_chars = _normalize_split_name(name)
    non_vowels, vowels = _split_chars_by_vowel_type(remaining_chars)
    chars_needed = id_length - len(prefix)
    core_name = _select_chars(non_vowels, vowels, chars_needed)
    suffix = core_name.ljust(chars_needed, "x")
    return f"team_{prefix}{suffix}"


def _build_player_uid(name: str) -> str:
    """
    Builds a player UID with a 'player=' prefix.

    Args:
        name: The player name.

    Returns:
        A player UID string of fixed length.
    """
    id_length: int = 7
    normalized_name = _normalize_name(name)
    core_name = normalized_name[:id_length]
    suffix = core_name.ljust(id_length, "x")
    return f"player_{suffix}"


_uid_builders: dict[str, Callable[[str], str]] = {
    "team": _build_team_uid,
    "player": _build_player_uid,
}


@cache
def generate_uid(value: str, entity: str) -> str:
    """
    Generates a unique, prefixed identifier for a given name and entity type.

    Args:
        value: The name of the player or team.
        entity: Either 'player' or 'team'.

    Returns:
        A string like 'player=JULIANX' or 'team_at_bat=AZBC123'.

    Raises:
        ValueError: If the entity type is not supported.
    """
    try:
        builder = _uid_builders[entity]
        return builder(value)
    except KeyError:
        raise ValueError(f"Entity type '{entity}' not supported!")
