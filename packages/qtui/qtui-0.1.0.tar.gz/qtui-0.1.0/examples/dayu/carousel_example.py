from qtpy import QtWidgets

from qtui.dayu.carousel import MCarousel
from qtui.dayu.label import MLabel
from qtui.dayu.qt import MPixmap
from qtui.dayu.slider import MSlider
from qtui.dayu.switch import MSwitch


class CarouselExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MCarousel")
        self._init_ui()

    def _init_ui(self):
        switch = MSwitch()
        switch.setChecked(True)
        slider = MSlider()
        slider.setRange(1, 10)
        switch_lay = QtWidgets.QFormLayout()
        switch_lay.addRow(MLabel("AutoPlay"), switch)
        switch_lay.addRow(MLabel("Interval"), slider)
        test = MCarousel(
            [MPixmap(f"app-{a}.png") for a in ["maya", "nuke", "houdini"]],
            width=300,
            height=300,
            autoplay=True,
        )
        switch.toggled.connect(test.set_autoplay)

        def set_interval(x: int):
            test.set_interval(x * 1000)

        slider.valueChanged.connect(set_interval)
        slider.setValue(3)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(test)
        main_lay.addLayout(switch_lay)
        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = CarouselExample()
        MTheme().apply(test)
        test.show()
