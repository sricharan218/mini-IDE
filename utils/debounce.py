"""Debounce utility using QTimer for delaying rapid-fire events."""

from PyQt6.QtCore import QTimer


class Debouncer:
    """Delays a callback until a specified interval has passed without new calls."""

    def __init__(self, delay_ms: int, callback):
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(callback)

    def trigger(self):
        """Reset the timer. The callback fires only after `delay_ms` of silence."""
        self._timer.stop()
        self._timer.start()

    def cancel(self):
        self._timer.stop()

    @property
    def is_active(self):
        return self._timer.isActive()
