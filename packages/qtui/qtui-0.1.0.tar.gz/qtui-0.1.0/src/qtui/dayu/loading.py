"""
MLoading
"""

from qtpy import QtCore, QtGui, QtWidgets

from .qt import MPixmap
from .theme import MTheme


class MLoading(QtWidgets.QWidget):
    """
    Show a loading animation image.
    """

    def __init__(
        self,
        size: int | None = None,
        color: str | None = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        size = size or MTheme().default_size
        self.setFixedSize(QtCore.QSize(size, size))
        self.pix = MPixmap(
            "loading.svg", color or MTheme().primary_color
        ).scaledToWidth(size, QtCore.Qt.TransformationMode.SmoothTransformation)
        self._rotation: int = 0
        self._loading_ani = QtCore.QPropertyAnimation()
        self._loading_ani.setTargetObject(self)
        self._loading_ani.setDuration(1000)
        self._loading_ani.setPropertyName(b"rotation")
        self._loading_ani.setStartValue(0)
        self._loading_ani.setEndValue(360)
        self._loading_ani.setLoopCount(-1)
        self._loading_ani.start()

    def _set_rotation(self, value: int):
        self._rotation = value
        self.update()

    def _get_rotation(self) -> int:
        return self._rotation

    rotation = QtCore.Property(int, _get_rotation, _set_rotation)

    def paintEvent(self, event: QtGui.QPaintEvent):  # noqa: N802
        """override the paint event to paint the 1/4 circle image."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.translate(int(self.pix.width() / 2), int(self.pix.height() / 2))
        painter.rotate(self._rotation)
        painter.drawPixmap(
            int(-self.pix.width() / 2),
            int(-self.pix.height() / 2),
            self.pix.width(),
            self.pix.height(),
            self.pix,
        )
        painter.end()
        return super().paintEvent(event)

    @classmethod
    def huge(cls, color: str | None = None):
        """Create a MLoading with huge size"""
        return cls(MTheme().huge, color)

    @classmethod
    def large(cls, color: str | None = None):
        """Create a MLoading with large size"""
        return cls(MTheme().large, color)

    @classmethod
    def medium(cls, color: str | None = None):
        """Create a MLoading with medium size"""
        return cls(MTheme().medium, color)

    @classmethod
    def small(cls, color: str | None = None):
        """Create a MLoading with small size"""
        return cls(MTheme().small, color)

    @classmethod
    def tiny(cls, color: str | None = None):
        """Create a MLoading with tiny size"""
        return cls(MTheme().tiny, color)


class MLoadingWrapper(QtWidgets.QWidget):
    """
    A wrapper widget to show the loading widget or hide.
    Property:
        dayu_loading: bool. current loading state.
    """

    def __init__(
        self,
        widget: QtWidgets.QWidget,
        loading: bool = True,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self._widget = widget
        self._mask_widget = QtWidgets.QFrame()
        self._mask_widget.setObjectName("mask")
        self._mask_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self._loading_widget = MLoading()
        self._loading_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        self._main_lay = QtWidgets.QGridLayout()
        self._main_lay.setContentsMargins(0, 0, 0, 0)
        self._main_lay.addWidget(widget, 0, 0)
        self._main_lay.addWidget(self._mask_widget, 0, 0)
        self._main_lay.addWidget(
            self._loading_widget, 0, 0, QtCore.Qt.AlignmentFlag.AlignCenter
        )
        self.setLayout(self._main_lay)
        self._loading: bool = False
        self.set_dayu_loading(loading)

    def _set_loading(self):
        self._loading_widget.setVisible(self._loading)
        self._mask_widget.setVisible(self._loading)

    def set_dayu_loading(self, loading: bool):
        """
        Set current state to loading or not
        :param loading: bool
        :return: None
        """
        self._loading = loading
        self._set_loading()

    def get_dayu_loading(self) -> bool:
        """
        Get current loading widget is loading or not.
        :return: bool
        """
        return self._loading

    dayu_loading = QtCore.Property(bool, get_dayu_loading, set_dayu_loading)
