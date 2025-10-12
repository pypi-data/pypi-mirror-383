# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from PySide6.QtCore import (
    SIGNAL,
    SLOT,
    Property,
    QEasingCurve,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QImage, QPainter, QPainterPath
from PySide6.QtQuick import QQuickItem, QQuickItemGrabResult, QQuickPaintedItem


# noinspection PyTypeChecker,PyPep8Naming
class CircularReveal(QQuickPaintedItem):
    radiusChanged = Signal()
    imageChanged = Signal()
    animationFinished = Signal()
    targetChanged = Signal()

    def __init__(self):
        QQuickPaintedItem.__init__(self)
        self._target: QQuickItem | None = None
        self._radius: int = 0
        self._source: QImage | None = None
        self._center: QPoint | None = None
        self._grabResult: QQuickItemGrabResult | None = None
        self.setVisible(False)
        self._anim = QPropertyAnimation(self, b"radius", self)
        self._anim.setDuration(333)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.connect(self._anim, SIGNAL("finished()"), self, SLOT("onAnimaFinish()"))
        self.radiusChanged.connect(lambda: self.update())
        self.destroyed.connect(lambda: self.release())

    def release(self):
        self._anim.deleteLater()
        del self._grabResult
        del self._source

    def onAnimaFinish(self):
        self.update()
        self.setVisible(False)
        self.animationFinished.emit()

    @Property(int, notify=radiusChanged)
    def radius(self) -> int:
        return self._radius

    @radius.setter
    def radius(self, value: int):
        self._radius = value
        self.radiusChanged.emit()

    @Property(QQuickItem, notify=targetChanged)
    def target(self) -> QQuickItem | None:
        return self._target

    @target.setter
    def target(self, value: QQuickItem):
        self._target = value
        self.targetChanged.emit()

    def paint(self, painter: QPainter):
        if self._source is None:
            return
        painter.save()
        painter.drawImage(
            QRect(
                0,
                0,
                int(self.boundingRect().width()),
                int(self.boundingRect().height()),
            ),
            self._source,
        )
        if self._center is None:
            return

        path = QPainterPath()
        path.moveTo(self._center.x(), self._center.y())
        path.addEllipse(
            QPointF(self._center.x(), self._center.y()), self._radius, self._radius
        )
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillPath(path, Qt.GlobalColor.black)
        painter.restore()

    @Slot()
    def handleGrabResult(self):
        if self._grabResult is None or self._source is None:
            return
        self._grabResult.image().swap(self._source)
        # self._grabResult.data().image().swap(self._source)
        self.update()
        self.setVisible(True)
        self.imageChanged.emit()
        self._anim.start()

    @Slot(int, int, QPoint, int)
    def start(self, w: int, h: int, center: QPoint, radius: int):
        if self._target is None:
            return
        self._anim.setStartValue(0)
        self._anim.setEndValue(radius)
        self._center = center
        self._grabResult = self._target.grabToImage(QSize(w, h)).data()
        # self._grabResult.data().ready.connect(self.handleGrabResult)
        self._grabResult.ready.connect(self.handleGrabResult)
