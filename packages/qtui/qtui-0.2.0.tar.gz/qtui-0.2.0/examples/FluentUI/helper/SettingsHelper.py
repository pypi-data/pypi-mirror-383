# ruff: noqa: N815 N802

from typing import Any

from PySide6.QtCore import QObject, QSettings, Slot
from PySide6.QtGui import QGuiApplication

from qtui.FluentUI import Singleton

from .. import PROJECT_ROOT


# noinspection PyPep8Naming
@Singleton
class SettingsHelper(QObject):
    def __init__(self):
        super().__init__(QGuiApplication.instance())
        self._settings = QSettings()
        ini_file_path = (PROJECT_ROOT / "settings.ini").as_posix()
        self._settings = QSettings(ini_file_path, QSettings.Format.IniFormat)

    def _save(self, key: str, val: Any):
        self._settings.setValue(key, val)

    def _get(self, key: str, default: Any):
        data = self._settings.value(key)
        if data is None:
            return default
        return data

    @Slot(result=int)
    def getDarkMode(self) -> int:
        return int(self._get("darkMode", 0))

    @Slot(int)
    def saveDarkMode(self, dark_mode: int):
        self._save("darkMode", dark_mode)

    @Slot(result=bool)
    def getUseSystemAppBar(self) -> bool:
        return bool(self._get("useSystemAppBar", "false") == "true")

    @Slot(bool)
    def saveUseSystemAppBar(self, use_system_app_bar: bool):
        self._save("useSystemAppBar", use_system_app_bar)

    @Slot(result=str)
    def getLanguage(self) -> str:
        return str(self._get("language", "en_US"))

    @Slot(str)
    def saveLanguage(self, language: str):
        self._save("language", language)
