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
    atbat_block = []

    for line in lines:
        if line.startswith("entry=inning"):
            result.extend(process_atbat_block(atbat_block))
            atbat_block = []
            result.append(line)
        elif line.startswith("entry=atbat"):
            atbat_block.append(line)
        else:
            result.extend(process_atbat_block(atbat_block))
            atbat_block = []
            result.append(line)

    # Final block
    result.extend(process_atbat_block(atbat_block))
    return "\n".join(result)


def process_atbat_block(lines: list[str]) -> list[str]:
    output = []
    for l1, l2 in zip_longest(*[iter(lines)] * 2):
        abid = get_atbat_id()
        if l1:
            entry = l1.removeprefix("entry=atbat").lstrip(", ")
            output.append(f"entry=atbat_events, abid={abid}, {entry}")
        if l2:
            entry = l2.removeprefix("entry=atbat").lstrip(", ")
            output.append(f"entry=atbat_outcome, abid={abid}, {entry}")
    return output


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
            balls += 1 if word.startswith(" Ball") else 0
            fouls += 1 if word.startswith(" Foul") else 0
            strikes += 1 if word.startswith(" Strike") else 0
            if word.startswith(" Foul"):
                strikes += 1 if strikes < 2 else 0

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
    outcome_pattern = re.compile(r"batter=player_[a-z]{7}(?P<outcome>.*?)[,.]")
    for line in lines:
        if line.startswith("entry=atbat_outcome"):
            match = outcome_pattern.search(line)
            outcome = match.group("outcome").strip() if match is not None else "missing"
            updated_line = line.replace(outcome, f", ab_result={outcome}")
            result.append(updated_line)
        else:
            result.append(line)

    return "\n".join(result)


def in_play(text: str) -> str:
    lines = text.splitlines()
    result = []
    for line in lines:
        if not line.startswith("entry=atbat_events"):
            result.append(line)
            continue
        updated_line = line.replace("In play", "outcome_type=battedball")
        result.append(updated_line)

    return "\n".join(result)


def find_positions(text: str) -> str:
    lines = text.splitlines()
    pos_pattern = re.compile(r"to (\w+(?:\s+\w+){0,2}) player_")
    positions = set()

    for line in lines:
        if not line.startswith("entry=atbat_outcome"):
            continue
        pos = pos_pattern.findall(line)
        positions.update(pos)
    return positions


POSITIONS = {
    "first baseman",
    "pitcher",
    "second baseman",
    "center fielder",
    "left fielder",
    "shortstop",
    "catcher",
    "third baseman",
    "right fielder",
}


def get_outcome(text):
    lines = text.splitlines()
    pattern = re.compile(r"ab_result=(?P<outcome>.*?)(?=,|player_)")

    result = [
        match.group("outcome") for line in lines if (match := pattern.search(line))
    ]

    return set(result)


