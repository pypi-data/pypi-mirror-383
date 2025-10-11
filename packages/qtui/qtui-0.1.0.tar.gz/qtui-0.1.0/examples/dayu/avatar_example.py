from qtpy import QtCore, QtWidgets

from qtui.dayu.avatar import MAvatar
from qtui.dayu.divider import MDivider
from qtui.dayu.field_mixin import MFieldMixin
from qtui.dayu.label import MLabel
from qtui.dayu.push_button import MPushButton
from qtui.dayu.qt import MPixmap
from qtui.dayu.theme import MTheme


class AvatarExample(QtWidgets.QWidget, MFieldMixin):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Example for MAvatar")
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(MDivider("different size"))

        size_list = [
            ("Huge", MAvatar.huge),
            ("Large", MAvatar.large),
            ("Medium", MAvatar.medium),
            ("Small", MAvatar.small),
            ("Tiny", MAvatar.tiny),
        ]

        self.pix_map_list = [
            None,
            MPixmap("avatar.png"),
            MPixmap("app-maya.png"),
            MPixmap("app-nuke.png"),
            MPixmap("app-houdini.png"),
        ]
        form_lay = QtWidgets.QFormLayout()
        form_lay.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        for label, cls in size_list:
            h_lay = QtWidgets.QHBoxLayout()
            for image in self.pix_map_list:
                avatar_tmp = cls(image)
                h_lay.addWidget(avatar_tmp)
            h_lay.addStretch()
            form_lay.addRow(MLabel(label), h_lay)
        main_lay.addLayout(form_lay)
        self.register_field("image", None)
        main_lay.addWidget(MDivider("different image"))
        avatar = MAvatar()
        self.bind("image", avatar, "dayu_image")
        button = MPushButton(text="Change Avatar Image").primary()
        button.clicked.connect(self.slot_change_image)

        main_lay.addWidget(avatar)
        main_lay.addWidget(button)
        main_lay.addStretch()
        self.setLayout(main_lay)

    def slot_change_image(self):
        """Set the Avatar image random by data bind."""
        import random

        self.set_field("image", random.choice(self.pix_map_list))


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = AvatarExample()
        MTheme().apply(test)
        test.show()
