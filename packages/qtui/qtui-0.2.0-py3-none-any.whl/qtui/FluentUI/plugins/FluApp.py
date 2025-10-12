"""
The FluApp class
"""

# pyright: reportRedeclaration=none, reportUnknownMemberType=none, reportUnknownVariableType=none, reportAttributeAccessIssue=none, reportUnknownArgumentType=none
# ruff: noqa: N815 N802

from PySide6.QtCore import Property, QLocale, QObject, QTranslator, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import qmlEngine

from .FluentIconDef import FluentIcons
from .Singleton import Singleton


@Singleton
class FluApp(QObject):
    useSystemAppBarChanged = Signal()
    windowIconChanged = Signal()
    localeChanged = Signal()
    launcherChanged = Signal()

    def __init__(self):
        QObject.__init__(self)
        self._engine = None
        self._translator = None
        self._useSystemAppBar: bool = False
        self._windowIcon = None
        self._locale = None
        self._launcher = None

    @Property(QObject, notify=launcherChanged)
    def launcher(self) -> QObject | None:
        return self._launcher

    @launcher.setter
    def launcher(self, value: QObject | None):
        self._launcher = value
        self.launcherChanged.emit()

    @Property(bool, notify=useSystemAppBarChanged)
    def useSystemAppBar(self) -> bool:
        return self._useSystemAppBar

    @useSystemAppBar.setter
    def useSystemAppBar(self, value: bool):
        self._useSystemAppBar = value
        self.useSystemAppBarChanged.emit()

    @Property(str, notify=windowIconChanged)
    def windowIcon(self) -> str | None:
        return self._windowIcon

    @windowIcon.setter
    def windowIcon(self, value: str | None):
        self._windowIcon = value
        self.windowIconChanged.emit()

    @Property(QLocale, notify=localeChanged)
    def locale(self) -> QLocale | None:
        return self._locale

    @locale.setter
    def locale(self, value: QLocale):
        self._locale = value
        self.localeChanged.emit()

    @Slot(QObject)
    @Slot(QObject, QLocale)
    def init(self, launcher: QObject, locale: QLocale | None = None):
        self._launcher = launcher
        if locale is None:
            locale = QLocale.system()
        self._locale = locale
        self._engine = qmlEngine(launcher)
        translator = QTranslator()
        self._translator = translator
        QGuiApplication.installTranslator(self._translator)
        ui_languages = self._locale.uiLanguages()
        for lang in ui_languages:
            name = "FluentUI_" + QLocale(lang).name()
            if (
                self._translator.load(":/FluentUI/i18n/" + name)
                and self._engine is not None
            ):
                self._engine.retranslate()
                break

    # noinspection PyUnresolvedReferences
    @Slot(result=list)
    @Slot(str, result=list)
    def iconData(self, keyword: str | None = None) -> list[dict[str, str | int]]:
        if not keyword:
            keyword = ""
        arr: list[dict[str, str | int]] = []
        enum_type = FluentIcons.staticMetaObject.enumerator(
            FluentIcons.staticMetaObject.indexOfEnumerator("Type")
        )

        for i in range(enum_type.keyCount()):
            name = str(enum_type.key(i))
            icon = enum_type.value(i)
            if keyword in name:
                obj = {"name": name, "icon": icon}
                arr.append(obj)
        return arr
