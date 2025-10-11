"""
MPushButton.
"""

from enum import StrEnum

from qtpy import QtGui, QtWidgets

from .mixin import cursor_mixin, focus_shadow_mixin
from .theme import MTheme
from .widget import MWidget


@cursor_mixin
@focus_shadow_mixin
class MPushButton(QtWidgets.QPushButton, MWidget):
    """
    QPushButton.
    """

    class ButtonType(StrEnum):
        Default = "default"
        Primary = "primary"
        Success = "success"
        Warning = "warning"
        Danger = "danger"

    def __init__(
        self,
        text: str = "",
        icon: QtGui.QIcon | None = None,
        parent: QtWidgets.QWidget | None = None,
    ):
        if icon is None:
            super().__init__(text, parent=parent)
        else:
            super().__init__(icon, text, parent=parent)
        self.set_dayu_type(MPushButton.ButtonType.Default)

    def primary(self):
        """Set MPushButton to PrimaryType"""
        self.set_dayu_type(MPushButton.ButtonType.Primary)
        return self

    def success(self):
        """Set MPushButton to SuccessType"""
        self.set_dayu_type(MPushButton.ButtonType.Success)
        return self

    def warning(self):
        """Set MPushButton to  WarningType"""
        self.set_dayu_type(MPushButton.ButtonType.Warning)
        return self

    def danger(self):
        """Set MPushButton to DangerType"""
        self.set_dayu_type(MPushButton.ButtonType.Danger)
        return self

    def huge(self):
        """Set MPushButton to huge size"""
        self.set_dayu_size(MTheme().huge)
        return self

    def large(self):
        """Set MPushButton to large size"""
        self.set_dayu_size(MTheme().large)
        return self

    def medium(self):
        """Set MPushButton to  medium"""
        self.set_dayu_size(MTheme().medium)
        return self

    def small(self):
        """Set MPushButton to small size"""
        self.set_dayu_size(MTheme().small)
        return self

    def tiny(self):
        """Set MPushButton to tiny size"""
        self.set_dayu_size(MTheme().tiny)
        return self
