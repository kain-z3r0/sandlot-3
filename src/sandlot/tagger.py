from pattern_handler import PatternHandler

def _build_inning_uid(inning: str) -> str:
    half = PatternHandler("inning_half").search(inning).group("half").upper()
    num = PatternHandler("inning_num").search(inning).group("num")
    return f"type=inning,half={half},num={num},"