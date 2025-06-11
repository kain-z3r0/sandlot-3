from pattern_handler import PatternHandler
from pathlib import Path
import re


class Extractor:
    def __init__(self, text: str):
        self.text = text

    def extract_players(self) -> tuple[str, ...]:
        players = set(PatternHandler("players_ahead").findall(self.text))
        players.update(PatternHandler("players_behind").findall(self.text))
        return tuple(players)

    def extract_innings(self) -> tuple[str, ...]:
        return tuple(set(PatternHandler("inning_header").findall(self.text)))

    def extract_teams(self) -> tuple[str, ...]:
        return tuple(PatternHandler("team_info").findall(self.text))

    def extract_positions(self) -> tuple[str, ...]:
        pass

    def line_selector(self) -> tuple[str, ...]:
        return tuple(PatternHandler("filter").findall(self.text, re.MULTILINE))

    def extract(self) -> dict[str, tuple[str, ...]]:
        return {
            "players": self.extract_players(),
            "team_info": self.extract_teams(),
            "innings": self.extract_innings(),
            "filtered_lines": self.line_selector(),
            "positions": self.extract_positions()
        }


def rewriter(text: str) -> str:
    pass

def main():
    filepath = Path(__file__).resolve().parents[2] / "simple_sample.txt"

    text = filepath.read_text()
    info = Extractor(text).extract()
    for key, values in info.items():
        print(values)
    


if __name__ == "__main__":
    main()
