def prepend_atbat_entry(text: str) -> str:
    """Insert 'entry=atbat,' prefix before lines that are not inning entries."""
    lines = text.splitlines()
    updated_lines = [
        f"entry=atbat, {line}" if not line.startswith("entry=inning") else line
        for line in lines
    ]
    return "\n".join(updated_lines)


def remove_duplicate_tags_per_line(text: str) -> str:
    """Remove duplicate comma-separated tags from each line, preserving order."""
    lines = text.splitlines()
    deduped_lines = [
        ", ".join(dict.fromkeys(part.strip() for part in line.split(",")))
        for line in lines
    ]
    return "\n".join(deduped_lines)
