from typing import Any

from qtpy import QtCore, QtWidgets

from .mixin import property_mixin
from .theme import MTheme
from .utils import str_to_qbytearray


@property_mixin  # pyright: ignore[reportArgumentType, reportUntypedClassDecorator]
class MCompleter(QtWidgets.QCompleter):
    ITEM_HEIGHT = 28

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setProperty("animatable", True)

        if not (popup := self.popup()):
            return

        MTheme().apply(popup)

        self._opacity_anim = QtCore.QPropertyAnimation(
            popup, str_to_qbytearray("windowOpacity")
        )
        self.setProperty("anim_opacity_duration", 300)
        self.setProperty("anim_opacity_curve", "OutCubic")
        self.setProperty("anim_opacity_start", 0)
        self.setProperty("anim_opacity_end", 1)

        self._size_anim = QtCore.QPropertyAnimation(popup, str_to_qbytearray("size"))
        self.setProperty("anim_size_duration", 300)
        self.setProperty("anim_size_curve", "OutCubic")

        popup.installEventFilter(self)

    def _set_anim_opacity_duration(self, value: int):
        self._opacity_anim.setDuration(value)

    def _set_anim_opacity_curve(self, value: str):
        curve = getattr(QtCore.QEasingCurve, value, None)
        assert curve, "invalid QEasingCurve"
        self._opacity_anim.setEasingCurve(curve)

    def _set_anim_opacity_start(self, value: Any):
        self._opacity_anim.setStartValue(value)

    def _set_anim_opacity_end(self, value: Any):
        self._opacity_anim.setEndValue(value)

    def _set_anim_size_duration(self, value: Any):
        self._size_anim.setDuration(value)

    def _set_anim_size_curve(self, value: str):
        curve = getattr(QtCore.QEasingCurve, value, None)
        assert curve, "invalid QEasingCurve"
        self._size_anim.setEasingCurve(curve)

    def _set_anim_size_start(self, value: Any):
        self._size_anim.setStartValue(value)

    def _set_anim_size_end(self, value: Any):
        self._size_anim.setEndValue(value)

    def init_size(self):
        if not (popup := self.popup()):
            return

        model = popup.model()

        width = self.widget().width()
        max_height = popup.sizeHint().height()
        item_height = model.data(model.index(0, 0), QtCore.Qt.ItemDataRole.SizeHintRole)
        height = (item_height or self.ITEM_HEIGHT) * model.rowCount()
        height = height if height < max_height else max_height

        start_size = self.property("anim_size_start")
        start_size = start_size if start_size else QtCore.QSize(0, 0)
        end_size = self.property("anim_size_end")
        end_size = end_size if end_size else QtCore.QSize(width, height)
        self._size_anim.setStartValue(start_size)
        self._size_anim.setEndValue(end_size)

    def start_anim(self):
        self.init_size()
        self._opacity_anim.start()
        self._size_anim.start()

    def eventFilter(self, widget: QtWidgets.QWidget, event: QtCore.QEvent):  # noqa: N802  # pyright: ignore[reportIncompatibleMethodOverride]
        if event.type() == QtCore.QEvent.Type.Show and self.property("animatable"):
            self.start_anim()
        return super().eventFilter(widget, event)
