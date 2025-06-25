import re


def tag_batter_id(text: str) -> str:
    """Replace the first player ID in each outcome line with batter=player_xxxxxxx."""
    lines = text.splitlines()
    player_pattern = re.compile(r"(?P<batter>player_[a-z]{7})")
    result = []

    for line in lines:
        if line.startswith("entry=atbat_outcome"):
            match = player_pattern.search(line)
            batter = match.group("batter") if match else "none"
            result.append(line.replace(batter, f"batter={batter}"))
        else:
            result.append(line)

    return "\n".join(result)


def tag_ab_raw_outcome(text: str) -> str:
    """Extract raw outcome text after batter ID and tag it as ab_raw=..."""
    lines = text.splitlines()
    pattern = re.compile(r"batter=player_[a-z]{7}(?P<outcome>.*?)[,.]")
    result = []

    for line in lines:
        if line.startswith("entry=atbat_outcome"):
            match = pattern.search(line)
            outcome = match.group("outcome").strip() if match else "missing"
            result.append(line.replace(outcome, f", ab_raw={outcome}"))
        else:
            result.append(line)

    return "\n".join(result)


def tag_batted_ball_flag(text: str) -> str:
    """Replace 'In play' in atbat_events lines with outcome_type=battedball."""
    lines = text.splitlines()
    result = []

    for line in lines:
        if line.startswith("entry=atbat_events") and "In play" in line:
            result.append(line.replace("In play", "outcome_type=battedball"))
        else:
            result.append(line)

    return "\n".join(result)


def tag_pitch_count(text: str) -> str:
    """Count balls and strikes for each atbat_events line and add pitch_count=X-Y."""
    ball_pattern = re.compile(r"(?P<balls>, Ball [1-4])")
    strike_pattern = re.compile(r"(?P<strikes>, Strike [1-3]\b(?:\s+\w+)*)")
    foul_pattern = re.compile(r"(?P<fouls>, Foul)")
    result = []

    for line in text.splitlines():
        if not line.startswith("entry=atbat_events"):
            result.append(line)
            continue

        balls = strikes = fouls = 0
        for word in line.split(","):
            if word.startswith(" Ball"):
                balls += 1
            elif word.startswith(" Strike"):
                strikes += 1
            elif word.startswith(" Foul"):
                fouls += 1
                if strikes < 2:
                    strikes += 1

        count = f"{balls}-{strikes}"
        updated_line = line.replace(".", "")
        updated_line = ball_pattern.sub("", updated_line)
        updated_line = strike_pattern.sub("", updated_line)
        updated_line = foul_pattern.sub("", updated_line)
        result.append(f"{updated_line}, pitch_count={count}")

    return "\n".join(result)
