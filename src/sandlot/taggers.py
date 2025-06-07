from extractors import inning_extractor
from pattern_handler import PatternHandler
from pathlib import Path

def inning_tagger(inning_info: str) -> str:
    half = PatternHandler("inning_half").search(inning_info).group("half").upper()
    num = PatternHandler("inning_num").search(inning_info).group("num")
    return f"type=inning,half={half},num={num},"

def position_tagger(positions: str) -> str:
    pass




def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"
    text = filepath.read_text()

    innings = inning_extractor(text)
    for inning in innings:
        print(_inning_tagger(inning))


if __name__ == "__main__":
    main()