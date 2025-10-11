import functools
from collections.abc import Callable
from typing import Any

from qtpy import QtWidgets

from qtui.dayu.button_group import MPushButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.message import MMessage
from qtui.dayu.push_button import MPushButton


class MessageExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MMessage")
        self._init_ui()

    def _init_ui(self):
        button3 = MPushButton(text="Normal Message").primary()
        button4 = MPushButton(text="Success Message").success()
        button5 = MPushButton(text="Warning Message").warning()
        button6 = MPushButton(text="Error Message").danger()
        button3.clicked.connect(
            functools.partial(
                self.slot_show_message,
                MMessage.info,
                {"text": "This is a normal message"},
            )
        )
        button4.clicked.connect(
            functools.partial(
                self.slot_show_message,
                MMessage.success,
                {"text": "Congratulations, you have succeeded!"},
            )
        )
        button5.clicked.connect(
            functools.partial(
                self.slot_show_message, MMessage.warning, {"text": "I warned you!"}
            )
        )
        button6.clicked.connect(
            functools.partial(
                self.slot_show_message, MMessage.error, {"text": "You failed!"}
            )
        )

        sub_lay1 = QtWidgets.QHBoxLayout()
        sub_lay1.addWidget(button3)
        sub_lay1.addWidget(button4)
        sub_lay1.addWidget(button5)
        sub_lay1.addWidget(button6)

        button_duration = MPushButton(text="show 5s Message")
        button_duration.clicked.connect(
            functools.partial(
                self.slot_show_message,
                MMessage.info,
                {"text": "This message will be displayed for 5 seconds", "duration": 5},
            )
        )
        button_closable = MPushButton(text="closable Message")
        button_closable.clicked.connect(
            functools.partial(
                self.slot_show_message,
                MMessage.info,
                {"text": "The message can be manually closed", "closable": True},
            )
        )
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("different type"))
        main_lay.addLayout(sub_lay1)
        main_lay.addWidget(
            MLabel(
                "Different message types: normal, success, warning, error. Default 2 seconds after disappearance"  # noqa: E501
            )
        )
        main_lay.addWidget(MDivider("set duration"))
        main_lay.addWidget(button_duration)
        main_lay.addWidget(
            MLabel("Custom duration, set duration value in config, unit is seconds")
        )

        main_lay.addWidget(MDivider("set closable"))
        main_lay.addWidget(button_closable)
        main_lay.addWidget(
            MLabel("Set whether it can be closed, set closable to True in config")
        )

        button_grp = MPushButtonGroup()
        button_grp.set_button_list(
            [
                {
                    "text": "set duration to 1s",
                    "clicked": functools.partial(
                        self.slot_set_config, MMessage.config, {"duration": 1}
                    ),
                },
                {
                    "text": "set duration to 10s",
                    "clicked": functools.partial(
                        self.slot_set_config, MMessage.config, {"duration": 10}
                    ),
                },
                {
                    "text": "set top to 5",
                    "clicked": functools.partial(
                        self.slot_set_config, MMessage.config, {"top": 5}
                    ),
                },
                {
                    "text": "set top to 50",
                    "clicked": functools.partial(
                        self.slot_set_config, MMessage.config, {"top": 50}
                    ),
                },
            ]
        )
        loading_button = MPushButton("Display a loading indicator")
        loading_button.clicked.connect(self.slot_show_loading)
        main_lay.addWidget(MDivider("set global setting"))
        main_lay.addWidget(button_grp)
        main_lay.addWidget(
            MLabel(
                "Global setting default duration (default 2 seconds); top (distance from parent top, default 24px)"  # noqa: E501
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
        msg = MMessage.loading("Loading...", parent=self)
        msg.sig_closed.connect(
            functools.partial(MMessage.success, "Loading success!", self)
        )


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = MessageExample()
        MTheme().apply(test)
        test.show()
