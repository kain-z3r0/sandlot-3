from pattern_handler import PatternHandler

def _inning_tagger(inning_info: str) -> str:
    half = PatternHandler("inning_half").search(inning_info).group("half").upper()
    num = PatternHandler("inning_num").search(inning_info).group("num")
    return f"type=inning,half={half},num={num},"


def _position_tagger(positions: str) -> str:
    pass