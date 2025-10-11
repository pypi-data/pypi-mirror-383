import re
from enum import IntEnum, StrEnum

from qtpy import QtCore, QtWidgets

from .theme import MTheme
from .widget import MWidget


class MLabel(QtWidgets.QLabel, MWidget):
    """
    Display title in different level.
    """

    class LabelLevel(IntEnum):
        H1 = 1
        H2 = 2
        H3 = 3
        H4 = 4

    class LabelType(StrEnum):
        Secondary = "secondary"
        Warning = "warning"
        Danger = "danger"

    dayu_text_changed = QtCore.Signal(str)

    def __init__(
        self,
        text: str = "",
        parent: QtWidgets.QWidget | None = None,
        flags: QtCore.Qt.WindowType = QtCore.Qt.WindowType.Widget,
    ):
        super().__init__(text, parent, flags)
        self.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
            | QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self._dayu_text: str = text
        self._dayu_level: int = 0
        self._dayu_underline: bool = False
        self._dayu_delete: bool = False
        self._dayu_strong: bool = False
        self._dayu_mark: bool = False
        self._dayu_code: bool = False
        self._elide_mode = QtCore.Qt.TextElideMode.ElideNone

        self.dayu_text_changed.connect(self.on_dayu_text_changed)

    def get_dayu_text(self) -> str:
        return self._dayu_text

    def set_dayu_text(self, value: str) -> None:
        if value != self._dayu_text:
            self._dayu_text = value
            self.setText(value)
            self.dayu_text_changed.emit(value)

    def get_dayu_level(self) -> int:
        """Get MLabel level."""
        return self._dayu_level

    def set_dayu_level(self, value: int) -> None:
        """Set MLabel level"""
        if value != self._dayu_level:
            self._dayu_level = value
            self.on_style_changed()

    def set_dayu_underline(self, value: bool) -> None:
        """Set MLabel underline style."""
        if value != self._dayu_underline:
            self._dayu_underline = value
            self.on_style_changed()

    def get_dayu_underline(self) -> bool:
        return self._dayu_underline

    def set_dayu_delete(self, value: bool) -> None:
        """Set MLabel a delete line style."""
        if value != self._dayu_delete:
            self._dayu_delete = value
            self.on_style_changed()

    def get_dayu_delete(self) -> bool:
        return self._dayu_delete

    def set_dayu_strong(self, value: bool) -> None:
        """Set MLabel bold style."""
        if value != self._dayu_strong:
            self._dayu_strong = value
            self.on_style_changed()

    def get_dayu_strong(self) -> bool:
        return self._dayu_strong

    def set_dayu_mark(self, value: bool) -> None:
        """Set MLabel mark style."""
        if value != self._dayu_mark:
            self._dayu_mark = value
            self.on_style_changed()

    def get_dayu_mark(self) -> bool:
        return self._dayu_mark

    def set_dayu_code(self, value: bool) -> None:
        """Set MLabel code style."""
        if value != self._dayu_code:
            self._dayu_code = value
            self.on_style_changed()

    def get_dayu_code(self) -> bool:
        return self._dayu_code

    def get_elide_mode(self) -> QtCore.Qt.TextElideMode:
        return self._elide_mode

    def set_elide_mode(self, value: QtCore.Qt.TextElideMode) -> None:
        """Set MLabel elide mode.
        Only accepted Qt.ElideLeft/Qt.ElideMiddle/Qt.ElideRight/Qt.ElideNone"""
        self._elide_mode = value
        self._update_elided_text()

    dayu_text = QtCore.Property(
        str,
        get_dayu_text,
        set_dayu_text,
        notify=dayu_text_changed,
    )
    dayu_level = QtCore.Property(
        int,
        get_dayu_level,
        set_dayu_level,
    )
    dayu_underline = QtCore.Property(
        bool,
        get_dayu_underline,
        set_dayu_underline,
    )
    dayu_delete = QtCore.Property(
        bool,
        get_dayu_delete,
        set_dayu_delete,
    )
    dayu_strong = QtCore.Property(
        bool,
        get_dayu_strong,
        set_dayu_strong,
    )
    dayu_mark = QtCore.Property(
        bool,
        get_dayu_mark,
        set_dayu_mark,
    )
    dayu_code = QtCore.Property(
        bool,
        get_dayu_code,
        set_dayu_code,
    )
    dayu_elide_mod = QtCore.Property(
        QtCore.Qt.TextElideMode,
        get_dayu_code,
        set_dayu_code,
    )

    def minimumSizeHint(self):  # noqa: N802
        return QtCore.QSize(1, self.fontMetrics().height())

    def setText(self, text: str):  # noqa: N802
        """
        Overridden base method to set the text on the label

        :param text:    The text to set on the label
        """
        super().setText(text)
        self.set_dayu_text(text)
        self._update_elided_text()
        self.setToolTip(text)

    def set_link(self, href: str, text: str = "") -> None:
        """

        :param href: The href attr of a tag
        :param text: The a tag text content
        """
        link_style = MTheme().hyperlink_style
        self.setText(f'{link_style}<a href="{href}">{text or href}</a>')
        self.setOpenExternalLinks(True)

    def _update_elided_text(self):
        """
        Update the elided text on the label
        """
        _font_metrics = self.fontMetrics()
        text = self.property("text")
        text = text if text else ""

        is_html = bool(re.search(r"<[^>]+>", text))

        if is_html:
            super().setText(text)
        else:
            _elided_text = _font_metrics.elidedText(
                text, self._elide_mode, self.width() - 2 * 2
            )
            super().setText(_elided_text)

    def resizeEvent(self, event: QtCore.QEvent):  # noqa: N802
        """
        Overridden base method called when the widget is resized.

        :param event:    The resize event
        """
        self._update_elided_text()

    def h1(self):
        """Set QLabel with h1 type."""
        self.set_dayu_level(MLabel.LabelLevel.H1)
        return self

    def h2(self):
        """Set QLabel with h2 type."""
        self.set_dayu_level(MLabel.LabelLevel.H2)
        return self

    def h3(self):
        """Set QLabel with h3 type."""
        self.set_dayu_level(MLabel.LabelLevel.H3)
        return self

    def h4(self):
        """Set QLabel with h4 type."""
        self.set_dayu_level(MLabel.LabelLevel.H4)
        return self

    def secondary(self):
        """Set QLabel with secondary type."""
        self.set_dayu_type(MLabel.LabelType.Secondary)
        return self

    def warning(self):
        """Set QLabel with warning type."""
        self.set_dayu_type(MLabel.LabelType.Warning)
        return self

    def danger(self):
        """Set QLabel with danger type."""
        self.set_dayu_type(MLabel.LabelType.Danger)
        return self

    def strong(self):
        """Set QLabel with strong style."""
        self.set_dayu_strong(True)
        return self

    def mark(self):
        """Set QLabel with mark style."""
        self.set_dayu_mark(True)
        return self

    def code(self):
        """Set QLabel with code style."""
        self.set_dayu_code(True)
        return self

    def delete(self):
        """Set QLabel with delete style."""
        self.set_dayu_delete(True)
        return self

    def underline(self):
        """Set QLabel with underline style."""
        self.set_dayu_underline(True)
        return self

    @QtCore.Slot(str)
    def on_dayu_text_changed(self, value: str):
        self.setText(value)
