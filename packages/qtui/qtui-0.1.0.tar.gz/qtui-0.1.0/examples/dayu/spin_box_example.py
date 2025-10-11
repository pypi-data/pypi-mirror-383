"""
Example code for MDateTimeEdit, MDoubleSpinBox, MSpinBox, MTimeEdit, MDateEdit
"""

from qtpy import QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.spin_box import (
    MDateEdit,
    MDateTimeEdit,
    MDoubleSpinBox,
    MSpinBox,
    MTimeEdit,
)


class SpinBoxExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for Spin Box")

        main_lay = QtWidgets.QVBoxLayout()
        class_list = [MSpinBox, MDoubleSpinBox, MDateTimeEdit, MDateEdit, MTimeEdit]
        for cls in class_list:
            main_lay.addWidget(MDivider(cls.__name__))
            lay = QtWidgets.QHBoxLayout()
            lay.addWidget(cls().large())
            lay.addWidget(cls().medium())
            lay.addWidget(cls().small())
            main_lay.addLayout(lay)

        main_lay.addWidget(MDivider("Pop Calendar Widget"))
        date_time_edit = MDateTimeEdit()
        date_time_edit.setCalendarPopup(True)
        date_edit = MDateEdit()
        date_edit.setCalendarPopup(True)
        time_edit = MTimeEdit()
        time_edit.setCalendarPopup(True)
        date_lay = QtWidgets.QHBoxLayout()
        date_lay.addWidget(date_time_edit)
        date_lay.addWidget(date_edit)
        date_lay.addWidget(time_edit)
        main_lay.addLayout(date_lay)

        main_lay.addStretch()
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = SpinBoxExample()
        MTheme().apply(test)
        test.show()
