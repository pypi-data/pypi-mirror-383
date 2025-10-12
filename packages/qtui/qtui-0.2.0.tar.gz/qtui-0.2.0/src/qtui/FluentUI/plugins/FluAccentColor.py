"""
The FluAccentColor class is responsible for displaying the color of the fluent accident
"""

# pyright: reportRedeclaration=none
# ruff: noqa: N815

from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtGui import QColor


# noinspection PyCallingNonCallable
class FluAccentColor(QObject):
    darkestChanged = Signal()
    darkerChanged = Signal()
    darkChanged = Signal()
    normalChanged = Signal()
    lightChanged = Signal()
    lighterChanged = Signal()
    lightestChanged = Signal()

    def __init__(self, parent: QObject | None = None):
        QObject.__init__(self, parent)
        self._darkest: QColor | None = None
        self._darker: QColor | None = None
        self._dark: QColor | None = None
        self._normal: QColor | None = None
        self._light: QColor | None = None
        self._lighter: QColor | None = None
        self._lightest: QColor | None = None

    @Property(QColor, notify=darkestChanged)
    def darkest(self) -> QColor | None:
        return self._darkest

    @darkest.setter
    def darkest(self, value: QColor | None):
        self._darkest = value
        self.darkestChanged.emit()

    @Property(QColor, notify=darkerChanged)
    def darker(self) -> QColor | None:
        return self._darker

    @darker.setter
    def darker(self, value: QColor | None):
        self._darker = value
        self.darkerChanged.emit()

    @Property(QColor, notify=darkChanged)
    def dark(self) -> QColor | None:
        return self._dark

    @dark.setter
    def dark(self, value: QColor | None):
        self._dark = value
        self.darkChanged.emit()

    @Property(QColor, notify=normalChanged)
    def normal(self) -> QColor | None:
        return self._normal

    @normal.setter
    def normal(self, value: QColor | None):
        self._normal = value
        self.normalChanged.emit()

    @Property(QColor, notify=lightChanged)
    def light(self) -> QColor | None:
        return self._light

    @light.setter
    def light(self, value: QColor | None):
        self._light = value
        self.lightChanged.emit()

    @Property(QColor, notify=lighterChanged)
    def lighter(self) -> QColor | None:
        return self._lighter

    @lighter.setter
    def lighter(self, value: QColor | None):
        self._lighter = value
        self.lighterChanged.emit()

    @Property(QColor, notify=lightestChanged)
    def lightest(self) -> QColor | None:
        return self._lightest

    @lightest.setter
    def lightest(self, value: QColor | None):
        self._lightest = value
        self.lightestChanged.emit()
