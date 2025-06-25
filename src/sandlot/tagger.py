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
            updated_line = line.replace(outcome, f", ab_raw={outcome}")
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
    pattern = re.compile(r"ab_raw=(?P<outcome>.*?)(?=,|player_)")

    result = [
        match.group("outcome") for line in lines if (match := pattern.search(line))
    ]

    return set(result)


# *** Collision-safe mapping ***
# Keys are automatically ordered from longest to shortest, so substring
# collisions (e.g. “grounds into fielder’s choice ” vs
# “grounds into fielder’s choice double play ”) cannot occur.
grouped_phrases = dict(
    sorted(
        {
            # Singles
            "singles on a hard ground ball ": "ab_result=single, event_type=hit, batted_type=groundball, contact_quality=hard, outs_recorded=0, is_pa=true, is_ab=true, ab_description=singles on a hard ground ball",
            "singles on a ground ball ": "ab_result=single, event_type=hit, batted_type=groundball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=singles on a ground ball",
            "singles on a fly ball ": "ab_result=single, event_type=hit, batted_type=flyball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=singles on a fly ball",
            "singles on a line drive ": "ab_result=single, event_type=hit, batted_type=linedrive, outs_recorded=0, is_pa=true, is_ab=true, ab_description=singles on a line drive",
            "singles on a pop fly ": "ab_result=single, event_type=hit, batted_type=popup, outs_recorded=0, is_pa=true, is_ab=true, ab_description=singles on a pop fly",
            "singles on a bunt ": "ab_result=single, event_type=hit, batted_type=bunt, outs_recorded=0, is_pa=true, is_ab=true, ab_description=singles on a bunt",

            # Doubles
            "doubles on a hard ground ball ": "ab_result=double, event_type=hit, batted_type=groundball, contact_quality=hard, outs_recorded=0, is_pa=true, is_ab=true, ab_description=doubles on a hard ground ball",
            "doubles on a ground ball ": "ab_result=double, event_type=hit, batted_type=groundball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=doubles on a ground ball",
            "doubles on a fly ball ": "ab_result=double, event_type=hit, batted_type=flyball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=doubles on a fly ball",
            "doubles on a line drive ": "ab_result=double, event_type=hit, batted_type=linedrive, outs_recorded=0, is_pa=true, is_ab=true, ab_description=doubles on a line drive",

            # Triples
            "triples on a hard ground ball ": "ab_result=triple, event_type=hit, batted_type=groundball, contact_quality=hard, outs_recorded=0, is_pa=true, is_ab=true, ab_description=triples on a hard ground ball",
            "triples on a fly ball ": "ab_result=triple, event_type=hit, batted_type=flyball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=triples on a fly ball",
            "triples on a line drive ": "ab_result=triple, event_type=hit, batted_type=linedrive, outs_recorded=0, is_pa=true, is_ab=true, ab_description=triples on a line drive",

            # Home runs
            "hits an inside the park home run on a hard ground ball ": "ab_result=homerun, event_type=hit, batted_type=groundball, contact_quality=hard, outs_recorded=0, is_pa=true, is_ab=true, ab_description=hits an inside the park home run on a hard ground ball",
            "hits an inside the park home run on a fly ball ": "ab_result=homerun, event_type=hit, batted_type=flyball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=hits an inside the park home run on a fly ball",
            "homers on a fly ball ": "ab_result=homerun, event_type=hit, batted_type=flyball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=homers on a fly ball",

            # Walk / HBP
            "is hit by pitch ": "ab_result=hit_by_pitch, event_type=hbp, outs_recorded=0, is_pa=true, is_ab=false, ab_description=is hit by pitch",
            "walks ": "ab_result=walk, event_type=walk, outs_recorded=0, is_pa=true, is_ab=false, ab_description=walks",

            # Reaches on error
            "hits a hard ground ball and reaches on an error ": "ab_result=reaches_on_error, event_type=error, batted_type=groundball, contact_quality=hard, outs_recorded=0, is_pa=true, is_ab=true, ab_description=hits a hard ground ball and reaches on an error",
            "hits a ground ball and reaches on an error ": "ab_result=reaches_on_error, event_type=error, batted_type=groundball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=hits a ground ball and reaches on an error",
            "hits a line drive and reaches on an error ": "ab_result=reaches_on_error, event_type=error, batted_type=linedrive, outs_recorded=0, is_pa=true, is_ab=true, ab_description=hits a line drive and reaches on an error",
            "hits a fly ball and reaches on an error ": "ab_result=reaches_on_error, event_type=error, batted_type=flyball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=hits a fly ball and reaches on an error",

            # Dropped‐third strikes where batter reaches
            "reaches on dropped 3rd strike (passed ball) ": "ab_result=strikeout_dropped_third_strike, event_type=strikeout, pitch_type=passed_ball, outs_recorded=0, is_pa=true, is_ab=true, ab_description=reaches on dropped 3rd strike (passed ball)",
            "reaches on dropped 3rd strike (wild pitch) ": "ab_result=strikeout_dropped_third_strike, event_type=strikeout, pitch_type=wild_pitch, outs_recorded=0, is_pa=true, is_ab=true, ab_description=reaches on dropped 3rd strike (wild pitch)",

            # Strikeouts
            "strikes out swinging ": "ab_result=strikeout_swinging, event_type=strikeout, outs_recorded=1, is_pa=true, is_ab=true, ab_description=strikes out swinging",
            "strikes out looking ": "ab_result=strikeout_looking, event_type=strikeout, outs_recorded=1, is_pa=true, is_ab=true, ab_description=strikes out looking",
            "out at first on dropped 3rd strike ": "ab_result=strikeout_dropped_third, event_type=strikeout, outs_recorded=1, is_pa=true, is_ab=true, ab_description=out at first on dropped 3rd strike",
            "is out on foul tip ": "ab_result=strikeout_foul_tip, event_type=strikeout, outs_recorded=1, is_pa=true, is_ab=true, ab_description=is out on foul tip",

            # Outs – more specific first
            "flies out in foul territory ": "ab_result=flyout, event_type=out, batted_type=flyball, in_play=foul, outs_recorded=1, is_pa=true, is_ab=true, ab_description=flies out in foul territory",
            "pops into a double play ": "ab_result=double_play, event_type=out, batted_type=popup, outs_recorded=2, is_pa=true, is_ab=true, ab_description=pops into a double play",
            "grounds into fielder's choice double play ": "ab_result=double_play, event_type=out, batted_type=groundball, outs_recorded=2, is_pa=true, is_ab=true, ab_description=grounds into fielder's choice double play",
            "grounds into a double play ": "ab_result=double_play, event_type=out, batted_type=groundball, outs_recorded=2, is_pa=true, is_ab=true, ab_description=grounds into a double play",
            "lines into a double play ": "ab_result=double_play, event_type=out, batted_type=linedrive, outs_recorded=2, is_pa=true, is_ab=true, ab_description=lines into a double play",
            "grounds into fielder's choice ": "ab_result=fielder_choice, event_type=out, batted_type=groundball, outs_recorded=1, is_pa=true, is_ab=true, ab_description=grounds into fielder's choice",
            "out on sacrifice fly ": "ab_result=sacrifice_fly, event_type=sacrifice, batted_type=flyball, outs_recorded=1, is_pa=true, is_ab=false, ab_description=out on sacrifice fly",
            "out on infield fly ": "ab_result=infield_fly, event_type=out, batted_type=popup, outs_recorded=1, is_pa=true, is_ab=true, ab_description=out on infield fly",
            "grounds out ": "ab_result=groundout, event_type=out, batted_type=groundball, outs_recorded=1, is_pa=true, is_ab=true, ab_description=grounds out",
            "flies out ": "ab_result=flyout, event_type=out, batted_type=flyball, outs_recorded=1, is_pa=true, is_ab=true, ab_description=flies out",
            "lines out ": "ab_result=lineout, event_type=out, batted_type=linedrive, outs_recorded=1, is_pa=true, is_ab=true, ab_description=lines out",
            "pops out ": "ab_result=popout, event_type=out, batted_type=popup, outs_recorded=1, is_pa=true, is_ab=true, ab_description=pops out",
            "out (other) ": "ab_result=out_other, event_type=out, outs_recorded=1, is_pa=true, is_ab=true, ab_description=out (other)",

            # Sacrifice bunt (generic “sacrifices ” wording)
            "sacrifices ": "ab_result=sacrifice_bunt, event_type=sacrifice, batted_type=bunt, outs_recorded=1, is_pa=true, is_ab=false, ab_description=sacrifices",

            # Hit-location tags (no collision risk but included for completeness)
            "by center fielder": "hit_loc=8",
            "to center fielder": "hit_loc=8",
            "by right fielder": "hit_loc=9",
            "to right fielder": "hit_loc=9",
            "by left fielder": "hit_loc=7",
            "to left fielder": "hit_loc=7",
            "by shortstop": "hit_loc=6",
            "to shortstop": "hit_loc=6",
            "by third baseman": "hit_loc=5",
            "to third baseman": "hit_loc=5",
            "by second baseman": "hit_loc=4",
            "to second baseman": "hit_loc=4",
            "by first baseman": "hit_loc=3",
            "to first baseman": "hit_loc=3",
            "by catcher": "hit_loc=2",
            "to catcher": "hit_loc=2",
            "by pitcher": "hit_loc=1",
            "to pitcher": "hit_loc=1",
        }.items(),
        key=lambda kv: len(kv[0]),
        reverse=True
    )
)


