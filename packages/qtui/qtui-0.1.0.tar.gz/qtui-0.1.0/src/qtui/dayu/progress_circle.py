"""MProgressCircle"""

from __future__ import annotations

from qtpy import QtCore, QtGui, QtWidgets

from . import utils
from .label import MLabel
from .theme import MTheme


class MProgressCircle(QtWidgets.QProgressBar):
    """
    MProgressCircle: Display the current progress of an operation flow.
    When you need to display the completion percentage of an operation.

    Property:
        dayu_width: int
        dayu_color: str
    """

    def __init__(
        self, dashboard: bool = False, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._main_lay = QtWidgets.QHBoxLayout()
        self._default_label = MLabel().h3()
        self._default_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._main_lay.addWidget(self._default_label)
        self.setLayout(self._main_lay)
        self._color: str
        self._width: int

        self._start_angle = 90 * 16
        self._max_delta_angle = 360 * 16
        self._height_factor = 1.0
        self._width_factor = 1.0
        if dashboard:
            self._start_angle = 225 * 16
            self._max_delta_angle = 270 * 16
            self._height_factor = (2 + pow(2, 0.5)) / 4 + 0.03

        self.set_dayu_width(MTheme().progress_circle_default_radius)
        self.set_dayu_color(str(MTheme().primary_color))

    def set_widget(self, widget: QtWidgets.QWidget) -> None:
        """
        Set a custom widget to show on the circle's inner center
         and replace the default percent label
        :param widget: QWidget
        :return: None
        """
        self.setTextVisible(False)
        if not widget.styleSheet():
            widget.setStyleSheet("background:transparent")
        self._main_lay.addWidget(widget)

    def get_dayu_width(self) -> int:
        """
        Get current circle fixed width
        :return: int
        """
        return self._width

    def set_dayu_width(self, value: int) -> None:
        """
        Set current circle fixed width
        :param value: int
        :return: None
        """
        self._width = value
        self.setFixedSize(
            QtCore.QSize(
                int(self._width * self._width_factor),
                int(self._width * self._height_factor),
            )
        )

    def get_dayu_color(self) -> str:
        """
        Get current circle foreground color
        :return: str
        """
        return self._color

    def set_dayu_color(self, value: str) -> None:
        """
        Set current circle's foreground color
        :param value: str
        :return:
        """
        self._color = value
        self.update()

    dayu_color = QtCore.Property(str, get_dayu_color, set_dayu_color)
    dayu_width = QtCore.Property(int, get_dayu_width, set_dayu_width)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: N802
        """Override QProgressBar's paintEvent."""
        if self.text() != self._default_label.text():
            self._default_label.setText(self.text())
        if self.isTextVisible() != self._default_label.isVisible():
            self._default_label.setVisible(self.isTextVisible())

        percent = utils.get_percent(self.value(), self.minimum(), self.maximum())
        total_width = self.get_dayu_width()
        pen_width = int(3 * total_width / 50.0)
        radius = total_width - pen_width - 1

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing)

        # draw background circle
        pen_background = QtGui.QPen()
        pen_background.setWidth(pen_width)
        pen_background.setColor(QtGui.QColor(MTheme().background_selected_color))
        pen_background.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_background)
        painter.drawArc(
            int(pen_width / 2.0 + 1),
            int(pen_width / 2.0 + 1),
            radius,
            radius,
            self._start_angle,
            -self._max_delta_angle,
        )

        # draw foreground circle
        pen_foreground = QtGui.QPen()
        pen_foreground.setWidth(pen_width)
        pen_foreground.setColor(QtGui.QColor(self._color))
        pen_foreground.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_foreground)
        painter.drawArc(
            int(pen_width / 2.0 + 1),
            int(pen_width / 2.0 + 1),
            radius,
            radius,
            self._start_angle,
            int(-percent * 0.01 * self._max_delta_angle),
        )
        painter.end()

    @classmethod
    def dashboard(cls, parent: QtWidgets.QWidget | None = None) -> MProgressCircle:
        """Create a dashboard style MCircle"""
        return MProgressCircle(dashboard=True, parent=parent)
