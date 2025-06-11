from extractor import Extractor
from pattern_handler import PatternHandler
from pathlib import Path
from collections.abc import Callable
from typing import TypedDict
from pattern_handler import compile_pattern
import re
from uid_generator import generate_uid
from functools import partial

class Metadata(TypedDict):
    players: tuple[str, ...]
    filtered_lines: tuple[str, ...]
    team_info: tuple[str, ...]
    innings: tuple[str, ...]
    positions: tuple[str, ...]

class MappedData(TypedDict, total=False):  # use total=False if some keys are skipped
    players: dict[str, str]
    filtered_lines: dict[str, str]
    team_info: dict[str, str]
    innings: dict[str, str]
    positions: dict[str, str]  



def inning_tagger(inning_info: str) -> str:
    half = PatternHandler("inning_half").search(inning_info).group("half").lower()
    num = PatternHandler("inning_num").search(inning_info).group("num")
    return f"entry=inning,half={half},number={num},"

def position_tagger(positions: str) -> str:
    pass

map_builder: dict[str: Callable[[str], str ] | None] = {
    "players": partial(generate_uid, entity="player"),
    "filtered_lines": None,
    "team_info": None,
    "innings": inning_tagger, 
    "positions": None
}

def mapper(metadata: Metadata) -> MappedData:
    keys = metadata.keys()
    mapping = {}
    for key, values in metadata.items():
        builder = map_builder[key]
        if builder is None: # Just here to make code work while scaffolding/prototyping
            continue
        mapping[key] = {value: builder(value) for value in values}

    return mapping


def rewriter(text: str, mapping: MappedData) -> str:

    for entity in mapping.keys():
        for key, value in mapping[entity].items():
            pattern = compile_pattern(key)
            text = pattern.sub(value, text)

    return text



def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()

    metadata = Extractor(text).extract()
    

    data = mapper(metadata)

    for entity in data.values():
        print(entity)
    new_text = rewriter(text, data)


    #print(new_text)

if __name__ == "__main__":
    main()