# coding:utf-8
# 标准库导入
import sys
from typing import Union

# 第三方库导入
from PySide6.QtGui import QIcon, QColor, QPainter
from PySide6.QtCore import Qt, QRect, QSize
from qframelesswindow import TitleBarBase
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication

from ..common.icon import FluentIconBase
from ..common.config import qconfig
from ..common.router import qrouter
from .stacked_widget import StackedWidget
from .fluent_title_bar import SplitTitleBar, FluentTitleBar, MSFluentTitleBar
from ..common.animation import BackgroundAnimationWidget
from ..common.style_sheet import FluentStyleSheet, isDarkTheme
from ..components.navigation import (
    NavigationBar,
    NavigationInterface,
    NavigationTreeWidget,
    NavigationItemPosition,
    NavigationBarPushButton,
)
from ..components.widgets.frameless_window import FramelessWindow


class FluentWindowBase(BackgroundAnimationWidget, FramelessWindow):
    """Fluent window base class"""

    def __init__(self, parent=None):
        self._isMicaEnabled = False
        self._lightBackgroundColor = QColor(240, 244, 249)
        self._darkBackgroundColor = QColor(32, 32, 32)
        super().__init__(parent=parent)

        self.hBoxLayout = QHBoxLayout(self)
        self.stackedWidget = StackedWidget(self)
        self.navigationInterface = None

        # initialize layout
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        FluentStyleSheet.FLUENT_WINDOW.apply(self.stackedWidget)

        # enable mica effect on win11
        self.setMicaEffectEnabled(True)

        # show system title bar buttons on macOS
        if sys.platform == "darwin":
            self.setSystemTitleBarButtonVisible(True)

        qconfig.themeChangedFinished.connect(self._onThemeChangedFinished)

    def addSubInterface(
        self,
        interface: QWidget,
        icon: Union[FluentIconBase, QIcon, str],
        text: str,
        position=NavigationItemPosition.TOP,
    ):
        """add sub interface"""
        raise NotImplementedError

    def switchTo(self, interface: QWidget):
        self.stackedWidget.setCurrentWidget(interface, popOut=False)

    def _onCurrentInterfaceChanged(self, index: int):
        widget = self.stackedWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

        self._updateStackedBackground()

    def _updateStackedBackground(self):
        isTransparent = self.stackedWidget.currentWidget().property("isStackedTransparent")
        if bool(self.stackedWidget.property("isTransparent")) == isTransparent:
            return

        self.stackedWidget.setProperty("isTransparent", isTransparent)
        self.stackedWidget.setStyle(QApplication.style())

    def setCustomBackgroundColor(self, light, dark):
        """set custom background color

        Parameters
        ----------
        light, dark: QColor | Qt.GlobalColor | str
            background color in light/dark theme mode
        """
        self._lightBackgroundColor = QColor(light)
        self._darkBackgroundColor = QColor(dark)
        self._updateBackgroundColor()

    def _normalBackgroundColor(self):
        if not self.isMicaEffectEnabled():
            return self._darkBackgroundColor if isDarkTheme() else self._lightBackgroundColor

        return QColor(0, 0, 0, 0)

    def _onThemeChangedFinished(self):
        if self.isMicaEffectEnabled():
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.backgroundColor)
        painter.drawRect(self.rect())

    def setMicaEffectEnabled(self, isEnabled: bool):
        """set whether the mica effect is enabled, only available on Win11"""
        if sys.platform != "win32" or sys.getwindowsversion().build < 22000:
            return

        self._isMicaEnabled = isEnabled

        if isEnabled:
            self.windowEffect.setMicaEffect(self.winId(), isDarkTheme())
        else:
            self.windowEffect.removeBackgroundEffect(self.winId())

        self.setBackgroundColor(self._normalBackgroundColor())

    def isMicaEffectEnabled(self):
        return self._isMicaEnabled

    def systemTitleBarRect(self, size: QSize) -> QRect:
        """Returns the system title bar rect, only works for macOS

        Parameters
        ----------
        size: QSize
            original system title bar rect
        """
        return QRect(size.width() - 75, 0 if self.isFullScreen() else 9, 75, size.height())

    def setTitleBar(self, titleBar):
        super().setTitleBar(titleBar)

        # hide title bar buttons on macOS
        if sys.platform == "darwin" and self.isSystemButtonVisible() and isinstance(titleBar, TitleBarBase):
            titleBar.minBtn.hide()
            titleBar.maxBtn.hide()
            titleBar.closeBtn.hide()


