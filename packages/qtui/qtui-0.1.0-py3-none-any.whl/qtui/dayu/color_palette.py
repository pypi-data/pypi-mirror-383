import functools

from qtpy import QtCore, QtGui, QtWidgets

from .divider import MDivider
from .label import MLabel
from .message import MMessage
from .utils import generate_color


class MColorChart(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setSpacing(0)
        self.button_list: list[QtWidgets.QPushButton] = []
        for index in range(10):
            button = QtWidgets.QPushButton()
            button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            button.setToolTip("Click to Copy Color")
            button.setFixedSize(QtCore.QSize(250, 45))
            button.setText(f"color-{index + 1}")
            button.clicked.connect(functools.partial(self.on_copy_color, button))
            self.button_list.append(button)
            main_layout.addWidget(button)
        self.setLayout(main_layout)

    def set_colors(self, color_list: list[str]):
        for index, button in enumerate(self.button_list):
            target = color_list[index]
            button.setText(f"color-{index + 1}\t{target}")
            button.setProperty("color", target)
            button.setStyleSheet(
                "QPushButton{{background-color:{};color:{};border: 0 solid black}}"
                "QPushButton:hover{{font-weight:bold;}}".format(
                    target, "#000" if index < 5 else "#fff"
                )
            )

    def on_copy_color(self, button: QtWidgets.QPushButton):
        color = button.property("color")
        QtWidgets.QApplication.clipboard().setText(color)
        MMessage.success(f"copied: {color}", parent=self)


class MColorPaletteDialog(QtWidgets.QDialog):
    def __init__(self, init_color: str, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Color Palette")

        self.primary_color = QtGui.QColor(init_color)
        self.color_chart = MColorChart()

        self.choose_color_button = QtWidgets.QPushButton()
        self.choose_color_button.setFixedSize(QtCore.QSize(100, 30))

        self.color_label = QtWidgets.QLabel()
        self.info_label = MLabel()
        self.info_label.setProperty("error", True)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(MLabel("Primary Color:"))
        color_layout.addWidget(self.choose_color_button)
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.info_label)
        color_layout.addStretch()

        dialog = QtWidgets.QColorDialog(self.primary_color, parent=self)
        dialog.setWindowFlags(QtCore.Qt.WindowType.Widget)
        dialog.setOption(QtWidgets.QColorDialog.ColorDialogOption.NoButtons)
        dialog.currentColorChanged.connect(self.on_color_changed)
        setting_layout = QtWidgets.QVBoxLayout()
        setting_layout.addLayout(color_layout)
        setting_layout.addWidget(MDivider())
        setting_layout.addWidget(dialog)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.color_chart)
        main_layout.addLayout(setting_layout)
        self.setLayout(main_layout)
        self.update_color()

    @QtCore.Slot(QtGui.QColor)
    def on_color_changed(self, color: QtGui.QColor):
        self.primary_color = color
        light = self.primary_color.lightness()
        saturation = self.primary_color.saturation()
        self.info_label.setText("")
        if light <= 70:
            self.info_label.setText(f"lightness: {light}")
        if saturation <= 70:
            self.info_label.setText(f"saturation: {saturation}")

        self.update_color()

    def update_color(self):
        self.choose_color_button.setStyleSheet(
            "border-radius: 0;border: none;border:1px solid gray;"
            f"background-color:{self.primary_color.name()};"
        )
        self.color_label.setText(self.primary_color.name())
        self.color_chart.set_colors(
            [generate_color(self.primary_color, index + 1) for index in range(10)]
        )


if __name__ == "__main__":
    # Import built-in modules
    import sys

    # Import local modules
    from .theme import MTheme

    app = QtWidgets.QApplication(sys.argv)
    test = MColorPaletteDialog(init_color="#1890ff")
    MTheme().apply(test)
    test.show()
    sys.exit(app.exec_())
