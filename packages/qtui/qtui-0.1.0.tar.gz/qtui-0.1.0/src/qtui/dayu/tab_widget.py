from qtpy import QtCore, QtWidgets

from .mixin import cursor_mixin, stacked_animation_mixin


@cursor_mixin
class MTabBar(QtWidgets.QTabBar):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self.setDrawBase(False)

    def tabSizeHint(self, index: int) -> QtCore.QSize:  # noqa: N802
        tab_text = self.tabText(index)
        if self.tabsClosable():
            return QtCore.QSize(
                self.fontMetrics().boundingRect(tab_text).width() + 70,
                self.fontMetrics().height() + 20,
            )
        else:
            return QtCore.QSize(
                self.fontMetrics().boundingRect(tab_text).width() + 50,
                self.fontMetrics().height() + 20,
            )


@stacked_animation_mixin
class MTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent=parent)
        self.bar = MTabBar()
        self.setTabBar(self.bar)

    def disable_animation(self) -> None:
        self.currentChanged.disconnect(self._play_anim)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]
