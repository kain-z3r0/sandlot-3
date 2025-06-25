import argparse
from pathlib import Path

from extractor import Extractor
from mapper import apply_tag_replacements, build_mapping
from rewriter import prepend_atbat_entry, remove_duplicate_tags_per_line
from tag_ab_events import replace_ab_raw_events
from tag_abid import insert_abids
from tag_batting import tag_ab_raw_outcome, tag_batted_ball_flag, tag_batter_id, tag_pitch_count
from tag_fielding import tag_all_fielding
from tag_pitching import tag_pitchers

# TODO: Detect and handle cases where a player reaches first base on a clean single,
#       then advances to additional bases due to a fielding error or misplay.
#       Ensure `ab_result=single` remains accurate, but tag the advancement separately.


def run_pipeline(raw_text: str) -> str:
    metadata = Extractor(raw_text).extract()
    entity_map = build_mapping(metadata)
    text = apply_tag_replacements(raw_text, entity_map)

    text = remove_duplicate_tags_per_line(text)
    text = prepend_atbat_entry(text)
    text = insert_abids(text)

    text = tag_pitch_count(text)
    text = tag_pitchers(text)

    text = tag_batter_id(text)
    text = tag_ab_raw_outcome(text)
    text = tag_batted_ball_flag(text)

    text = tag_all_fielding(text)
    text = replace_ab_raw_events(text)

    return text


def main():
    parser = argparse.ArgumentParser(description="Run text tagging pipeline")
    parser.add_argument(
        "--full", action="store_true", help="Use full_sample.txt instead of simple_sample.txt"
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[2]
    sample_file = "full_sample.txt" if args.full else "simple_sample.txt"
    input_path = base_dir / sample_file
    raw_text = input_path.read_text()

    result = run_pipeline(raw_text)
    print(result)


if __name__ == "__main__":
    main()
