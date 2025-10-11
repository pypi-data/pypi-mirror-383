from qtpy import QtCore, QtWidgets

from qtui.dayu.collapse import MCollapse
from qtui.dayu.label import MLabel
from qtui.dayu.types import MCollapseData


class CollapseExample(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Examples for MCollapse")
        self._init_ui()

    def _init_ui(self):
        label_1 = MLabel(
            "Steve Jobs was an American inventor, entrepreneur, and co-founder of Apple Inc. He was born on February 24, 1955, in San Francisco, California."  # noqa: E501
        )
        label_2 = MLabel(
            "Stephen Gary Wozniak was an American computer engineer who co-founded Apple Inc. with Steve Jobs. He studied at the University of Colorado and then transferred to the University of California, Berkeley, where he earned a degree in electrical engineering and computer science in 1987."  # noqa: E501
        )
        label_3 = MLabel(
            "Jonathan Ive is an industrial designer who is currently the designer and senior vice president of Apple Inc. He is a British knight."  # noqa: E501
        )
        label_1.setWordWrap(True)
        label_2.setWordWrap(True)
        label_3.setWordWrap(True)
        section_list = [
            MCollapseData(title="Steve Jobs", expand=True, content=label_1),
            MCollapseData(
                title="This is a closable collapse item",
                expand=True,
                content=MLabel("This is a closable collapse item"),
                closable=True,
            ),
            MCollapseData(title="Stephen Gary Wozniak", expand=True, content=label_2),
        ]

        main_lay = QtWidgets.QVBoxLayout()
        main_lay.setSpacing(1)
        for section in section_list:
            section_item = MCollapse(**section)
            section_item.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
            main_lay.addWidget(section_item)
        main_lay.addStretch()
        main_lay.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_lay)


if __name__ == "__main__":
    from qtui.dayu.qt import application
    from qtui.dayu.theme import MTheme

    with application() as app:
        test = CollapseExample()
        MTheme().apply(test)
        test.show()
