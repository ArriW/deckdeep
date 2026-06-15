"""Pure-stdlib helpers for fitting long display names into UI elements."""


_ELLIPSIS = "\u2026"


def truncate_name(name: str, max_len: int) -> str:
    """Return ``name`` shortened to at most ``max_len`` characters.

    - Names already at or below ``max_len`` are returned unchanged.
    - Longer names are trimmed to ``max_len - 1`` characters, stripped of
      trailing whitespace, and terminated with a single-character ellipsis.
    - ``max_len <= 1`` always yields just the ellipsis.
    """
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    if not isinstance(max_len, int) or isinstance(max_len, bool):
        raise TypeError("max_len must be an int")
    if max_len <= 1:
        return _ELLIPSIS
    if len(name) <= max_len:
        return name
    return name[: max_len - 1].rstrip() + _ELLIPSIS


def wrap_name(name: str, max_width: int) -> list:
    """Wrap ``name`` into lines that each fit within ``max_width`` characters.

    Behaviour:
    - Empty strings and whitespace-only input return ``[]``.
    - Runs of whitespace are collapsed to single spaces.
    - Words are packed greedily onto a line while they still fit.
    - A single word longer than ``max_width`` is hard-split into chunks of
      ``max_width`` characters.
    """
    if not isinstance(name, str):
        raise TypeError("name must be a str")
    if not isinstance(max_width, int) or isinstance(max_width, bool):
        raise TypeError("max_width must be an int")
    if max_width <= 0:
        raise ValueError("max_width must be positive")

    collapsed = " ".join(name.split())
    if not collapsed:
        return []

    words = collapsed.split(" ")
    lines: list = []
    current = ""
    for word in words:
        if len(word) <= max_width:
            candidate = word if not current else current + " " + word
            if len(candidate) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        else:
            if current:
                lines.append(current)
                current = ""
            for start in range(0, len(word), max_width):
                chunk = word[start : start + max_width]
                if len(chunk) == max_width:
                    lines.append(chunk)
                else:
                    current = chunk
    if current:
        lines.append(current)
    return lines
