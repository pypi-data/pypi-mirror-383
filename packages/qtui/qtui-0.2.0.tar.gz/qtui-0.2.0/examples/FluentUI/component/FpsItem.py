# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from PySide6.QtCore import SIGNAL, SLOT, Property, Qt, QTimer, Signal
from PySide6.QtQuick import QQuickPaintedItem


# noinspection PyTypeChecker,PyPep8Naming
class FpsItem(QQuickPaintedItem):
    fpsChanged = Signal()

    @Property(int, notify=fpsChanged)
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int):
        self._fps = value
        self.fpsChanged.emit()

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        self._frameCount: int = 0
        self._fps: int = 0
        self._timer = QTimer()
        self.connect(self._timer, SIGNAL("timeout()"), self, SLOT("onTimeout()"))
        self.windowChanged.connect(lambda: self.onWindowChanged())
        self._timer.start(1000)

    def frameCountIncrease(self):
        self._frameCount += 1

    def onWindowChanged(self):
        if self.window():
            self.window().afterRendering.connect(
                lambda: self.frameCountIncrease(), Qt.ConnectionType.DirectConnection
            )

    def onTimeout(self):
        self.fps = self._frameCount  # pyright: ignore[reportAttributeAccessIssue]
        self._frameCount = 0
