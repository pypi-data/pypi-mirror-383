# pyright: reportRedeclaration=none, reportAttributeAccessIssue=none
# ruff: noqa: N815 N802

from PySide6.QtCore import Property, QObject, Qt, Signal
from PySide6.QtGui import QGuiApplication, QKeySequence, QShortcut


# noinspection PyPep8Naming
class FluHotkey(QObject):
    sequenceChanged = Signal()
    nameChanged = Signal()
    isRegisteredChanged = Signal()
    activated = Signal()

    def __init__(self):
        QObject.__init__(self)
        self._sequence: str = ""
        self._name: str = ""
        self._isRegistered: bool = False
        self._shortcut: QShortcut | None = None

        # QApplication 인스턴스 확인 및 취득
        self._app = QGuiApplication.instance()

        def handleSequenceChanged():
            # 이전 단축키 제거
            if self._shortcut:
                self._shortcut.setEnabled(False)
                self._shortcut.deleteLater()
                self._shortcut = None

            try:
                if not self._sequence:
                    self.isRegistered = False
                    return

                # Qt 단축키 형식으로 변환
                qt_sequence = self._convert_to_qt_sequence(self._sequence)

                # 전역 단축키 등록
                if self._app:
                    self._shortcut = QShortcut(QKeySequence(qt_sequence), self._app)
                    self._shortcut.activated.connect(self.hotkeyCallback)
                    self._shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
                    self.isRegistered = True
            except Exception:
                self.isRegistered = False

        self.sequenceChanged.connect(lambda: handleSequenceChanged())

    def _convert_to_qt_sequence(self, sequence: str):
        """키보드 라이브러리 형식의 단축키를 Qt 형식으로 변환합니다."""
        # macOS에서는 cmd를 Meta로 처리
        sequence = sequence.replace("cmd", "Meta")
        sequence = sequence.replace("command", "Meta")
        sequence = sequence.replace("alt", "Alt")
        sequence = sequence.replace("ctrl", "Ctrl")
        sequence = sequence.replace("control", "Ctrl")
        sequence = sequence.replace("shift", "Shift")

        # + 기호 주변에 공백 제거
        sequence = sequence.replace(" + ", "+")
        sequence = sequence.replace(" +", "+")
        sequence = sequence.replace("+ ", "+")

        return sequence

    def hotkeyCallback(self):
        self.activated.emit()

    @Property(bool, notify=isRegisteredChanged)
    def isRegistered(self):
        return self._isRegistered

    @isRegistered.setter
    def isRegistered(self, value: bool):
        if self._isRegistered != value:
            self._isRegistered = value
            self.isRegisteredChanged.emit()

    @Property(str, notify=nameChanged)
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if self._name != value:
            self._name = value
            self.nameChanged.emit()

    @Property(str, notify=sequenceChanged)
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value: str):
        if self._sequence != value:
            self._sequence = value
            self.sequenceChanged.emit()