class FluentWindow(FluentWindowBase):
    """Fluent window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitleBar(FluentTitleBar(self))

        self.navigationInterface = NavigationInterface(self, showReturnButton=True)
        self.widgetLayout = QHBoxLayout()

        # initialize layout
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackedWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)
        self.titleBar.raise_()

    def addSubInterface(
        self,
        interface: QWidget,
        icon: Union[FluentIconBase, QIcon, str],
        text: str,
        position=NavigationItemPosition.TOP,
        parent=None,
        isTransparent=False,
    ) -> NavigationTreeWidget:
        """add sub interface, the object name of `interface` should be set already
        before calling this method

        Parameters
        ----------
        interface: QWidget
            the subinterface to be added

        icon: FluentIconBase | QIcon | str
            the icon of navigation item

        text: str
            the text of navigation item

        position: NavigationItemPosition
            the position of navigation item

        parent: QWidget
            the parent of navigation item

        isTransparent: bool
            whether to use transparent background
        """
        if not interface.objectName():
            raise ValueError("The object name of `interface` can't be empty string.")
        if parent and not parent.objectName():
            raise ValueError("The object name of `parent` can't be empty string.")

        interface.setProperty("isStackedTransparent", isTransparent)
        self.stackedWidget.addWidget(interface)

        # add navigation item
        routeKey = interface.objectName()
        item = self.navigationInterface.addItem(
            routeKey=routeKey,
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parent.objectName() if parent else None,
        )

        # initialize selected item
        if self.stackedWidget.count() == 1:
            self.stackedWidget.currentChanged.connect(self._onCurrentInterfaceChanged)
            self.navigationInterface.setCurrentItem(routeKey)
            qrouter.setDefaultRouteKey(self.stackedWidget, routeKey)

        self._updateStackedBackground()

        return item

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


class MSFluentWindow(FluentWindowBase):
    """Fluent window in Microsoft Store style"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitleBar(MSFluentTitleBar(self))

        self.navigationInterface = NavigationBar(self)

        # initialize layout
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackedWidget, 1)

        self.titleBar.raise_()
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

    def addSubInterface(
        self,
        interface: QWidget,
        icon: Union[FluentIconBase, QIcon, str],
        text: str,
        selectedIcon=None,
        position=NavigationItemPosition.TOP,
        isTransparent=False,
    ) -> NavigationBarPushButton:
        """add sub interface, the object name of `interface` should be set already
        before calling this method

        Parameters
        ----------
        interface: QWidget
            the subinterface to be added

        icon: FluentIconBase | QIcon | str
            the icon of navigation item

        text: str
            the text of navigation item

        selectedIcon: str | QIcon | FluentIconBase
            the icon of navigation item in selected state

        position: NavigationItemPosition
            the position of navigation item
        """
        if not interface.objectName():
            raise ValueError("The object name of `interface` can't be empty string.")

        interface.setProperty("isStackedTransparent", isTransparent)
        self.stackedWidget.addWidget(interface)

        # add navigation item
        routeKey = interface.objectName()
        item = self.navigationInterface.addItem(
            routeKey=routeKey,
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

        if self.stackedWidget.count() == 1:
            self.stackedWidget.currentChanged.connect(self._onCurrentInterfaceChanged)
            self.navigationInterface.setCurrentItem(routeKey)
            qrouter.setDefaultRouteKey(self.stackedWidget, routeKey)

        self._updateStackedBackground()

        return item


class SplitFluentWindow(FluentWindow):
    """Fluent window with split style"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitleBar(SplitTitleBar(self))

        if sys.platform == "darwin":
            self.titleBar.setFixedHeight(48)

        self.widgetLayout.setContentsMargins(0, 0, 0, 0)

        self.titleBar.raise_()
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)


class FluentBackgroundTheme:
    """Fluent background theme"""

    DEFAULT = (QColor(243, 243, 243), QColor(32, 32, 32))  # light, dark
    DEFAULT_BLUE = (QColor(240, 244, 249), QColor(25, 33, 42))
