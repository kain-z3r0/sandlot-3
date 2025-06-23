from extractor import Extractor
from pattern_handler import PatternHandler
from pathlib import Path
from collections.abc import Callable
from typing import TypedDict
from pattern_handler import compile_pattern
import re
from uid_generator import generate_uid
from functools import partial
from itertools import count

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

def filter_lines(filtered_lines: str) -> str:
    return ""

map_builder: dict[str: Callable[[str], str ] | None] = {
    "players": partial(generate_uid, entity="player"),
    "filtered_lines": filter_lines,
    "team_info": partial(generate_uid, entity="team"),
    "innings": inning_tagger, 
    "positions": None
}

ABID_FILE = Path("atbat_ids.txt")


def mapper(metadata: Metadata) -> MappedData:
    keys = metadata.keys()
    mapping = {}
    for key, values in metadata.items():
        builder = map_builder[key]
        if builder is None: # Just here to make code work while scaffolding/prototyping
            continue
        mapping[key] = {value: builder(value) for value in values}

    return mapping

def get_atbat_id() -> str:
    ab_counter_file = Path("atbat_counter_ids.txt")

    if ab_counter_file.is_file():
        current = int(ab_counter_file.read_text().strip())
    else:
        current = 0

    current += 1
    ab_counter_file.write_text(str(current))

    return f"{current:09d}"

def replacer(text: str, mapping: MappedData) -> str:
    for entry, replacements in mapping.items():
        for entity, replacement in replacements.items():
            entire_line = (entry == "filtered_lines")
            pattern = compile_pattern(entity, use_boundaries=not entire_line, entire_line=entire_line)
            text = pattern.sub(replacement, text)

    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def rewriter(text: str) -> str:
    updated_text = [
        f"entry=atbat, {line}" if not line.startswith("entry=inning") else line 
        for line in text.splitlines() 
    ]
    return "\n".join(updated_text)

from itertools import zip_longest

def add_abid(text: str) -> str:
    lines = text.splitlines()
    result = []

    # Extract non-inning lines for tagging
    taggable = [line for line in lines if not line.startswith("entry=inning")]
    tagged_map = {}

    # Assign abid in pairs
    for line1, line2 in zip_longest(*[iter(taggable)]*2, fillvalue=None):
        abid = get_atbat_id()
        if line1:
            tagged_map[line1] = f"entry=atbat_events, abid={abid}" + line1.removeprefix("entry=atbat").lstrip()
        if line2:
            tagged_map[line2] = f"entry=atbat_outcome, abid={abid}" + line2.removeprefix("entry=atbat").lstrip()


    # Rebuild in original order
    for line in lines:
        result.append(tagged_map.get(line, line))

    return "\n".join(result)





sample_text = (
    "entry=atbat_events, abid=000000128, Score changed to 10-7, Ball 1, Strike 1 looking, Ball 2," 
    " Foul, Foul, Strike 3 looking."
)

def pitch_counter(text: str) -> str:
    result = []
    ball_pattern = re.compile(r"(?P<balls>, Ball [1-4])")
    strike_pattern = re.compile(r"(?P<strikes>), Strike [1-3]\b(?:\s+\w+)*)")
    foul_pattern = re.compile(r"(?P<fouls>Foul)")
    # ball_pattern = r"(?P<balls>, Ball [1-4])"
    # strike_pattern = r"(?P<strikes>, Strike [1-3]\b(?:\s+\w+)*)"
    # foul_pattern = r"(?P<fouls>Foul)"
    # pc_regex = re.compile(rf"{ball_pattern}|{strike_pattern}|{foul_pattern}")
    lines = text.splitlines()

    for line in lines:
        if not line.startswith("entry=atbat_events"):
            result.append(line)
            continue

        events = line.split(",")
        for event in events:
            

            print(f"{balls=}: {strikes=}")


        updated_line = ball_pattern.sub("", line).replace(".", "")
        updated_line = strike_pattern.sub("", updated_line)
        updated_line = f"{updated_line}, pitch_count={balls}-{strikes}"
        result.append(updated_line)

    return "\n".join(result)






def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()

    metadata = Extractor(text).extract()
    

    data = mapper(metadata)

    new_text = replacer(text, data)
    u_text = rewriter(new_text)
    n_text = add_abid(u_text)
    t = pitch_counter(sample_text)
    print(t)


if __name__ == "__main__":
    main()