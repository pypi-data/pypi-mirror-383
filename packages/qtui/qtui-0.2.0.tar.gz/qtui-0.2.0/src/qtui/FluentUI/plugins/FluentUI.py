"""
The FluentUI.py module contains classes and functions to interact with FluentUI
"""

# pyright: reportUnknownMemberType=none, reportUnknownArgumentType=none, reportAttributeAccessIssue=none, reportCallIssue=none, reportArgumentType=none
# ruff: noqa: N815 N802

from PySide6.QtCore import QUrl, qDebug
from PySide6.QtQml import (
    QQmlApplicationEngine,
    qmlRegisterSingletonType,
    qmlRegisterType,
    qmlRegisterUncreatableMetaObject,
)

from .. import resource_rc as rc
from .Def import (
    FluCalendarViewType,
    FluContentDialogType,
    FluNavigationViewType,
    FluPageType,
    FluSheetType,
    FluStatusLayoutType,
    FluTabViewType,
    FluThemeType,
    FluTimelineType,
    FluTimePickerType,
    FluTreeViewType,
    FluWindowType,
)
from .FluApp import FluApp
from .FluCaptcha import FluCaptcha
from .FluColors import FluColors
from .FluentIconDef import FluentIcons
from .FluFrameless import FluFrameless
from .FluHotkey import FluHotkey
from .FluQrCodeItem import FluQrCodeItem
from .FluRectangle import FluRectangle
from .FluTableModel import FluTableModel
from .FluTableSortProxyModel import FluTableSortProxyModel
from .FluTextStyle import FluTextStyle
from .FluTheme import FluTheme
from .FluTools import FluTools
from .FluTreeModel import FluTreeModel, FluTreeNode
from .FluWatermark import FluWatermark

_major = 1
_minor = 0
_uri = "FluentUI"


# noinspection PyPep8Naming
def registerTypes(engine: QQmlApplicationEngine):
    qDebug(f"Load the resource '{rc.__name__}'")
    _registerTypes(_uri, _major, _minor)
    _initializeEngine(engine)


