"""
The FluCaptcha class
"""

# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from random import randint

from PySide6.QtCore import Property, Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtQuick import QQuickPaintedItem


# noinspection PyPep8Naming
def _generaNumber(number: int) -> int:
    return randint(0, number - 1)


# noinspection PyCallingNonCallable,PyPep8Naming
class FluCaptcha(QQuickPaintedItem):
    fontChanged = Signal()
    ignoreCaseChanged = Signal()

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        self._ignoreCase: bool = True
        self._code = ""
        font_stype = QFont()
        font_stype.setPixelSize(28)
        font_stype.setBold(True)
        self._font = font_stype
        self.setWidth(180)
        self.setHeight(80)
        self.refresh()

    @Property(bool, notify=ignoreCaseChanged)
    def ignoreCase(self) -> bool:
        return self._ignoreCase

    @ignoreCase.setter
    def ignoreCase(self, value: bool):
        self._ignoreCase = value
        self.ignoreCaseChanged.emit()

    @Property(QFont, notify=fontChanged)
    def font(self) -> QFont:
        return self._font

    @font.setter
    def font(self, value: QFont):
        self._font = value
        self.fontChanged.emit()

    @Slot()
    def refresh(self):
        self._code = ""
        for _ in range(4):
            num = _generaNumber(3)
            if num == 0:
                self._code += str(_generaNumber(10))
            elif num == 1:
                temp = ord("A")
                self._code += chr(temp + _generaNumber(26))
            elif num == 2:
                temp = ord("a")
                self._code += chr(temp + _generaNumber(26))
        self.update()

    @Slot(str, result=bool)
    def verify(self, code: str) -> bool:
        if self._ignoreCase:
            return self._code.upper() == code.upper()
        return self._code == code

    def paint(self, painter: QPainter):
        painter.save()
        painter.fillRect(self.boundingRect().toRect(), QColor(255, 255, 255, 255))
        pen = QPen()
        painter.setFont(self._font)
        for _ in range(100):
            pen.setColor(
                QColor(_generaNumber(256), _generaNumber(256), _generaNumber(256))
            )
            painter.setPen(pen)
            painter.drawPoint(_generaNumber(180), _generaNumber(80))
        for _ in range(5):
            pen.setColor(
                QColor(_generaNumber(256), _generaNumber(256), _generaNumber(256))
            )
            painter.setPen(pen)
            painter.drawLine(
                _generaNumber(180),
                _generaNumber(80),
                _generaNumber(180),
                _generaNumber(80),
            )
        for i in range(4):
            pen.setColor(
                QColor(_generaNumber(255), _generaNumber(255), _generaNumber(255))
            )
            painter.setPen(pen)
            painter.drawText(
                15 + 35 * i,
                10 + _generaNumber(15),
                30,
                40,
                Qt.AlignmentFlag.AlignCenter,
                self._code[i],
            )
        painter.restore()
