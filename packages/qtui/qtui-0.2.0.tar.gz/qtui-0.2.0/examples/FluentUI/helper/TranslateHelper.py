# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from PySide6.QtCore import Property, QObject, QTranslator, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlEngine

from qtui.FluentUI import Singleton

from ..helper.SettingsHelper import SettingsHelper


@Singleton
class TranslateHelper(QObject):
    currentChanged = Signal()
    languagesChanged = Signal()

    def __init__(self):
        QObject.__init__(self, QGuiApplication.instance())
        self._engine = None
        self._translator = None
        self._languages = ["en_US"]
        self._current = SettingsHelper().getLanguage()

    @Property(str, notify=currentChanged)
    def current(self) -> str:
        return self._current

    @current.setter
    def current(self, value: str):
        self._current = value
        self.currentChanged.emit()

    @Property(list, notify=languagesChanged)
    def languages(self) -> list[str]:
        return self._languages

    @languages.setter
    def languages(self, value: list[str]):
        self._languages = value
        self.languagesChanged.emit()

    def init(self, engine: QQmlEngine):
        self._engine = engine
        self._translator = QTranslator()
        QGuiApplication.installTranslator(self._translator)
        if self._translator.load(f":/example/i18n/example_{self._current}.qm"):
            self._engine.retranslate()
