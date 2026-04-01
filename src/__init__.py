"""Kitsune — a white fox desktop pet."""
# Only needed on Linux (KDE workaround)
if sys.platform != "win32":
    self._raise_timer = QTimer(self)
    self._raise_timer.timeout.connect(self.raise_)
    self._raise_timer.start(500)
else:
    self._raise_timer = None