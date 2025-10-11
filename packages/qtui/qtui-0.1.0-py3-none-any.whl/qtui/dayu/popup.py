# Import third-party modules
from qtpy import QtCore, QtGui, QtWidgets

from .mixin import hover_shadow_mixin, property_mixin
from .utils import str_to_qbytearray


@hover_shadow_mixin
@property_mixin
class MPopup(QtWidgets.QFrame):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowType.Popup)
        self.mouse_pos: QtCore.QPoint | None = None
        self.setProperty("movable", True)
        self.setProperty("animatable", True)
        QtCore.QTimer.singleShot(0, self.post_init)

        self._opacity_anim = QtCore.QPropertyAnimation(
            self, str_to_qbytearray("windowOpacity")
        )
        self.setProperty("anim_opacity_duration", 300)
        self.setProperty("anim_opacity_curve", "OutCubic")
        self.setProperty("anim_opacity_start", 0)
        self.setProperty("anim_opacity_end", 1)

        self._size_anim = QtCore.QPropertyAnimation(self, str_to_qbytearray("size"))
        self.setProperty("anim_size_duration", 300)
        self.setProperty("anim_size_curve", "OutCubic")
        self.setProperty("border_radius", 15)

    def post_init(self) -> None:
        start_size = self.property("anim_size_start")
        size = self.sizeHint()
        start_size = start_size if start_size else QtCore.QSize(0, size.height())
        end_size = self.property("anim_size_end")
        end_size = end_size if end_size else size
        self.setProperty("anim_size_start", start_size)
        self.setProperty("anim_size_end", end_size)

    def update_mask(self):
        rect_path = QtGui.QPainterPath()
        end_size = self.property("anim_size_end")
        rect = QtCore.QRectF(0, 0, end_size.width(), end_size.height())
        radius = self.property("border_radius")
        rect_path.addRoundedRect(rect, radius, radius)
        self.setMask(QtGui.QRegion(rect_path.toFillPolygon().toPolygon()))

    def _get_curve(self, value: str) -> QtCore.QEasingCurve.Type:
        curve = getattr(QtCore.QEasingCurve, value, None)
        if not curve:
            raise TypeError("Invalid QEasingCurve")
        return curve

    def _set_border_radius(self, value: int) -> None:
        QtCore.QTimer.singleShot(0, self.update_mask)

    def _set_anim_opacity_duration(self, value: int) -> None:
        self._opacity_anim.setDuration(value)

    def _set_anim_opacity_curve(self, value: str) -> None:
        self._opacity_anim.setEasingCurve(self._get_curve(value))

    def _set_anim_opacity_start(self, value: float) -> None:
        self._opacity_anim.setStartValue(value)

    def _set_anim_opacity_end(self, value: float) -> None:
        self._opacity_anim.setEndValue(value)

    def _set_anim_size_duration(self, value: int) -> None:
        self._size_anim.setDuration(value)

    def _set_anim_size_curve(self, value: str) -> None:
        self._size_anim.setEasingCurve(self._get_curve(value))

    def _set_anim_size_start(self, value: QtCore.QSize) -> None:
        self._size_anim.setStartValue(value)

    def _set_anim_size_end(self, value: QtCore.QSize) -> None:
        self._size_anim.setEndValue(value)
        QtCore.QTimer.singleShot(0, self.update_mask)

    def start_anim(self) -> None:
        self._size_anim.start()
        self._opacity_anim.start()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.mouse_pos = event.pos()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802
        self.mouse_pos = None
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:  # noqa: N802
        if (
            event.buttons() == QtCore.Qt.MouseButton.LeftButton
            and self.mouse_pos
            and self.property("movable")
        ):
            self.move(self.mapToGlobal(event.pos() - self.mouse_pos))
        return super().mouseMoveEvent(event)

    def show(self) -> None:
        if self.property("animatable"):
            self.start_anim()
        self.move(QtGui.QCursor.pos())
        super().show()
        self.activateWindow()
