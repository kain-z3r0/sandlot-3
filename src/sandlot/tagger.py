from extractor import Extractor
from pattern_handler import PatternHandler
from pathlib import Path
from collections.abc import Callable

def inning_tagger(inning_info: str) -> str:
    half = PatternHandler("inning_half").search(inning_info).group("half").lower()
    num = PatternHandler("inning_num").search(inning_info).group("num")
    return f"type=inning,half={half},number={num},"

def position_tagger(positions: str) -> str:
    pass


def up(text):
    return text.upper()

map_builder: dict[str: Callable[[str], str]] = {
    "players": up,
    "filtered_lines": up,
    "team_info": up,
    "innings": inning_tagger
}

def mapper(metadata: dict[str, tuple[str, ...]]):
    keys = metadata.keys()
    mapping = {}
    for key, values in metadata.items():
        builder = map_builder[key]
        mapping[key] = {value: builder(value) for value in values}

    return mapping



def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()

    metadata = Extractor(text).extract()
    

    data = mapper(metadata)
    print(data)
    # for keys in metadata.keys():
    #     print(keys)

    # for innings in metadata["innings"]:
    #     print(innings)

if __name__ == "__main__":
    main()