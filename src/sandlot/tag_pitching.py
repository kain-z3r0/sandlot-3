import re


def tag_pitchers(text: str) -> str:
    """Track pitcher substitutions and tag atbat_outcome lines with current pitcher ID."""

    # --- Patterns ---
    pattern_lineup_change = re.compile(r"Lineup changed: (player_\w{7}) in at pitcher")
    pattern_inline_pitching = re.compile(r"(player_\w{7}) pitching")
    pattern_pitcher_already_tagged = re.compile(r"pitcher=player_\w{7}")
    pattern_inning = re.compile(r"entry=inning, half=(top|bottom), number=(\d+)")

    # --- State Tracking ---
    top_pitcher = None
    bottom_pitcher = None
    current_half = None
    tagged_lines = []

    # --- Process Each Line ---
    for line in text.splitlines():
        # Identify inning half
        match_inning = pattern_inning.match(line)
        if match_inning:
            current_half = match_inning.group(1)  # 'top' or 'bottom'

        # Handle pitcher substitution line
        match_sub = pattern_lineup_change.search(line)
        if match_sub:
            pitcher = match_sub.group(1)
            if current_half == "top":
                top_pitcher = pitcher
            elif current_half == "bottom":
                bottom_pitcher = pitcher
            line = pattern_lineup_change.sub("", line).strip(", ").strip()

        # Handle inline pitching tag
        match_inline = pattern_inline_pitching.search(line)
        if match_inline:
            pitcher = match_inline.group(1)
            if current_half == "top":
                top_pitcher = pitcher
            elif current_half == "bottom":
                bottom_pitcher = pitcher

        # Apply pitcher tag if missing and line is an outcome
        if line.startswith("entry=atbat_outcome") and not pattern_pitcher_already_tagged.search(line):
            if current_half == "top":
                line += f", pitcher={top_pitcher or 'unknown'}"
            elif current_half == "bottom":
                line += f", pitcher={bottom_pitcher or 'unknown'}"

        tagged_lines.append(line)

    return "\n".join(tagged_lines)
