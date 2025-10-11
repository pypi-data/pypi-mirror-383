"""
MToast
"""

from typing import ClassVar

from qtpy import QtCore, QtGui, QtWidgets

from .avatar import MAvatar
from .label import MLabel
from .loading import MLoading
from .qt import MPixmap
from .theme import MTheme


class MToast(QtWidgets.QWidget):
    """
    MToast
    A Phone style message.
    """

    InfoType = "info"
    SuccessType = "success"
    WarningType = "warning"
    ErrorType = "error"
    LoadingType = "loading"

    default_config: ClassVar[dict[str, int]] = {
        "duration": 2,
    }

    sig_closed = QtCore.Signal()

    def __init__(
        self,
        text: str,
        duration: int | None = None,
        dayu_type: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.Dialog
        )
        # self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)

        _icon_lay = QtWidgets.QHBoxLayout()
        _icon_lay.addStretch()

        if dayu_type == MToast.LoadingType:
            _icon_lay.addWidget(
                MLoading(size=MTheme().huge, color=MTheme().text_color_inverse)
            )
        else:
            _icon_label = MAvatar()
            _icon_label.set_dayu_size(MTheme().toast_icon_size)
            _icon_label.set_dayu_image(
                MPixmap(
                    f"{dayu_type or MToast.InfoType}_line.svg",
                    MTheme().text_color_inverse,
                )
            )
            _icon_lay.addWidget(_icon_label)
        _icon_lay.addStretch()

        _content_label = MLabel()
        _content_label.setText(text)
        _content_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        _main_lay = QtWidgets.QVBoxLayout()
        _main_lay.setContentsMargins(0, 0, 0, 0)
        _main_lay.addStretch()
        _main_lay.addLayout(_icon_lay)
        _main_lay.addSpacing(10)
        _main_lay.addWidget(_content_label)
        _main_lay.addStretch()
        self.setLayout(_main_lay)
        self.setFixedSize(QtCore.QSize(MTheme().toast_size, MTheme().toast_size))

        _close_timer = QtCore.QTimer(self)
        _close_timer.setSingleShot(True)
        _close_timer.timeout.connect(self.close)
        _close_timer.timeout.connect(self.sig_closed)
        _close_timer.setInterval((duration or self.default_config["duration"]) * 1000)
        self.has_played = False

        if dayu_type != MToast.LoadingType:
            _close_timer.start()

        self._opacity_ani = QtCore.QPropertyAnimation()
        self._opacity_ani.setTargetObject(self)
        self._opacity_ani.setDuration(300)
        self._opacity_ani.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        self._opacity_ani.setPropertyName(b"windowOpacity")
        self._opacity_ani.setStartValue(0.0)
        self._opacity_ani.setEndValue(0.9)

        self._get_center_position(parent)
        self._fade_int()

    def closeEvent(self, event: QtGui.QCloseEvent):  # noqa: N802
        if self.has_played:
            event.accept()
        else:
            self._fade_out()
            event.ignore()

    def _fade_out(self) -> None:
        self.has_played = True
        self._opacity_ani.setDirection(QtCore.QAbstractAnimation.Direction.Backward)
        self._opacity_ani.finished.connect(self.close)
        self._opacity_ani.start()

    def _fade_int(self) -> None:
        self._opacity_ani.start()

    def _get_center_position(self, parent: QtWidgets.QWidget | None) -> None:
        if parent is None:
            return
        parent_geo = parent.geometry()
        pos = parent.mapToGlobal(parent_geo.topLeft())
        offset = 0
        for child in parent.children():
            if isinstance(child, MToast) and child.isVisible():
                offset = max(offset, child.y())
        target_x = pos.x() + parent_geo.width() / 2 - self.width() / 2
        target_y = pos.y() + parent_geo.height() / 2 - self.height() / 2
        self.setProperty("pos", QtCore.QPoint(int(target_x), int(target_y)))

    @classmethod
    def info(cls, text: str, parent: QtWidgets.QWidget, duration: int | None = None):
        """Show a normal toast message"""
        inst = cls(text, duration=duration, dayu_type=MToast.InfoType, parent=parent)
        inst.show()
        return inst

    @classmethod
    def success(cls, text: str, parent: QtWidgets.QWidget, duration: int | None = None):
        """Show a success toast message"""
        inst = cls(text, duration=duration, dayu_type=MToast.SuccessType, parent=parent)
        inst.show()
        return inst

    @classmethod
    def warning(cls, text: str, parent: QtWidgets.QWidget, duration: int | None = None):
        """Show a warning toast message"""
        inst = cls(text, duration=duration, dayu_type=MToast.WarningType, parent=parent)
        inst.show()
        return inst

    @classmethod
    def error(cls, text: str, parent: QtWidgets.QWidget, duration: int | None = None):
        """Show an error toast message"""
        inst = cls(text, duration=duration, dayu_type=MToast.ErrorType, parent=parent)
        inst.show()
        return inst

    @classmethod
    def loading(cls, text: str, parent: QtWidgets.QWidget):
        """Show a toast message with loading animation.
        You should close this widget by yourself."""
        inst = cls(text, dayu_type=MToast.LoadingType, parent=parent)
        inst.show()
        return inst

    @classmethod
    def config(cls, duration: int | None = None):
        """
        Config the global MToast duration setting.
        :param duration: int (unit is second)
        :return: None
        """
        if duration is not None:
            cls.default_config["duration"] = duration
