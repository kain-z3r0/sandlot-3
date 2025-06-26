"""
base_state_engine.py
────────────────────
Walk a fully-tagged game log and emit a base–out snapshot for every
plate appearance (abid).  Each snapshot dict contains:

    abid            : plate-appearance ID
    before_bases    : "---", "1--", "-2-" … runner layout BEFORE PA
    before_outs     : outs before PA (0-2)
    after_bases     : layout AFTER all baserunning for that PA
    after_outs      : outs after PA (0-3)

You can extend the batter-result mapping (singles/double-plays etc.)
as your `ab_result` vocabulary grows.
"""

from __future__ import annotations
import re
from typing import Dict, List


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def _bases_str(bases: Dict[int, str | None]) -> str:
    """Return layout string like '1-3'."""
    return "".join(str(b) if bases[b] else "-" for b in (1, 2, 3))


OUT_BASERUN_EVENTS = {
    "out", "out_at", "out_on", "caught_stealing", "picked_off"
}


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def compute_baseout_states(lines: List[str]) -> List[Dict]:
    bases: Dict[int, str | None] = {1: None, 2: None, 3: None}
    outs: int = 0
    snaps: List[Dict] = []

    for line in lines:
        # ---------------- baserunning entries -----------------
        if line.startswith("entry=baserunning"):
            parts = dict(p.split("=", 1) for p in line.split(", ") if "=" in p)
            runner = parts["runner"]
            dest   = parts.get("dest_base")
            evt    = parts["event_type"]

            # remove runner from current base (if found)
            for b, r in bases.items():
                if r == runner:
                    bases[b] = None

            if evt in OUT_BASERUN_EVENTS:
                outs += 1
            else:
                if dest and dest != "4":        # 4 == scored
                    bases[int(dest)] = runner
            continue  # baserunning lines don’t trigger snapshots

        # ---------------- plate-appearance outcome lines -----------------
        if not line.startswith("entry=atbat_outcome"):
            continue

        abid_match = re.search(r"abid=(\d+)", line)
        if not abid_match:          # malformed line; skip
            continue
        abid = abid_match.group(1)

        # snapshot BEFORE PA changes
        snaps.append({
            "abid": abid,
            "before_bases": _bases_str(bases),
            "before_outs": outs
        })

        # ------ apply batter movement ------
        batter_match = re.search(r"batter=(player_[\w]+)", line)
        batter = batter_match.group(1) if batter_match else None
        if batter:
            # remove from bases if somehow already present
            for b in bases:
                if bases[b] == batter:
                    bases[b] = None

        # crude result mapping — extend to cover your full ab_result map
        if "walk" in line or "single" in line:
            bases[1] = batter
        elif "double" in line:
            bases[2] = batter
        elif "triple" in line:
            bases[3] = batter
        elif "home_run" in line or "homerun" in line or "ab_result=home_run" in line:
            # batter scores; clear bases after runners score elsewhere
            pass  # bases unchanged here; runners scoring handled via baserunning tags

        # outs from the PA itself
        outs_tag = re.search(r"outs_recorded=(\d)", line)
        if outs_tag:
            outs += int(outs_tag.group(1))

        # snapshot AFTER PA changes
        snaps[-1].update({
            "after_bases": _bases_str(bases),
            "after_outs": outs
        })

        # reset if half-inning over
        if outs >= 3:
            outs = 0
            bases = {1: None, 2: None, 3: None}

    return snaps
