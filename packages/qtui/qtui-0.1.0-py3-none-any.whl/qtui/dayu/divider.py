"""
MDivider
"""

from enum import IntFlag
from typing import ClassVar

from qtpy import QtCore, QtWidgets

from .label import MLabel


class MDivider(QtWidgets.QWidget):
    """
    A divider line separates different content.

    Property:
        dayu_text: str
    """

    _alignment_map: ClassVar[dict[IntFlag, int]] = {
        QtCore.Qt.AlignmentFlag.AlignCenter: 50,
        QtCore.Qt.AlignmentFlag.AlignLeft: 20,
        QtCore.Qt.AlignmentFlag.AlignRight: 80,
    }

    def __init__(
        self,
        text: str = "",
        orientation: QtCore.Qt.Orientation = QtCore.Qt.Orientation.Horizontal,
        alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self._orient = orientation
        self._text_label = MLabel().secondary()
        self._left_frame = QtWidgets.QFrame()
        self._right_frame = QtWidgets.QFrame()
        self._main_lay = QtWidgets.QHBoxLayout()
        self._main_lay.setContentsMargins(0, 0, 0, 0)
        self._main_lay.setSpacing(0)
        self._main_lay.addWidget(self._left_frame)
        self._main_lay.addWidget(self._text_label)
        self._main_lay.addWidget(self._right_frame)
        self.setLayout(self._main_lay)

        if orientation == QtCore.Qt.Orientation.Horizontal:
            self._left_frame.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            self._left_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            self._right_frame.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            self._right_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        else:
            self._text_label.setVisible(False)
            self._right_frame.setVisible(False)
            self._left_frame.setFrameShape(QtWidgets.QFrame.Shape.VLine)
            self._left_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
            self.setFixedWidth(2)
        self._main_lay.setStretchFactor(
            self._left_frame, self._alignment_map.get(alignment, 50)
        )
        self._main_lay.setStretchFactor(
            self._right_frame, 100 - self._alignment_map.get(alignment, 50)
        )
        self._text = None
        self.set_dayu_text(text)

    def set_dayu_text(self, value: str):
        """
        Set the divider's text.
        When text is empty, hide the text_label and right_frame
        to ensure the divider not has a gap.

        :param value: str
        :return: None
        """
        self._text = value
        self._text_label.setText(value)
        if self._orient == QtCore.Qt.Orientation.Horizontal:
            self._text_label.setVisible(bool(value))
            self._right_frame.setVisible(bool(value))

    def get_dayu_text(self):
        """
        Get current text
        :return: str
        """
        return self._text

    dayu_text = QtCore.Property(str, get_dayu_text, set_dayu_text)

    @classmethod
    def left(cls, text: str = ""):
        """Create a horizontal divider with text at left."""
        return cls(text, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

    @classmethod
    def right(cls, text: str = ""):
        """Create a horizontal divider with text at right."""
        return cls(text, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

    @classmethod
    def center(cls, text: str = ""):
        """Create a horizontal divider with text at center."""
        return cls(text, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    @classmethod
    def vertical(cls):
        """Create a vertical divider"""
        return cls(orientation=QtCore.Qt.Orientation.Vertical)
