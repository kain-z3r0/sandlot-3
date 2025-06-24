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


def filter_lines(filtered_lines: str) -> str:
    return ""


map_builder: dict[str : Callable[[str], str] | None] = {
    "players": partial(generate_uid, entity="player"),
    "filtered_lines": filter_lines,
    "team_info": partial(generate_uid, entity="team"),
    "innings": inning_tagger,
    "positions": None,
}

ABID_FILE = Path("atbat_ids.txt")


def mapper(metadata: Metadata) -> MappedData:
    keys = metadata.keys()
    mapping = {}
    for key, values in metadata.items():
        builder = map_builder[key]
        if builder is None:  # Just here to make code work while scaffolding/prototyping
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
            entire_line = entry == "filtered_lines"
            pattern = compile_pattern(
                entity, use_boundaries=not entire_line, entire_line=entire_line
            )
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
    for line1, line2 in zip_longest(*[iter(taggable)] * 2, fillvalue=None):
        abid = get_atbat_id()
        if line1:
            tagged_map[line1] = (
                f"entry=atbat_events, abid={abid}"
                + line1.removeprefix("entry=atbat").lstrip()
            )
        if line2:
            tagged_map[line2] = (
                f"entry=atbat_outcome, abid={abid}"
                + line2.removeprefix("entry=atbat").lstrip()
            )

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
    strike_pattern = re.compile(r"(?P<strikes>, Strike [1-3]\b(?:\s+\w+)*)")
    foul_pattern = re.compile(r"(?P<fouls>, Foul)")
    lines = text.splitlines()

    for line in lines:
        if not line.startswith("entry=atbat_events"):
            result.append(line)
            continue
        balls = 0
        strikes = 0
        fouls = 0
        for word in line.split(","):

            balls += (1 if word.startswith(" Ball") else 0)
            fouls += (1 if word.startswith(" Foul") else 0)
            strikes += (1 if word.startswith(" Strike") else 0)
            if word.startswith(" Foul"):
                strikes += (1 if strikes < 2 else 0)

        count = f"{balls}-{strikes}"
        updated_line = ball_pattern.sub("", line).replace(".", "")
        updated_line = strike_pattern.sub("", updated_line)
        updated_line = foul_pattern.sub("", updated_line)
        result.append(f"{updated_line}, pitch_count={count}")
    


    return "\n".join(result)

def tag_batter(text: str) -> str:
    lines = text.splitlines()
    result = []
    player_pattern = re.compile(r"(?P<batter>player_[a-z]{7})")

    for line in lines:
        if line.startswith("entry=atbat_outcome"):
            match = player_pattern.search(line)
            batter = match.group("batter") if match is not None else "none"
            updated_line = line.replace(batter, f"batter={batter}")
            result.append(updated_line)
        else:
            result.append(line)

    return "\n".join(result)

def tag_outcome(text: str) -> str:
    result = []
    lines = text.splitlines()
    outcome_pattern = re.compile(r"batter=player_[a-z]{7} (?P<outcome>.*?)[,.]")
    for line in lines:
        if line.startswith("entry=atbat_outcome"):
            match = outcome_pattern.search(line)
            print(match.group("outcome") if match is not None else "missing")
            outcome = match.group("outcome") if match is not None else "missing"
            updated_line = outcome_pattern.sub("", line) 
            result.append(f"{updated_line}, outcome={outcome}")
        else:
            result.append(line)

    return "\n".join(result)



def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()

    metadata = Extractor(text).extract()

    data = mapper(metadata)

    new_text = replacer(text, data)
    u_text = rewriter(new_text)
    n_text = add_abid(u_text)
    t = pitch_counter(n_text)
    b = tag_batter(t)
    c = tag_outcome(b)
    print(c)


if __name__ == "__main__":
    main()