# noinspection PyUnresolvedReferences,PyTypeChecker,PyPep8Naming,PyCallingNonCallable
def _registerTypes(uri: str, major: int, minor: int):
    qmlRegisterType(FluTreeNode, uri, major, minor, "FluTreeNode")  # pyright: ignore[reportCallIssue, reportArgumentType]
    qmlRegisterType(FluTreeModel, uri, major, minor, "FluTreeModel")
    qmlRegisterType(FluTableModel, uri, major, minor, "FluTableModel")
    qmlRegisterType(FluRectangle, uri, major, minor, "FluRectangle")
    qmlRegisterType(FluFrameless, uri, major, minor, "FluFrameless")
    qmlRegisterType(FluWatermark, uri, major, minor, "FluWatermark")
    qmlRegisterType(FluQrCodeItem, uri, major, minor, "FluQrCodeItem")
    qmlRegisterType(FluCaptcha, uri, major, minor, "FluCaptcha")
    qmlRegisterType(FluHotkey, uri, major, minor, "FluHotkey")
    qmlRegisterType(FluTableSortProxyModel, uri, major, minor, "FluTableSortProxyModel")

    qmlRegisterType(
        QUrl("qrc:/Controls/FluAcrylic.qml"), uri, major, minor, "FluAcrylic"
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluAppBar.qml"), uri, major, minor, "FluAppBar")
    qmlRegisterType(QUrl("qrc:/Controls/FluFrame.qml"), uri, major, minor, "FluFrame")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluAutoSuggestBox.qml"),
        uri,
        major,
        minor,
        "FluAutoSuggestBox",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluBadge.qml"), uri, major, minor, "FluBadge")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluBreadcrumbBar.qml"),
        uri,
        major,
        minor,
        "FluBreadcrumbBar",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluButton.qml"), uri, major, minor, "FluButton")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluCalendarPicker.qml"),
        uri,
        major,
        minor,
        "FluCalendarPicker",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluCarousel.qml"), uri, major, minor, "FluCarousel"
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluChart.qml"), uri, major, minor, "FluChart")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluCheckBox.qml"), uri, major, minor, "FluCheckBox"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluColorPicker.qml"),
        uri,
        major,
        minor,
        "FluColorPicker",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluComboBox.qml"), uri, major, minor, "FluComboBox"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluContentDialog.qml"),
        uri,
        major,
        minor,
        "FluContentDialog",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluContentPage.qml"),
        uri,
        major,
        minor,
        "FluContentPage",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluControl.qml"), uri, major, minor, "FluControl"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluCopyableText.qml"),
        uri,
        major,
        minor,
        "FluCopyableText",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluDatePicker.qml"),
        uri,
        major,
        minor,
        "FluDatePicker",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluDivider.qml"), uri, major, minor, "FluDivider"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluDropDownButton.qml"),
        uri,
        major,
        minor,
        "FluDropDownButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluExpander.qml"), uri, major, minor, "FluExpander"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluFilledButton.qml"),
        uri,
        major,
        minor,
        "FluFilledButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluFlipView.qml"), uri, major, minor, "FluFlipView"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluFocusRectangle.qml"),
        uri,
        major,
        minor,
        "FluFocusRectangle",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluIcon.qml"), uri, major, minor, "FluIcon")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluIconButton.qml"),
        uri,
        major,
        minor,
        "FluIconButton",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluImage.qml"), uri, major, minor, "FluImage")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluImageButton.qml"),
        uri,
        major,
        minor,
        "FluImageButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluInfoBar.qml"), uri, major, minor, "FluInfoBar"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluItemDelegate.qml"),
        uri,
        major,
        minor,
        "FluItemDelegate",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluMenu.qml"), uri, major, minor, "FluMenu")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluMenuBar.qml"), uri, major, minor, "FluMenuBar"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluMenuBarItem.qml"),
        uri,
        major,
        minor,
        "FluMenuBarItem",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluMenuItem.qml"), uri, major, minor, "FluMenuItem"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluMenuSeparator.qml"),
        uri,
        major,
        minor,
        "FluMenuSeparator",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluMultilineTextBox.qml"),
        uri,
        major,
        minor,
        "FluMultilineTextBox",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluNavigationView.qml"),
        uri,
        major,
        minor,
        "FluNavigationView",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluObject.qml"), uri, major, minor, "FluObject")
    qmlRegisterType(QUrl("qrc:/Controls/FluPage.qml"), uri, major, minor, "FluPage")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPagination.qml"),
        uri,
        major,
        minor,
        "FluPagination",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPaneItem.qml"), uri, major, minor, "FluPaneItem"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPaneItemEmpty.qml"),
        uri,
        major,
        minor,
        "FluPaneItemEmpty",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPaneItemExpander.qml"),
        uri,
        major,
        minor,
        "FluPaneItemExpander",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPaneItemHeader.qml"),
        uri,
        major,
        minor,
        "FluPaneItemHeader",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPaneItemSeparator.qml"),
        uri,
        major,
        minor,
        "FluPaneItemSeparator",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPasswordBox.qml"),
        uri,
        major,
        minor,
        "FluPasswordBox",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluPivot.qml"), uri, major, minor, "FluPivot")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluPivotItem.qml"),
        uri,
        major,
        minor,
        "FluPivotItem",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluPopup.qml"), uri, major, minor, "FluPopup")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluProgressBar.qml"),
        uri,
        major,
        minor,
        "FluProgressBar",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluProgressRing.qml"),
        uri,
        major,
        minor,
        "FluProgressRing",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluQRCode.qml"), uri, major, minor, "FluQRCode")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluRadioButton.qml"),
        uri,
        major,
        minor,
        "FluRadioButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluRadioButtons.qml"),
        uri,
        major,
        minor,
        "FluRadioButtons",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluRatingControl.qml"),
        uri,
        major,
        minor,
        "FluRatingControl",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluRemoteLoader.qml"),
        uri,
        major,
        minor,
        "FluRemoteLoader",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluScrollBar.qml"),
        uri,
        major,
        minor,
        "FluScrollBar",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluScrollIndicator.qml"),
        uri,
        major,
        minor,
        "FluScrollIndicator",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluScrollablePage.qml"),
        uri,
        major,
        minor,
        "FluScrollablePage",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluShadow.qml"), uri, major, minor, "FluShadow")
    qmlRegisterType(QUrl("qrc:/Controls/FluSlider.qml"), uri, major, minor, "FluSlider")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluSpinBox.qml"), uri, major, minor, "FluSpinBox"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluStatusLayout.qml"),
        uri,
        major,
        minor,
        "FluStatusLayout",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTabView.qml"), uri, major, minor, "FluTabView"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTableView.qml"),
        uri,
        major,
        minor,
        "FluTableView",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluText.qml"), uri, major, minor, "FluText")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTextBox.qml"), uri, major, minor, "FluTextBox"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTextBoxBackground.qml"),
        uri,
        major,
        minor,
        "FluTextBoxBackground",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTextBoxMenu.qml"),
        uri,
        major,
        minor,
        "FluTextBoxMenu",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTextButton.qml"),
        uri,
        major,
        minor,
        "FluTextButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTimePicker.qml"),
        uri,
        major,
        minor,
        "FluTimePicker",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTimeline.qml"), uri, major, minor, "FluTimeline"
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluToggleButton.qml"),
        uri,
        major,
        minor,
        "FluToggleButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluToggleSwitch.qml"),
        uri,
        major,
        minor,
        "FluToggleSwitch",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTooltip.qml"), uri, major, minor, "FluTooltip"
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluTour.qml"), uri, major, minor, "FluTour")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluTreeView.qml"), uri, major, minor, "FluTreeView"
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluWindow.qml"), uri, major, minor, "FluWindow")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluWindowDialog.qml"),
        uri,
        major,
        minor,
        "FluWindowDialog",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluRangeSlider.qml"),
        uri,
        major,
        minor,
        "FluRangeSlider",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluStaggeredLayout.qml"),
        uri,
        major,
        minor,
        "FluStaggeredLayout",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluProgressButton.qml"),
        uri,
        major,
        minor,
        "FluProgressButton",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluLoadingButton.qml"),
        uri,
        major,
        minor,
        "FluLoadingButton",
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluClip.qml"), uri, major, minor, "FluClip")
    qmlRegisterType(QUrl("qrc:/Controls/FluLoader.qml"), uri, major, minor, "FluLoader")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluShortcutPicker.qml"),
        uri,
        major,
        minor,
        "FluShortcutPicker",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluSplitLayout.qml"),
        uri,
        major,
        minor,
        "FluSplitLayout",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluWindowResultLauncher.qml"),
        uri,
        major,
        minor,
        "FluWindowResultLauncher",
    )
    qmlRegisterType(
        QUrl("qrc:/Controls/FluLauncher.qml"), uri, major, minor, "FluLauncher"
    )
    qmlRegisterType(QUrl("qrc:/Controls/FluEvent.qml"), uri, major, minor, "FluEvent")
    qmlRegisterType(QUrl("qrc:/Controls/FluSheet.qml"), uri, major, minor, "FluSheet")
    qmlRegisterType(
        QUrl("qrc:/Controls/FluGroupBox.qml"), uri, major, minor, "FluGroupBox"
    )
    qmlRegisterSingletonType(
        QUrl("qrc:/Controls/FluRouter.qml"), uri, major, minor, "FluRouter"
    )
    qmlRegisterSingletonType(
        QUrl("qrc:/Controls/FluEventBus.qml"), uri, major, minor, "FluEventBus"
    )

    qmlRegisterUncreatableMetaObject(
        FluentIcons.staticMetaObject,
        uri,
        major,
        minor,
        "FluentIcons",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluThemeType.staticMetaObject,
        uri,
        major,
        minor,
        "FluThemeType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluPageType.staticMetaObject,
        uri,
        major,
        minor,
        "FluPageType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluWindowType.staticMetaObject,
        uri,
        major,
        minor,
        "FluWindowType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluTreeViewType.staticMetaObject,
        uri,
        major,
        minor,
        "FluTreeViewType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluStatusLayoutType.staticMetaObject,
        uri,
        major,
        minor,
        "FluStatusLayoutType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluContentDialogType.staticMetaObject,
        uri,
        major,
        minor,
        "FluContentDialogType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluTimePickerType.staticMetaObject,
        uri,
        major,
        minor,
        "FluTimePickerType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluCalendarViewType.staticMetaObject,
        uri,
        major,
        minor,
        "FluCalendarViewType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluTabViewType.staticMetaObject,
        uri,
        major,
        minor,
        "FluTabViewType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluNavigationViewType.staticMetaObject,
        uri,
        major,
        minor,
        "FluNavigationViewType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluTimelineType.staticMetaObject,
        uri,
        major,
        minor,
        "FluTimelineType",
        "Access to enums & flags only",
    )
    qmlRegisterUncreatableMetaObject(
        FluSheetType.staticMetaObject,
        uri,
        major,
        minor,
        "FluSheetType",
        "Access to enums & flags only",
    )


# noinspection PyPep8Naming,PyUnusedLocal
def _initializeEngine(engine: QQmlApplicationEngine):
    engine.rootContext().setContextProperty("FluTools", FluTools())
    engine.rootContext().setContextProperty("FluApp", FluApp())
    engine.rootContext().setContextProperty("FluTheme", FluTheme())
    engine.rootContext().setContextProperty("FluTextStyle", FluTextStyle())
    engine.rootContext().setContextProperty("FluColors", FluColors())
