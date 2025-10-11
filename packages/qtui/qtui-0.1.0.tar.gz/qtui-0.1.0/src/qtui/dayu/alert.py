"""
MAlert class.
"""

import functools
from enum import StrEnum

from qtpy import QtCore, QtWidgets

from .avatar import MAvatar
from .label import MLabel
from .mixin import property_mixin
from .qt import MPixmap, get_scale_factor
from .theme import MTheme
from .tool_button import MToolButton
from .widget import MWidget


@property_mixin
class MAlert(QtWidgets.QWidget, MWidget):  # pyright: ignore[reportGeneralTypeIssues]
    """
    Alert component for feedback.

    Property:
        dayu_type: The feedback type with different color container.
        dayu_text: The feedback string showed in container.
    """

    class AlertType(StrEnum):
        Info = "info"
        Success = "success"
        Warning = "warning"
        Error = "error"

    def __init__(
        self,
        text: str = "",
        parent: QtWidgets.QWidget | None = None,
        flags: QtCore.Qt.WindowType = QtCore.Qt.WindowType.Widget,
    ):
        super().__init__(parent, flags)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground)

        self._icon_label = MAvatar.tiny()
        self._content_label = MLabel().secondary()
        self._close_button = MToolButton().svg("close_line.svg").tiny().icon_only()
        self._close_button.clicked.connect(functools.partial(self.setVisible, False))

        scale_x, _ = get_scale_factor()
        margin = int(8 * scale_x)

        self._main_layout = QtWidgets.QHBoxLayout()
        self._main_layout.setContentsMargins(margin, margin, margin, margin)
        self._main_layout.addWidget(self._icon_label)
        self._main_layout.addWidget(self._content_label)
        self._main_layout.addStretch()
        self._main_layout.addWidget(self._close_button)

        self.setLayout(self._main_layout)
        self.set_show_icon(True)
        self.set_closable(False)

        self._dayu_text: str
        self.set_dayu_type(MAlert.AlertType.Info)
        self.set_dayu_text(text)

    def set_closable(self, closable: bool):
        """Display the close icon button or not."""
        self._close_button.setVisible(closable)

    def set_show_icon(self, show_icon: bool):
        """Display the information type icon or not."""
        self._icon_label.setVisible(show_icon)

    def _set_dayu_text(self):
        self._content_label.setText(self._dayu_text)
        self.setVisible(bool(self._dayu_text))

    def set_dayu_text(self, value: str):
        """Set the feedback content."""

        self._dayu_text = value
        self._set_dayu_text()

    def _set_dayu_type(self):
        self._icon_label.set_dayu_image(
            MPixmap(
                f"{self._dayu_type}_fill.svg",
                MTheme().get_color(self._dayu_type),
            )
        )
        self.on_style_changed()

    def set_dayu_type(self, value: str):
        """Set feedback type."""

        if value != self._dayu_type:
            self._dayu_type = value
            self._icon_label.set_dayu_image(
                MPixmap(
                    f"{self._dayu_type}_fill.svg",
                    MTheme().get_color(self._dayu_type),
                )
            )
            self.on_style_changed()

    def get_dayu_type(self):
        """
        Get MAlert feedback type.
        :return: str
        """
        return self._dayu_type

    def get_dayu_text(self):
        """
        Get MAlert feedback message.
        :return: str
        """
        return self._dayu_text

    dayu_text = QtCore.Property(str, get_dayu_text, set_dayu_text)
    dayu_type = QtCore.Property(str, get_dayu_type, set_dayu_type)

    def info(self):
        """Set MAlert to InfoType"""
        self.set_dayu_type(MAlert.AlertType.Info)
        return self

    def success(self):
        """Set MAlert to SuccessType"""
        self.set_dayu_type(MAlert.AlertType.Success)
        return self

    def warning(self):
        """Set MAlert to  WarningType"""
        self.set_dayu_type(MAlert.AlertType.Warning)
        return self

    def error(self):
        """Set MAlert to ErrorType"""
        self.set_dayu_type(MAlert.AlertType.Error)
        return self

    def closable(self):
        """Set MAlert closebale is True"""
        self.set_closable(True)
        return self
