import functools
from collections.abc import Callable
from typing import Any

from qtpy import QtCore, QtWidgets

from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.push_button import MPushButton
from qtui.dayu.toast import MToast


class MWorkThread(QtCore.QThread):
    def __init__(self, parent: QtCore.QObject | None = None):
        super().__init__(parent)

    def run(self):
        import time

        time.sleep(3)


class ToastExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MToast")
        self._init_ui()

    def _init_ui(self):
        button3 = MPushButton(text="Normal Message").primary()
        button4 = MPushButton(text="Success Message").success()
        button5 = MPushButton(text="Warning Message").warning()
        button6 = MPushButton(text="Error Message").danger()
        button3.clicked.connect(
            functools.partial(self.slot_show_message, MToast.info, {"text": "No use"})
        )
        button4.clicked.connect(
            functools.partial(
                self.slot_show_message, MToast.success, {"text": "Success"}
            )
        )
        button5.clicked.connect(
            functools.partial(
                self.slot_show_message, MToast.warning, {"text": "Not supported"}
            )
        )
        button6.clicked.connect(
            functools.partial(
                self.slot_show_message,
                MToast.error,
                {"text": "Payment failed, please try again"},
            )
        )

        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(button3)
        sub_lay1.addWidget(button4)
        sub_lay1.addWidget(button5)
        sub_lay1.addWidget(button6)

        loading_button = MPushButton("Loading Toast").primary()
        loading_button.clicked.connect(self.slot_show_loading)

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("different type"))
        main_lay.addLayout(sub_lay1)
        main_lay.addWidget(
            MLabel(
                "Different prompt status: success, failure, loading. Default 2 seconds to disappear"  # noqa: E501
            )
        )
        main_lay.addWidget(loading_button)

        main_lay.addStretch()
        self.setLayout(main_lay)

    def slot_show_message(self, func: Callable[..., Any], config: dict[str, Any]):
        func(parent=self, **config)

    def slot_set_config(self, func: Callable[..., Any], config: dict[str, Any]):
        func(**config)

    def slot_show_loading(self):
        my_thread = MWorkThread(parent=self)
        my_thread.finished.connect(self.slot_finished)
        my_thread.start()
        self.msg = MToast.loading("Loading", parent=self)

    def slot_finished(self):
        self.msg.close()
        MToast.success("Loading successful", self)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = ToastExample()
        MTheme().apply(test)
        test.show()