grouped_phrases = {
    # Singles
    "singles on a bunt ": "ab_result=single, batted_type=bunt, play_type=battedball, outs_recorded=0",
    "singles on a fly ball ": "ab_result=single, batted_type=flyball, play_type=battedball, outs_recorded=0",
    "singles on a ground ball ": "ab_result=single, batted_type=groundball, play_type=battedball, outs_recorded=0",
    "singles on a hard ground ball ": "ab_result=single, batted_type=groundball, play_type=battedball, batted_strength=hard, outs_recorded=0",
    "singles on a line drive ": "ab_result=single, batted_type=linedrive, play_type=battedball, outs_recorded=0",
    "singles on a pop fly ": "ab_result=single, batted_type=popup, play_type=battedball, outs_recorded=0",

    # Doubles
    "doubles on a fly ball ": "ab_result=double, batted_type=flyball, play_type=battedball, outs_recorded=0",
    "doubles on a ground ball ": "ab_result=double, batted_type=groundball, play_type=battedball, outs_recorded=0",
    "doubles on a hard ground ball ": "ab_result=double, batted_type=groundball, play_type=battedball, batted_strength=hard, outs_recorded=0",
    "doubles on a line drive ": "ab_result=double, batted_type=linedrive, play_type=battedball, outs_recorded=0",

    # Triples
    "triples on a fly ball ": "ab_result=triple, batted_type=flyball, play_type=battedball, outs_recorded=0",
    "triples on a hard ground ball ": "ab_result=triple, batted_type=groundball, play_type=battedball, batted_strength=hard, outs_recorded=0",
    "triples on a line drive ": "ab_result=triple, batted_type=linedrive, play_type=battedball, outs_recorded=0",

    # Home Runs
    "homers on a fly ball ": "ab_result=homerun, batted_type=flyball, play_type=battedball, outs_recorded=0",
    "hits an inside the park home run on a fly ball ": "ab_result=homerun, batted_type=flyball, play_type=battedball, outs_recorded=0",
    "hits an inside the park home run on a hard ground ball ": "ab_result=homerun, batted_type=groundball, play_type=battedball, batted_strength=hard, outs_recorded=0",

    # Walks / HBP
    "walks ": "ab_result=walk, play_type=non_batted, outs_recorded=0",
    "is hit by pitch ": "ab_result=hit_by_pitch, play_type=non_batted, outs_recorded=0"

    # Reaches on Error
    "hits a ground ball and reaches on an error ": "ab_result=reaches_on_error, batted_type=groundball, play_type=error, outs_recorded=0",
    "hits a fly ball and reaches on an error ": "ab_result=reaches_on_error, batted_type=flyball, play_type=error, outs_recorded=0",
    "hits a line drive and reaches on an error ": "ab_result=reaches_on_error, batted_type=linedrive, play_type=error, outs_recorded=0",
    "hits a hard ground ball and reaches on an error ": "ab_result=reaches_on_error, batted_type=groundball, batted_strength=hard, play_type=error, outs_recorded=0",
    "reaches on dropped 3rd strike (wild pitch) ": "ab_result=strikeout_dropped_third_strike, play_type=dropped_third_strike, pitch_type=wild_pitch, outs_recorded=0",
    "reaches on dropped 3rd strike (passed ball) ": "ab_result=strikeout_dropped_third_strike, play_type=dropped_third_strike, pitch_type=passed_ball, outs_recorded=0"

    # Strikeouts
    "strikes out swinging ": "ab_result=strikeout_swinging, play_type=strikeout, outs_recorded=1",
    "strikes out looking ": "ab_result=strikeout_looking, play_type=strikeout, outs_recorded=1",
    "out at first on dropped 3rd strike ": "ab_result=strikeout_dropped_third, play_type=dropped_third_strike, outs_recorded=1",

    # Outs
    "grounds out ": "ab_result=groundout, batted_type=groundball, play_type=battedball, outs_recorded=1",
    "flies out ": "ab_result=flyout, batted_type=flyball, play_type=battedball, outs_recorded=1",
    "flies out in foul territory ": "ab_result=flyout, batted_type=flyball, play_type=battedball, foul=True, outs_recorded=1",
    "lines out ": "ab_result=lineout, batted_type=linedrive, play_type=battedball, outs_recorded=1",
    "pops out ": "ab_result=popout, batted_type=popup, play_type=battedball, outs_recorded=1",
    "pops into a double play ": "ab_result=double_play, batted_type=popup, play_type=battedball, outs_recorded=2",
    "out (other) ": "ab_result=out_other, play_type=fielded_play, outs_recorded=1",
    "out on sacrifice fly ": "ab_result=sacrifice_fly, batted_type=flyball, play_type=sacrifice, outs_recorded=1",
    "out on infield fly ": "ab_result=infield_fly, batted_type=popup, play_type=battedball, outs_recorded=1",
    "is out on foul tip ": "ab_result=strikeout_foul_tip, play_type=strikeout, outs_recorded=1",

    # Double / Multiple Outs
    "lines into a double play ": "ab_result=double_play, batted_type=linedrive, play_type=battedball, outs_recorded=2",
    "grounds into a double play ": "ab_result=double_play, batted_type=groundball, play_type=battedball, outs_recorded=2",
    "grounds into fielder's choice double play ": "ab_result=double_play, play_type=fielder_choice, batted_type=groundball, outs_recorded=2",
    "grounds into fielder's choice ": "ab_result=fielder_choice, batted_type=groundball, play_type=fielder_choice, outs_recorded=1",

    # Misc
    "sacrifices ": "ab_result=sacrifice_hit, play_type=sacrifice, outs_recorded=1",

    # Hit locations
    "to pitcher": "hit_loc=1",
    "by pitcher": "hit_loc=1",
    "to catcher": "hit_loc=2",
    "by catcher": "hit_loc=2",
    "to first baseman": "hit_loc=3",
    "by first baseman": "hit_loc=3",
    "to second baseman": "hit_loc=4",
    "by second baseman": "hit_loc=4",
    "to third baseman": "hit_loc=5",
    "by third baseman": "hit_loc=5",
    "to shortstop": "hit_loc=6",
    "by shortstop": "hit_loc=6",
    "to left fielder": "hit_loc=7",
    "by left fielder": "hit_loc=7",
    "to center fielder": "hit_loc=8",
    "by center fielder": "hit_loc=8",
    "to right fielder": "hit_loc=9",
    "by right fielder": "hit_loc=9"
}




def fix_location_formatting(text):
    pattern = re.compile(
        r"(ab_result=[^,]+), "
        r"((?:pitcher|catcher|first baseman|second baseman|third baseman|"
        r"shortstop|left fielder|center fielder|right fielder))([^,.]*)"
    )

    result = []

    for line in text.splitlines():
        if line.startswith("entry=atbat") and (match := pattern.search(line)):
            result.append(f"{match.group(1)} to {match.group(2)}")
            # print(f"Full match: {match.group(0)}")
            # print(f"Modified: {match.group(1)} to {match.group(2)}")
        else:
            result.append(line)

    return "\n".join(result)


def find_single(text):
    pattern = re.compile(r"singles on a fly ball(?! to)")
    matches = [line for line in text.splitlines() if pattern.search(line)]
    return set(matches)


def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()
    full_text_filepath = Path(__file__).resolve().parents[2] / "full_sample.txt"
    full_text = full_text_filepath.read_text()

    metadata = Extractor(full_text).extract()

    data = mapper(metadata)

    new_text = replacer(full_text, data)
    u_text = rewriter(new_text)
    n_text = add_abid(u_text)
    t = pitch_counter(n_text)
    b = tag_batter(t)
    c = tag_outcome(b)
    d = in_play(c)
    # pos = find_positions(d)
    # out = get_outcome(d)

    h = fix_location_formatting(d)
    # print(h)
    # for o in out:
    #     print(o)
    # singles = find_single(full_text)
    # for single in singles:
    #     print(single)


if __name__ == "__main__":
    main()
