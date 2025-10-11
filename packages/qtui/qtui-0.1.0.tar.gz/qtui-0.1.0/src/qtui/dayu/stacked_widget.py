"""MStackedWidget"""

# Import third-party modules
from qtpy import QtWidgets

# Import local modules
from .mixin import stacked_animation_mixin


@stacked_animation_mixin
class MStackedWidget(QtWidgets.QStackedWidget):
    """Just active animation when current index changed."""

    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

    def disable_animation(self):
        self.currentChanged.disconnect(self._play_anim)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