import re
from pathlib import Path
import yaml
from functools import lru_cache

@lru_cache(maxsize=1)
def load_ab_event_map(fp: str | Path = "ab_event_mapping.yaml") -> dict[str, str]:
    raw = yaml.safe_load(Path(fp).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{fp!r} must contain a top-level mapping")

    # Flatten multiline replacements
    flat = {
        k: " ".join(v.splitlines()).strip().replace("  ", " ")
        for k, v in raw.items()
    }

    return dict(sorted(flat.items(), key=lambda kv: len(kv[0]), reverse=True))


# def tag_ab_events(text: str) -> str:
#     mapping = load_ab_event_map()
#     updated_lines = []

#     for line in text.splitlines():
#         for phrase, replacement in mapping.items():
#             if phrase in line:
#                 line = line.replace(phrase, replacement)
#         updated_lines.append(line)
#     return "\n".join(updated_lines)

def clean_spacing(text: str) -> str:
    text = re.sub(r'\s+,', ',', text)       # remove space before commas
    text = re.sub(r',\s+', ', ', text)      # normalize comma spacing
    text = re.sub(r'\s{2,}', ' ', text)     # collapse multiple spaces
    return text.strip()

import re

def tag_ab_events(text: str) -> str:
    mapping = load_ab_event_map()
    out_lines = []

    for line in text.splitlines():
        if "ab_raw=" not in line:
            out_lines.append(clean_spacing(line))
            continue

        # Extract ab_raw value
        match = re.search(r"ab_raw=([^,]+)", line)
        if not match:
            out_lines.append(clean_spacing(line))
            continue

        raw_val = match.group(1).strip()

        # Replace using mapping
        tagged = raw_val
        for phrase, replacement in mapping.items():
            if phrase in tagged:
                tagged = tagged.replace(phrase, replacement + " ")

        # Remove ab_raw=... from the line
        line = re.sub(r",?\s*ab_raw=[^,]+", "", line)

        # Insert tagged data at end
        line = f"{line}, {clean_spacing(tagged)}"
        out_lines.append(clean_spacing(line))

    return "\n".join(out_lines)


def tag_admin_events(text):
    pass

import re

import re

import re

import re

import re

import re

def tag_pitchers(text: str) -> str:
    sub_pattern = re.compile(r"Lineup changed: (player_\w{7}) in at pitcher")
    pitching_pattern = re.compile(r"(player_\w{7}) pitching")
    pitcher_tagged_pattern = re.compile(r"pitcher=player_\w{7}")
    inning_pattern = re.compile(r"entry=inning, half=(top|bottom), number=(\d+)")

    top_pitcher = None
    bottom_pitcher = None
    current_half = None
    result = []

    for line in text.splitlines():
        # Detect inning line and capture current half
        inning_match = inning_pattern.match(line)
        if inning_match:
            current_half = inning_match.group(1)  # 'top' or 'bottom'

        # Detect substitution and remove it
        sub_match = sub_pattern.search(line)
        if sub_match:
            pitcher = sub_match.group(1)
            if current_half == "top":
                top_pitcher = pitcher
            elif current_half == "bottom":
                bottom_pitcher = pitcher
            line = sub_pattern.sub("", line).strip(", ").strip()

        # Detect inline 'pitching'
        pitch_match = pitching_pattern.search(line)
        if pitch_match:
            pitcher = pitch_match.group(1)
            if current_half == "top":
                top_pitcher = pitcher
            elif current_half == "bottom":
                bottom_pitcher = pitcher

        # Tag only atbat_outcome lines
        if line.startswith("entry=atbat_outcome") and not pitcher_tagged_pattern.search(line):
            if current_half == "top":
                line += f", pitcher={top_pitcher or 'unknown'}"
            elif current_half == "bottom":
                line += f", pitcher={bottom_pitcher or 'unknown'}"

        result.append(line)

    return "\n".join(result)










def deduplicate_atbat_events(text: str) -> str:
    return "\n".join(
        ", ".join(
            dict.fromkeys(
                part.strip() for part in line.split(",")
            )
        )
        for line in text.splitlines()
    )



# def delete_duplicate_events(text: str) -> str:
#     cleaned_lines = []

#     for line in text.splitlines():
#         parts = (part.strip() for part in line.split(","))
#         unique = dict.fromkeys(parts)          # keeps first-seen order
#         cleaned_lines.append(", ".join(unique))

#     return "\n".join(cleaned_lines)





def fix_location_formatting(text: str) -> str:
    pattern = re.compile(
        r"(ab_raw=[^,]+),\s*"
        r"(?P<pos>pitcher|catcher|first baseman|second baseman|"
        r"third baseman|shortstop|left fielder|center fielder|right fielder)"
        r"([^.,]*)"
    )

    def repl(m: re.Match) -> str:
        return f"{m.group(1)} to {m.group('pos')}{m.group(3)}"

    lines = text.splitlines()
    out = []
    for line in lines:
        # only run on lines with raw, unprocessed event description
        if "ab_raw=" in line:
            line = pattern.sub(repl, line)
        out.append(line)

    return "\n".join(out)


def find_single(text):
    pattern = re.compile(r"singles on a fly ball(?! to)")
    matches = [line for line in text.splitlines() if pattern.search(line)]
    return set(matches)


POS_MAP = {
    "pitcher": "1", "catcher": "2", "first baseman": "3",
    "second baseman": "4", "third baseman": "5", "shortstop": "6",
    "left fielder": "7", "center fielder": "8", "right fielder": "9"
}

pattern_field = re.compile(
    r"\b(?P<pos1>pitcher|catcher|first baseman|second baseman|third baseman|shortstop|"
    r"left fielder|center fielder|right fielder) player_\w+ to (?P<pos2>pitcher|catcher|"
    r"first baseman|second baseman|third baseman|shortstop|left fielder|center fielder|"
    r"right fielder) player_\w+"
)

def replace_fielding(text: str) -> str:
    def repl(m):
        p1 = POS_MAP[m.group("pos1")]
        p2 = POS_MAP[m.group("pos2")]
        return f"fielding={p1}-{p2}"
    
    return pattern_field.sub(repl, text)

import re

# MLB position number mapping
POSITION_MAP = {
    "pitcher": "1",
    "catcher": "2",
    "first baseman": "3",
    "second baseman": "4",
    "third baseman": "5",
    "shortstop": "6",
    "left fielder": "7",
    "center fielder": "8",
    "right fielder": "9"
}

# ----------- Hit Location Only -----------

# Matches: "to shortstop player_xxxxxx" → hit location only (not a throw)
hit_loc_pattern = re.compile(
    r" to (?P<pos>pitcher|catcher|first baseman|second baseman|third baseman|shortstop|left fielder|center fielder|right fielder)"
    r"(?: player_\w{7})?"
)

def tag_hit_location_only(text: str) -> str:
    def replacer(match):
        pos = match.group("pos")
        return f", hit_loc={POSITION_MAP[pos]}"
    return "\n".join(hit_loc_pattern.sub(replacer, line) for line in text.splitlines())


# ----------- Fielder Sequence -----------

# Matches fielder throw chains: "shortstop to first baseman"
field_pattern = re.compile(
    r", (?P<chain>(?:(?:pitcher|catcher|first baseman|second baseman|third baseman|shortstop|left fielder|center fielder|right fielder)"
    r"(?: player_\w{7})? to )+"
    r"(?:pitcher|catcher|first baseman|second baseman|third baseman|shortstop|left fielder|center fielder|right fielder)"
    r"(?: player_\w{7})?)"
)

def tag_fielding_sequence(text: str) -> str:
    def replacer(match):
        raw = match.group("chain")
        fielders = re.findall(
            r"(pitcher|catcher|first baseman|second baseman|third baseman|shortstop|left fielder|center fielder|right fielder)",
            raw
        )
        if not fielders:
            return match.group(0)
        hit_loc = POSITION_MAP[fielders[0]]
        fielder_seq = "-".join(POSITION_MAP[f] for f in fielders)
        return f", hit_loc={hit_loc}, fielder_sequence={fielder_seq}"
    return "\n".join(field_pattern.sub(replacer, line) for line in text.splitlines())


# ----------- Combo Wrapper (optional) -----------

def tag_all_fielding(text: str) -> str:
    text = tag_fielding_sequence(text)
    text = tag_hit_location_only(text)
    return text






def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()
    full_text_filepath = Path(__file__).resolve().parents[2] / "full_sample.txt"
    full_text = full_text_filepath.read_text()

    metadata = Extractor(text).extract()

    data = mapper(metadata)

    new_text = replacer(text, data)
    keys = deduplicate_atbat_events(new_text)
    u_text = rewriter(keys)
    n_text = add_abid(u_text)
    t = pitch_counter(n_text)
    y = tag_pitchers(t)
    b = tag_batter(y)
    c = tag_outcome(b)
    d = in_play(c)
    # pos = find_positions(d)
    # out = get_outcome(d)
    h = tag_all_fielding(d)
    #h = fix_location_formatting(d)
    #j = replace_fielding(h)
    ii = tag_ab_events(h)
    print(ii)

    # print(h)
    # for o in out:
    #     print(o)
    # singles = find_single(full_text)
    # for single in singles:
    #     print(single)


if __name__ == "__main__":
    main()

# TODO:
# failing to tag up phrase fix
# need to fix hit_loc, replacing fielding positions involved in fielding plays