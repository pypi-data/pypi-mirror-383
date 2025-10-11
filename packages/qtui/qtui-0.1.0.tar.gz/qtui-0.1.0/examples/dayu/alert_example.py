import functools

from qtpy import QtWidgets

from qtui.dayu.alert import MAlert
from qtui.dayu.button_group import MPushButtonGroup
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.types import MButtonGroupData


class AlertExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Example for MAlert")
        main_lay = QtWidgets.QVBoxLayout()
        self.setLayout(main_lay)
        main_lay.addWidget(MDivider("different type"))
        main_lay.addWidget(MAlert(text="Information Message", parent=self).info())
        main_lay.addWidget(MAlert(text="Success Message", parent=self).success())
        main_lay.addWidget(MAlert(text="Warning Message", parent=self).warning())
        main_lay.addWidget(MAlert(text="Error Message", parent=self).error())

        closable_alert = MAlert("Some Message", parent=self).closable()

        main_lay.addWidget(MLabel("Different Alert Types"))
        main_lay.addWidget(MDivider("closable"))
        main_lay.addWidget(closable_alert)
        main_lay.addWidget(MDivider("data bind"))
        self.register_field("msg", "")
        self.register_field("msg_type", MAlert.AlertType.Info)

        data_bind_alert = MAlert(parent=self)
        data_bind_alert.set_closable(True)

        self.bind("msg", data_bind_alert, "dayu_text")
        self.bind("msg_type", data_bind_alert, "dayu_type")
        button_grp = MPushButtonGroup()
        button_grp.set_button_list(
            [
                MButtonGroupData(
                    text="error",
                    clicked=functools.partial(
                        self.slot_change_alert,
                        "password is wrong",
                        MAlert.AlertType.Error,
                    ),
                ),
                MButtonGroupData(
                    text="success",
                    clicked=functools.partial(
                        self.slot_change_alert,
                        "login success",
                        MAlert.AlertType.Success,
                    ),
                ),
                MButtonGroupData(
                    text="no more error",
                    clicked=functools.partial(
                        self.slot_change_alert,
                        "",
                        MAlert.AlertType.Info,
                    ),
                ),
            ]
        )
        main_lay.addWidget(button_grp)
        main_lay.addWidget(data_bind_alert)
        main_lay.addStretch()

    def slot_change_alert(self, alert_text: str, alert_type: MAlert.AlertType):
        self.set_field("msg_type", alert_type)
        self.set_field("msg", alert_text)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = AlertExample()
        MTheme().apply(test)
        test.show()
