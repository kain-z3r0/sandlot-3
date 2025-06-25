import re

# --- Position Constants ---

# Human-readable position labels
POSITIONS = {
    "pitcher", "catcher", "first baseman", "second baseman", "third baseman",
    "shortstop", "left fielder", "center fielder", "right fielder",
}

# MLB numeric position mapping
POSITION_MAP = {
    "pitcher": "1",
    "catcher": "2",
    "first baseman": "3",
    "second baseman": "4",
    "third baseman": "5",
    "shortstop": "6",
    "left fielder": "7",
    "center fielder": "8",
    "right fielder": "9",
}

# Compatibility alias
POS_MAP = POSITION_MAP


# --- Regex Patterns ---

# Handles simple throw sequences like: "shortstop player_abc123 to first baseman player_xyz789"
pattern_throw = re.compile(
    r"\b(?P<pos1>pitcher|catcher|first baseman|second baseman|third baseman|shortstop|"
    r"left fielder|center fielder|right fielder) player_\w+ to (?P<pos2>pitcher|catcher|"
    r"first baseman|second baseman|third baseman|shortstop|left fielder|center fielder|"
    r"right fielder) player_\w+"
)

# Handles compound fielding chains (e.g., "shortstop to second baseman to first baseman")
pattern_chain = re.compile(
    r", (?P<chain>(?:(?:pitcher|catcher|first baseman|second baseman|third baseman|shortstop|"
    r"left fielder|center fielder|right fielder)(?: player_\w{7})? to )+"
    r"(?:pitcher|catcher|first baseman|second baseman|third baseman|shortstop|left fielder|"
    r"center fielder|right fielder)(?: player_\w{7})?)"
)

# Handles standalone location: "to shortstop player_xxx"
pattern_hit_loc = re.compile(
    r" to (?P<pos>pitcher|catcher|first baseman|second baseman|third baseman|shortstop|"
    r"left fielder|center fielder|right fielder)(?: player_\w{7})?"
)


# --- Tagging Functions ---

def tag_hit_location_only(text: str) -> str:
    """Tag hit location (hit_loc=X) based on single position mentions like 'to shortstop'."""
    def replacer(match: re.Match) -> str:
        pos = match.group("pos")
        return f", hit_loc={POSITION_MAP[pos]}"
    return "\n".join(pattern_hit_loc.sub(replacer, line) for line in text.splitlines())


def tag_fielding_sequence(text: str) -> str:
    """Tag fielding chains with hit_loc=X and fielder_sequence=1-3-6, etc."""
    def replacer(match: re.Match) -> str:
        raw = match.group("chain")
        fielders = re.findall(
            r"(pitcher|catcher|first baseman|second baseman|third baseman|shortstop|"
            r"left fielder|center fielder|right fielder)",
            raw,
        )
        if not fielders:
            return match.group(0)
        hit_loc = POSITION_MAP[fielders[0]]
        fielder_seq = "-".join(POSITION_MAP[pos] for pos in fielders)
        return f", hit_loc={hit_loc}, fielder_sequence={fielder_seq}"
    return "\n".join(pattern_chain.sub(replacer, line) for line in text.splitlines())


def tag_all_fielding(text: str) -> str:
    """Apply both fielding chain and hit location tags to the text."""
    text = tag_fielding_sequence(text)
    text = tag_hit_location_only(text)
    return text


def replace_fielding_chain(text: str) -> str:
    """Replace 'pos1 to pos2' fielding throw with fielding=X-Y style tag."""
    def repl(m: re.Match) -> str:
        p1 = POS_MAP[m.group("pos1")]
        p2 = POS_MAP[m.group("pos2")]
        return f"fielding={p1}-{p2}"
    return pattern_throw.sub(repl, text)


def fix_ab_raw_location_phrase(text: str) -> str:
    """Patch unstructured ab_raw field to preserve 'to [position]' phrases."""
    pattern = re.compile(
        r"(ab_raw=[^,]+),\s*"
        r"(?P<pos>pitcher|catcher|first baseman|second baseman|third baseman|shortstop|"
        r"left fielder|center fielder|right fielder)([^.,]*)"
    )

    def repl(m: re.Match) -> str:
        return f"{m.group(1)} to {m.group('pos')}{m.group(3)}"

    lines = text.splitlines()
    return "\n".join(
        pattern.sub(repl, line) if "ab_raw=" in line else line
        for line in lines
    )
