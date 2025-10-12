# pyright: reportRedeclaration=none
# ruff: noqa: N815 N802

from PySide6.QtCore import Property, QObject, Signal
from PySide6.QtGui import QFont, QGuiApplication

from .FluTools import FluTools
from .Singleton import Singleton

"""
The FluTextStyle class is used to define the style of text
"""


# noinspection PyCallingNonCallable,PyPep8Naming
@Singleton
class FluTextStyle(QObject):
    familyChanged = Signal()
    CaptionChanged = Signal()
    BodyChanged = Signal()
    BodyStrongChanged = Signal()
    SubtitleChanged = Signal()
    TitleChanged = Signal()
    TitleLargeChanged = Signal()
    DisplayChanged = Signal()

    def __init__(self):
        QObject.__init__(self, QGuiApplication.instance())
        self._family = QFont().defaultFamily()
        if FluTools().isWin():
            self._family = "Arial"

        caption = QFont()
        caption.setPixelSize(12)
        self._Caption = caption

        body = QFont()
        body.setPixelSize(13)
        self._Body = body

        body_strong = QFont()
        body_strong.setPixelSize(13)
        body_strong.setWeight(QFont.Weight.DemiBold)
        self._BodyStrong = body_strong

        subtitle = QFont()
        subtitle.setPixelSize(20)
        subtitle.setWeight(QFont.Weight.DemiBold)
        self._Subtitle = subtitle

        title = QFont()
        title.setPixelSize(28)
        title.setWeight(QFont.Weight.DemiBold)
        self._Title = title

        title_large = QFont()
        title_large.setPixelSize(40)
        title_large.setWeight(QFont.Weight.DemiBold)
        self._TitleLarge = title_large

        display = QFont()
        display.setPixelSize(68)
        display.setWeight(QFont.Weight.DemiBold)
        self._Display = display

    @Property(str, notify=familyChanged)
    def family(self):
        return self._family

    @family.setter
    def family(self, value: str):
        self._family = value
        self.familyChanged.emit()

    @Property(QFont, notify=CaptionChanged)
    def Caption(self):
        return self._Caption

    @Caption.setter
    def Caption(self, value: QFont):
        self._Caption = value
        self.CaptionChanged.emit()

    @Property(QFont, notify=BodyChanged)
    def Body(self):
        return self._Body

    @Body.setter
    def Body(self, value: QFont):
        self._Body = value
        self.BodyChanged.emit()

    @Property(QFont, notify=BodyStrongChanged)
    def BodyStrong(self):
        return self._BodyStrong

    @BodyStrong.setter
    def BodyStrong(self, value: QFont):
        self._BodyStrong = value
        self.BodyStrongChanged.emit()

    @Property(QFont, notify=SubtitleChanged)
    def Subtitle(self):
        return self._Subtitle

    @Subtitle.setter
    def Subtitle(self, value: QFont):
        self._Subtitle = value
        self.SubtitleChanged.emit()

    @Property(QFont, notify=TitleChanged)
    def Title(self):
        return self._Title

    @Title.setter
    def Title(self, value: QFont):
        self._Title = value
        self.TitleChanged.emit()

    @Property(QFont, notify=TitleLargeChanged)
    def TitleLarge(self):
        return self._TitleLarge

    @TitleLarge.setter
    def TitleLarge(self, value: QFont):
        self._TitleLarge = value
        self.TitleLargeChanged.emit()

    @Property(QFont, notify=DisplayChanged)
    def Display(self):
        return self._Display

    @Display.setter
    def Display(self, value: QFont):
        self._Display = value
        self.DisplayChanged.emit()
