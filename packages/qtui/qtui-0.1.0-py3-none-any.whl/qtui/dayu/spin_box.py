"""
Custom Stylesheet for QSpinBox, QDoubleSpinBox, QDateTimeEdit, QDateEdit, QTimeEdit.
Only add size arg for their __init__.
"""

from qtpy import QtCore, QtWidgets

from .mixin import cursor_mixin
from .theme import MTheme


@cursor_mixin
class MSpinBox(QtWidgets.QSpinBox):
    """
    MSpinBox just use stylesheet and add dayu_size. No more extend.
    Property:
        dayu_size: The height of MSpinBox
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self._dayu_size: int = MTheme().default_size

    def get_dayu_size(self) -> int:
        """
        Get the MSpinBox height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int) -> None:
        """
        Set the MSpinBox size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        """Set MSpinBox to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MSpinBox to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MSpinBox to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MSpinBox to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MSpinBox to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self


@cursor_mixin
class MDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    """
    MDoubleSpinBox just use stylesheet and add dayu_size. No more extend.
    Property:
        dayu_size: The height of MDoubleSpinBox
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self._dayu_size: int = MTheme().default_size

    def get_dayu_size(self) -> int:
        """
        Get the MDoubleSpinBox height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int) -> None:
        """
        Set the MDoubleSpinBox size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        """Set MDoubleSpinBox to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MDoubleSpinBox to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MDoubleSpinBox to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MDoubleSpinBox to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MDoubleSpinBox to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self


@cursor_mixin
class MDateTimeEdit(QtWidgets.QDateTimeEdit):
    """
    MDateTimeEdit just use stylesheet and add dayu_size. No more extend.
    Property:
        dayu_size: The height of MDateTimeEdit
    """

    def __init__(
        self,
        datetime: QtCore.QDateTime | None = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        if datetime is None:
            super().__init__(parent=parent)
        else:
            super().__init__(datetime, parent=parent)
        self._dayu_size: int = MTheme().default_size

    def get_dayu_size(self) -> int:
        """
        Get the MDateTimeEdit height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int) -> None:
        """
        Set the MDateTimeEdit size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        """Set MDateTimeEdit to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MDateTimeEdit to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MDateTimeEdit to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MDateTimeEdit to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MDateTimeEdit to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self


@cursor_mixin
class MDateEdit(QtWidgets.QDateEdit):
    """
    MDateEdit just use stylesheet and add dayu_size. No more extend.
    Property:
        dayu_size: The height of MDateEdit
    """

    def __init__(
        self,
        date: QtCore.QDate | None = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        if date is None:
            super().__init__(parent=parent)
        else:
            super().__init__(date, parent=parent)
        self._dayu_size: int = MTheme().default_size

    def get_dayu_size(self) -> int:
        """
        Get the MDateEdit height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int) -> None:
        """
        Set the MDateEdit size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        """Set MDateEdit to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MDateEdit to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MDateEdit to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MDateEdit to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MDateEdit to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self


@cursor_mixin
class MTimeEdit(QtWidgets.QTimeEdit):
    """
    MTimeEdit just use stylesheet and add dayu_size. No more extend.
    Property:
        dayu_size: The height of MTimeEdit
    """

    def __init__(
        self,
        time: QtCore.QTime | None = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        if time is None:
            super().__init__(parent=parent)
        else:
            super().__init__(time, parent=parent)
        self._dayu_size: int = MTheme().default_size

    def get_dayu_size(self) -> int:
        """
        Get the MTimeEdit height
        :return: integer
        """
        return self._dayu_size

    def set_dayu_size(self, value: int) -> None:
        """
        Set the MTimeEdit size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.style().polish(self)

    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)

    def huge(self):
        """Set MTimeEdit to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MTimeEdit to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MTimeEdit to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MTimeEdit to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MTimeEdit to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self
