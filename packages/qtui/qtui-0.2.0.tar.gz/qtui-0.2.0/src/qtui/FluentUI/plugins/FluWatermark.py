# pyright: reportRedeclaration=none, reportArgumentType=none
# ruff: noqa: N815 N802

from PySide6.QtCore import Property, QPoint, QRectF, Signal
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter
from PySide6.QtQuick import QQuickPaintedItem

from .FluTextStyle import FluTextStyle


# noinspection PyCallingNonCallable,PyPropertyAccess,PyPep8Naming
class FluWatermark(QQuickPaintedItem):
    textChanged = Signal()
    gapChanged = Signal()
    offsetChanged = Signal()
    textColorChanged = Signal()
    rotateChanged = Signal()
    textSizeChanged = Signal()

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        self._text: str = ""
        self._gap: QPoint = QPoint(100, 100)
        self._offset: QPoint = QPoint(self._gap.x() // 2, self._gap.y() // 2)
        self._textColor: QColor = QColor(222, 222, 222, 222)
        self._rotate: int = 22
        self._textSize: int = 16
        self.textColorChanged.connect(lambda: self.update())
        self.gapChanged.connect(lambda: self.update())
        self.offsetChanged.connect(lambda: self.update())
        self.textChanged.connect(lambda: self.update())
        self.rotateChanged.connect(lambda: self.update())
        self.textSizeChanged.connect(lambda: self.update())

    @Property(str, notify=textChanged)
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self.textChanged.emit()

    @Property(QPoint, notify=gapChanged)
    def gap(self):
        return self._gap

    @gap.setter
    def gap(self, value: QPoint):
        self._gap = value
        self.gapChanged.emit()

    @Property(QPoint, notify=offsetChanged)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value: QPoint):
        self._offset = value
        self.offsetChanged.emit()

    @Property(QColor, notify=textColorChanged)
    def textColor(self):
        return self._textColor

    @textColor.setter
    def textColor(self, value: QColor):
        self._textColor = value
        self.textColorChanged.emit()

    @Property(int, notify=rotateChanged)
    def rotate(self):
        return self._rotate

    @rotate.setter
    def rotate(self, value: int):
        self._rotate = value
        self.rotateChanged.emit()

    @Property(int, notify=textSizeChanged)
    def textSize(self):
        return self._textSize

    @textSize.setter
    def textSize(self, value: int):
        self._textSize = value
        self.textSizeChanged.emit()

    def paint(self, painter: QPainter):
        font = QFont()
        font.setFamily(FluTextStyle().family)
        font.setPixelSize(self._textSize)
        painter.setFont(font)
        painter.setPen(self._textColor)
        font_metrics = QFontMetricsF(font)
        font_width = font_metrics.horizontalAdvance(self._text)
        font_height = font_metrics.height()
        step_x = font_width + self._gap.x()
        step_y = font_height + self._gap.y()
        row_count = int(self.width() / step_x) + 1
        col_count = int(self.height() / step_y) + 1
        for r in range(row_count):
            for c in range(col_count):
                center_x = step_x * r + self._offset.x() + font_width / 2.0
                center_y = step_y * c + self._offset.y() + font_height / 2.0
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(self._rotate)
                painter.drawText(
                    QRectF(
                        -font_width / 2.0, -font_height / 2.0, font_width, font_height
                    ),
                    self._text,
                )
                painter.restore()
