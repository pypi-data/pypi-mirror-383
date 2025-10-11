"""
MAvatar.
"""

from __future__ import annotations

from qtpy import QtCore, QtGui, QtWidgets

from .qt import MPixmap
from .theme import MTheme
from .widget import MWidget


class MAvatar(QtWidgets.QLabel, MWidget):
    """
    Avatar component. It can be used to represent people or object.
    Property:
        image: avatar image, should be QPixmap.
        dayu_size: the size of image.
    """

    def __init__(
        self,
        parent: QtWidgets.QWidget | None = None,
        flags: QtCore.Qt.WindowType = QtCore.Qt.WindowType.Widget,
    ):
        super().__init__(parent, flags)
        self._default_pix = MPixmap("user_fill.svg")
        self._pixmap = self._default_pix
        self._dayu_size = 0
        self.set_dayu_size(MTheme().default_size)

    def set_dayu_size(self, value: int) -> None:
        """
        Set the avatar size.
        :param value: integer
        :return: None
        """
        if value != self._dayu_size:
            self._dayu_size = value
            self._set_size()

    def _set_size(self) -> None:
        self.setFixedSize(QtCore.QSize(self._dayu_size, self._dayu_size))
        self._set_image()

    def _set_image(self) -> None:
        self.setPixmap(
            self._pixmap.scaledToWidth(
                self.height(), QtCore.Qt.TransformationMode.SmoothTransformation
            )
        )

    def set_dayu_image(self, value: QtGui.QPixmap | None):
        """
        Set avatar image.
        :param value: QPixmap or None.
        :return: None
        """

        if value is None:
            self._pixmap = self._default_pix
        else:
            self._pixmap = self._default_pix if value.isNull() else value

        self._set_image()

    def get_dayu_image(self) -> QtGui.QPixmap:
        """
        Get the avatar image.
        :return: QPixmap
        """
        return self._pixmap

    def get_dayu_size(self) -> int:
        """
        Get the avatar size
        :return: integer
        """
        return self._dayu_size

    dayu_image = QtCore.Property(QtGui.QPixmap, get_dayu_image, set_dayu_image)
    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    @classmethod
    def huge(cls, image: QtGui.QPixmap | None = None) -> MAvatar:
        """Create a MAvatar with huge size"""
        inst = cls()
        inst.set_dayu_size(MTheme().huge)
        inst.set_dayu_image(image)
        return inst

    @classmethod
    def large(cls, image: QtGui.QPixmap | None = None) -> MAvatar:
        """Create a MAvatar with large size"""
        inst = cls()
        inst.set_dayu_size(MTheme().large)
        inst.set_dayu_image(image)
        return inst

    @classmethod
    def medium(cls, image: QtGui.QPixmap | None = None) -> MAvatar:
        """Create a MAvatar with medium size"""
        inst = cls()
        inst.set_dayu_size(MTheme().medium)
        inst.set_dayu_image(image)
        return inst

    @classmethod
    def small(cls, image: QtGui.QPixmap | None = None) -> MAvatar:
        """Create a MAvatar with small size"""
        inst = cls()
        inst.set_dayu_size(MTheme().small)
        inst.set_dayu_image(image)
        return inst

    @classmethod
    def tiny(cls, image: QtGui.QPixmap | None = None) -> MAvatar:
        """Create a MAvatar with tiny size"""
        inst = cls()
        inst.set_dayu_size(MTheme().tiny)
        inst.set_dayu_image(image)
        return inst
