import re
from collections.abc import Callable, Iterable
from functools import cache, cached_property

from pattern_store import PatternStore


class PatternHandler:
    def __init__(self, pattern_key: str):
        self.pattern_key = pattern_key

    def findall(self, text: str, flags: int = 0) -> list[str]:
        rx = PatternStore.get(self.pattern_key, flags)
        return rx.findall(text)

    def search(self, text: str, flags: int = 0) -> re.Match[str] | None:
        rx = PatternStore.get(self.pattern_key, flags)
        return rx.search(text)

    def finditer(self, text: str, flags: int = 0) -> Iterable[re.Match[str]]:
        rx = PatternStore.get(self.pattern_key, flags)
        return rx.finditer(text)

    def sub(self, repl: str | Callable[[re.Match], str], string: str, flags: int = 0) -> str:
        rx = PatternStore.get(self.pattern_key, flags)
        return rx.sub(repl, string, flags)

    @cached_property
    def pattern(self):
        return PatternStore.get(self.pattern_key)


@cache
def compile_entity_pattern(entities: tuple[str]) -> re.Pattern:
    joined = "|".join(entities)
    return re.compile(rf"(?P<entity>\b{joined})\b")


@cache
def compile_pattern(
    entity: str, use_boundaries: bool = True, entire_line: bool = False
) -> re.Pattern:
    escaped = re.escape(entity)
    if use_boundaries:
        return re.compile(rf"\b{escaped}\b")
    if entire_line:
        return re.compile(rf"^{escaped}$", re.MULTILINE)
    return re.compile(escaped)
