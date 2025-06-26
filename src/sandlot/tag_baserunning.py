import re
from pathlib import Path

BASE_RE = r"(?:1st|2nd|3rd|home)"  # word forms; numeric already implied by ordinal

BASE_MAP = {
    "1st": "1", "2nd": "2", "3rd": "3",
    "home": "4", "home plate": "4", "plate": "4",
}

OUT_EVENT_TYPES = {"out", "out_at", "out_on", "caught_stealing", "picked_off"}


def _normalise_base(txt: str | None) -> str | None:
    if not txt:
        return None
    txt = txt.lower().strip().rstrip(".,")
    return BASE_MAP.get(txt, txt.lstrip("0"))


def tag_baserunning_events(text: str) -> str:
    """Detect baserunning phrases inside *both* at‑bat events & outcomes, create
    `entry=baserunning` lines, and scrub raw phrases to prevent duplicate logic.
    """

    # Helper to build patterns that allow trailing punctuation/comma
    def _p(body: str) -> re.Pattern:
        return re.compile(body + r"(?=[\s.,]|$)", re.I)

    patterns: list[tuple[str, re.Pattern]] = [
        ("steal",            _p(rf"(?P<runner>player_[\w]+) steals (?P<to_base>{BASE_RE})")),
        ("advance",          _p(rf"(?P<runner>player_[\w]+) advances to (?P<to_base>{BASE_RE})(?: on [^,\.]+)?")),
        ("score",            _p(r"(?P<runner>player_[\w]+) scores(?: on [^,\.]+)?")),
        ("remain",           _p(rf"(?P<runner>player_[\w]+) remains at (?P<base>{BASE_RE})")),
        ("held_up",          _p(rf"(?P<runner>player_[\w]+) held up at (?P<base>{BASE_RE})")),
        ("caught_stealing",  _p(rf"(?P<runner>player_[\w]+) caught stealing (?P<base>{BASE_RE})")),
        ("picked_off",       _p(rf"(?P<runner>player_[\w]+) picked off (?P<base>{BASE_RE})")),
        ("out_at",           _p(r"(?P<runner>player_[\w]+) out at (?P<location>[A-Za-z ]+)")),
        ("out_on",           _p(r"(?P<runner>player_[\w]+) out on (?P<reason>[^,.]+)")),
        ("out",              _p(r"(?P<runner>player_[\w]+) out")),
    ]

    cleaned_log: list[str] = []

    for line in text.splitlines():
        if not line.startswith("entry=atbat_"):
            cleaned_log.append(line)
            continue

        m_abid = re.search(r"abid=(\d+)", line)
        abid = m_abid.group(1) if m_abid else ""

        for evt, pat in patterns:
            for m in list(pat.finditer(line)):
                runner = m.group("runner")
                raw_to_base = m.groupdict().get("to_base") or m.groupdict().get("base")
                dest_base = _normalise_base(raw_to_base) or ("4" if evt == "score" else None)
                location = m.groupdict().get("location")
                reason = m.groupdict().get("reason")
                outs_recorded = 1 if evt in OUT_EVENT_TYPES else 0

                tag_parts = [
                    "entry=baserunning",
                    f"abid={abid}",
                    f"runner={runner}",
                    f"event_type={evt}",
                    f"outs_recorded={outs_recorded}",
                ]
                if dest_base:
                    tag_parts.append(f"dest_base={dest_base}")
                if location and evt == "out_at":
                    tag_parts.append(f"location={location.strip()}")
                if reason and evt == "out_on":
                    tag_parts.append(f"reason={reason.strip()}")

                cleaned_log.append(", ".join(tag_parts))

            # Remove phrase(s) from line
            line = pat.sub("", line)

        # Tidy whitespace & excess punctuation
        line = re.sub(r"\s{2,}", " ", line)
        line = re.sub(r",{2,}", ",", line)
        line = line.strip().strip(",")
        cleaned_log.append(line)

    return "\n".join(cleaned_log)


if __name__ == "__main__":
    sample_path = Path("tagger_output.txt")
    if sample_path.exists():
        print(tag_baserunning_events(sample_path.read_text()))
    else:
        print("tagger_output.txt not found – run pipeline first.")
