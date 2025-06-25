from pathlib import Path

from extractor import Extractor
from mapper import build_mapping, apply_tag_replacements
from rewriter import remove_duplicate_tags_per_line, prepend_atbat_entry
from tag_abid import insert_abids
from tag_ab_events import replace_ab_raw_events
from tag_batting import tag_batter_id, tag_ab_raw_outcome, tag_batted_ball_flag, tag_pitch_count
from tag_fielding import tag_all_fielding
from tag_pitching import tag_pitchers
import argparse


def main():
    parser = argparse.ArgumentParser(description="Run text tagging pipeline")
    parser.add_argument("--full", action="store_true", help="Use full_sample.txt instead of simple_sample.txt")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[2]
    sample_file = "full_sample.txt" if args.full else "simple_sample.txt"
    input_path = base_dir / sample_file
    raw_text = input_path.read_text()

    # --- Metadata Extraction & Mapping ---
    metadata = Extractor(raw_text).extract()
    entity_map = build_mapping(metadata)
    text = apply_tag_replacements(raw_text, entity_map)

    # --- At-bat Structuring ---
    text = remove_duplicate_tags_per_line(text)
    text = prepend_atbat_entry(text)
    text = insert_abids(text)

    # --- Pitching Tagging ---
    text = tag_pitch_count(text)
    text = tag_pitchers(text)

    # --- Batting Tags ---
    text = tag_batter_id(text)
    text = tag_ab_raw_outcome(text)
    text = tag_batted_ball_flag(text)

    # --- Fielding Tags ---
    text = tag_all_fielding(text)

    # --- At-bat Outcome Tagging ---
    text = replace_ab_raw_events(text)

    print(text)

if __name__ == "__main__":
    main()