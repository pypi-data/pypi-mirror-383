import functools
from typing import cast

from qtpy import QtCore, QtGui, QtWidgets

from .mixin import property_mixin
from .theme import MTheme


class MGuidPrivate(QtWidgets.QFrame):
    go_to_page = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.set_checked(False)

    def set_checked(self, value: bool):
        self.setStyleSheet(
            f"background-color:"
            f"{MTheme().primary_color if value else MTheme().background_color}"
        )
        self.setFixedSize(20 if value else 16, 4)

    def mousePressEvent(self, event: QtGui.QMouseEvent):  # noqa: N802
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.go_to_page.emit()
        return super().mousePressEvent(event)


@property_mixin
class MCarousel(QtWidgets.QGraphicsView):
    def __init__(
        self,
        pix_list: list[QtGui.QPixmap],
        autoplay: bool = True,
        width: int = 500,
        height: int = 500,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)

        self._scene = QtWidgets.QGraphicsScene()
        self._scene.setBackgroundBrush(
            QtGui.QBrush(QtGui.QColor(MTheme().background_color))
        )
        self.setScene(self._scene)

        self.hor_bar = self.horizontalScrollBar()
        self.carousel_width = width
        self.carousel_height = height

        pos = QtCore.QPoint(0, 0)
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.red)
        pen.setWidth(5)
        self.page_count = len(pix_list)
        line_width = 20
        total_width = self.page_count * (line_width + 5)
        self.scene().setSceneRect(0, 0, self.page_count * width, height)

        self.navigate_layout = QtWidgets.QHBoxLayout()
        self.navigate_layout.setSpacing(5)
        target_size = min(width, height)
        for index, pix in enumerate(pix_list):
            if pix.width() > pix.height():
                new_pix = pix.scaledToWidth(
                    target_size, QtCore.Qt.TransformationMode.SmoothTransformation
                )
            else:
                new_pix = pix.scaledToHeight(
                    target_size, QtCore.Qt.TransformationMode.SmoothTransformation
                )
            pix_item = QtWidgets.QGraphicsPixmapItem(new_pix)
            pix_item.setPos(pos)
            pix_item.setTransformationMode(
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            pos.setX(pos.x() + width)
            line_item = MGuidPrivate()
            line_item.go_to_page.connect(functools.partial(self.go_to_page, index))
            self.navigate_layout.addWidget(line_item)
            self.scene().addItem(pix_item)

        hud_widget = QtWidgets.QWidget(self)
        hud_widget.setLayout(self.navigate_layout)
        hud_widget.setStyleSheet("background:transparent")
        hud_widget.move(int(width / 2 - total_width / 2), height - 30)

        self.setFixedWidth(width + 2)
        self.setFixedHeight(height + 2)

        self.loading_ani = QtCore.QPropertyAnimation()
        self.loading_ani.setTargetObject(self.hor_bar)
        self.loading_ani.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
        self.loading_ani.setDuration(500)
        self.loading_ani.setPropertyName(b"value")
        self.autoplay_timer = QtCore.QTimer(self)
        self.autoplay_timer.setInterval(2000)
        self.autoplay_timer.timeout.connect(self.next_page)

        self.current_index: int = 0
        self.go_to_page(0)
        self.set_autoplay(autoplay)

    def set_autoplay(self, value: bool):
        self.setProperty("autoplay", value)

    def _set_autoplay(self, value: bool):
        if value:
            self.autoplay_timer.start()
        else:
            self.autoplay_timer.stop()

    def set_interval(self, ms: int):
        self.autoplay_timer.setInterval(ms)

    def next_page(self):
        index = (
            self.current_index + 1 if self.current_index + 1 < self.page_count else 0
        )
        self.go_to_page(index)

    def pre_page(self):
        index = (
            self.current_index - 1 if self.current_index > 0 else self.page_count - 1
        )
        self.go_to_page(index)

    def go_to_page(self, index: int):
        self.loading_ani.setStartValue(self.current_index * self.carousel_width)
        self.loading_ani.setEndValue(index * self.carousel_width)
        self.loading_ani.start()
        self.current_index = index
        for i in range(self.navigate_layout.count()):
            frame = cast(MGuidPrivate, self.navigate_layout.itemAt(i).widget())
            frame.set_checked(i == self.current_index)
