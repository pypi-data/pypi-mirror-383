from qtpy import QtWidgets

from qtui.dayu.card import MCard, MMetaCard
from qtui.dayu.divider import MDivider
from qtui.dayu.flow_layout import MFlowLayout
from qtui.dayu.label import MLabel
from qtui.dayu.qt import MPixmap
from qtui.dayu.theme import MTheme
from qtui.dayu.types import MCardData, MMetaCardData


class CardExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MCard")
        self._init_ui()

    def _init_ui(self):
        basic_card_lay = MFlowLayout()
        basic_card_lay.setSpacing(20)
        for setting in [
            MCardData(
                title="",
            ),
            MCardData(title="Card Title", size=MTheme().small),
            MCardData(title="Card Title", image=MPixmap("app-houdini.png")),
            MCardData(
                title="Card Title",
                extra=True,
                image=MPixmap("app-houdini.png"),
            ),
            MCardData(
                title="Card Title",
                extra=True,
                extra_menus=[("extra", lambda: print("extra"))],
            ),
        ]:
            card_0 = MCard(**setting)
            content_widget_0 = QtWidgets.QWidget()
            content_lay_0 = QtWidgets.QVBoxLayout()
            content_lay_0.setContentsMargins(15, 15, 15, 15)
            content_widget_0.setLayout(content_lay_0)
            for i in range(4):
                content_lay_0.addWidget(MLabel(f"Card Content {i + 1}"))
            card_0.set_content(content_widget_0)
            card_0.set_title("")
            card_0.set_title(setting.get("title", ""))

            basic_card_lay.addWidget(card_0)

        meta_card_lay = MFlowLayout()
        meta_card_lay.setSpacing(20)
        for setting in [
            MMetaCardData(
                title="Houdini",
                description=(
                    "Side Effects Software's flagship product, "
                    "an effective tool for creating advanced visual effects"
                ),
                avatar=MPixmap("user_line.svg"),
                cover=MPixmap("app-houdini.png"),
            ),
            MMetaCardData(
                title="Autodesk Maya",
                description=(
                    "The world's leading software application for 3D digital "
                    "animation and visual effects"
                ),
                cover=MPixmap("app-maya.png"),
            ),
        ]:
            meta_card = MMetaCard(**setting)
            meta_card_lay.addWidget(meta_card)

        task_card_lay = QtWidgets.QVBoxLayout()
        task_card_lay.setSpacing(10)
        for setting in [
            MMetaCardData(
                title="Task A",
                description="demo pl_0010 Animation \n2019/04/01 - 2019/04/09",
                avatar=MPixmap("success_line.svg", MTheme().success_color),
                extra=True,
                extra_menus=[("extra", lambda: print("extra"))],
            ),
            MMetaCardData(
                title="Task B",
                description="#2 closed by xiao hua.",
                avatar=MPixmap("error_line.svg", MTheme().error_color),
            ),
            MMetaCardData(
                title="Task C",
                description="#3 closed by xiao hua.",
                avatar=MPixmap("warning_line.svg", MTheme().warning_color),
            ),
        ] * 5:
            meta_card = MMetaCard(**setting)
            task_card_lay.addWidget(meta_card)

        left_lay = QtWidgets.QVBoxLayout()
        left_lay.addWidget(MDivider("Basic"))
        left_lay.addLayout(basic_card_lay)
        left_lay.addWidget(MDivider("Meta E-Commerce Example"))
        left_lay.addLayout(meta_card_lay)
        left_lay.addStretch()
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_lay)

        right_lay = QtWidgets.QVBoxLayout()
        right_lay.addWidget(MDivider("Meta Task Item Example"))
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        task_widget = QtWidgets.QWidget()
        task_widget.setLayout(task_card_lay)
        scroll.setWidget(task_widget)

        right_lay.addWidget(scroll)
        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_lay)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 80)
        splitter.setStretchFactor(1, 20)
        main_lay = QtWidgets.QVBoxLayout()
        main_lay.addWidget(splitter)
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = CardExample()
        MTheme().apply(test)
        test.show()
