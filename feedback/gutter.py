"""Gutter (margin) warning icons for the editor."""


class GutterData:
    """Stores per-line gutter annotations."""

    def __init__(self):
        self._annotations = {}  # line_number -> {"icon": str, "label": str, "prob": float}

    def set_annotation(self, line: int, icon: str, label: str, probability: float, tooltip: str = ""):
        self._annotations[line] = {
            "icon": icon,
            "label": label,
            "probability": probability,
            "tooltip": tooltip,
        }

    def get_annotation(self, line: int):
        return self._annotations.get(line)

    def clear(self):
        self._annotations.clear()

    def clear_range(self, start: int, end: int):
        for line in range(start, end + 1):
            self._annotations.pop(line, None)

    @property
    def all_annotations(self):
        return dict(self._annotations)
