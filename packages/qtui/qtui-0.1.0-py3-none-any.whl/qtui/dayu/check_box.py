"""
MCheckBox
"""

from qtpy import QtWidgets

from .mixin import cursor_mixin


@cursor_mixin
class MCheckBox(QtWidgets.QCheckBox):
    """
    MCheckBox just use stylesheet and set cursor shape when hover. No more extend.
    """

    def __init__(self, text: str = "", parent: QtWidgets.QWidget | None = None):
        super().__init__(text, parent=parent)
