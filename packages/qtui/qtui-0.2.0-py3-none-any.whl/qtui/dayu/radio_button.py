"""
MRadioButton
"""

from PySide6 import QtWidgets

from .mixin import cursor_mixin


@cursor_mixin
class MRadioButton(QtWidgets.QRadioButton):
    """
    MRadioButton just use stylesheet and set cursor shape when hover. No more extend.
    """

    def __init__(self, text: str = "", parent: QtWidgets.QWidget | None = None):
        super().__init__(text, parent=parent)
