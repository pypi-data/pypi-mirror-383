# coding:utf-8
# 标准库导入
from enum import Enum
from typing import Dict, Union

# 第三方库导入
from PySide6.QtGui import QIcon, QColor, QPainterPath, QResizeEvent
from PySide6.QtCore import Qt, QRect, QSize, QEvent, QPoint, Signal, QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QApplication

from ...common.icon import FluentIcon as FIF
from ...common.icon import FluentIconBase
from ...common.router import qrouter
from ..widgets.flyout import Flyout, FlyoutViewBase, FlyoutAnimationType, SlideRightFlyoutAnimationManager
from ..widgets.tool_tip import ToolTipFilter
from .navigation_widget import (
    NavigationWidget,
    NavigationSeparator,
    NavigationFlyoutMenu,
    NavigationToolButton,
    NavigationTreeWidget,
    NavigationTreeWidgetBase,
)
from ...common.style_sheet import FluentStyleSheet, isDarkTheme
from ..widgets.scroll_area import ScrollArea
from ..widgets.acrylic_label import AcrylicBrush
from ..material.acrylic_flyout import AcrylicFlyout, AcrylicFlyoutViewBase


class NavigationDisplayMode(Enum):
    """导航显示模式"""

    MINIMAL = 0  # 最小模式
    COMPACT = 1  # 紧凑模式
    EXPAND = 2  # 展开模式
    MENU = 3  # 菜单模式


class NavigationItemPosition(Enum):
    """导航项位置"""

    TOP = 0  # 顶部
    SCROLL = 1  # 滚动区
    BOTTOM = 2  # 底部


class NavigationToolTipFilter(ToolTipFilter):
    """导航工具提示过滤器"""

    def _canShowToolTip(self) -> bool:
        isVisible = super()._canShowToolTip()
        parent: NavigationWidget = self.parent()
        return isVisible and parent.isCompacted


class RouteKeyError(Exception):
    """路由键错误"""


class NavigationItem:
    """导航项"""

    def __init__(self, routeKey: str, parentRouteKey: str, widget: NavigationWidget):
        """
        初始化导航项

        Parameters
        ----------
        routeKey : str
            导航项的唯一标识符

        parentRouteKey : str
            父级导航项的标识符

        widget : NavigationWidget
            该导航项对应的控件
        """
        self.routeKey = routeKey
        self.parentRouteKey = parentRouteKey
        self.widget = widget


class NavigationPanel(QFrame):
    """导航面板"""

    # 显示模式改变信号
    displayModeChanged = Signal(NavigationDisplayMode)

    def __init__(self, parent: QWidget = None, isMinimalEnabled: bool = False) -> None:
        super().__init__(parent=parent)
        # 父级窗口组件,方便调用
        self._parent = parent

        # 定义内置属性
        self._isMenuButtonVisible = True
        self._isReturnButtonVisible = False
        self._isCollapsible = True
        self._isAcrylicEnabled = False

        # 亚克力材料
        self.acrylicBrush = AcrylicBrush(self, 30)

        # 滚动区域
        self.scrollArea = ScrollArea(self)
        self.scrollWidget = QWidget()

        # 创建按钮
        self.menuButton = NavigationToolButton(FIF.MENU, self)
        self.returnButton = NavigationToolButton(FIF.RETURN, self)

        # 创建布局
        self.vBoxLayout = NavigationItemLayout(self)
        self.topLayout = NavigationItemLayout()
        self.bottomLayout = NavigationItemLayout()
        self.scrollLayout = NavigationItemLayout(self.scrollWidget)

        # 导航项以及历史记录
        self.items: Dict[str, NavigationItem] = {}
        self.history = qrouter

        # 展开动画
        self.expandAni = QPropertyAnimation(self, b"geometry", self)
        self.expandWidth = 322
        self.minimumExpandWidth = 1008

        self.isMinimalEnabled = isMinimalEnabled
        if isMinimalEnabled:
            self.displayMode = NavigationDisplayMode.MINIMAL
        else:
            self.displayMode = NavigationDisplayMode.COMPACT

        # 初始化控件
        self.__initWidget()

    def __initWidget(self) -> None:
        """初始化控件"""
        self.resize(48, self.height())
        self.setAttribute(Qt.WA_StyledBackground)
        self.window().installEventFilter(self)

        self.returnButton.hide()
        self.returnButton.setDisabled(True)

        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.horizontalScrollBar().setEnabled(False)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)

        self.expandAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.expandAni.setDuration(150)

        self.menuButton.clicked.connect(self.toggle)
        self.expandAni.finished.connect(self._onExpandAniFinished)
        self.history.emptyChanged.connect(self.returnButton.setDisabled)
        self.returnButton.clicked.connect(self.history.pop)

        # add tool tip
        self.returnButton.installEventFilter(ToolTipFilter(self.returnButton, 1000))
        self.returnButton.setToolTip(self.tr("Back"))

        self.menuButton.installEventFilter(ToolTipFilter(self.menuButton, 1000))
        self.menuButton.setToolTip(self.tr("Open Navigation"))

        self.scrollWidget.setObjectName("scrollWidget")
        self.setProperty("menu", False)
        FluentStyleSheet.NAVIGATION_INTERFACE.apply(self)
        FluentStyleSheet.NAVIGATION_INTERFACE.apply(self.scrollWidget)
        self.__initLayout()

    def __initLayout(self):
        self.vBoxLayout.setContentsMargins(0, 5, 0, 5)
        self.topLayout.setContentsMargins(4, 0, 4, 0)
        self.bottomLayout.setContentsMargins(4, 0, 4, 0)
        self.scrollLayout.setContentsMargins(4, 0, 4, 0)
        self.vBoxLayout.setSpacing(4)
        self.topLayout.setSpacing(4)
        self.bottomLayout.setSpacing(4)
        self.scrollLayout.setSpacing(4)

        self.vBoxLayout.addLayout(self.topLayout, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addLayout(self.bottomLayout, 0)

        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.topLayout.setAlignment(Qt.AlignTop)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.bottomLayout.setAlignment(Qt.AlignBottom)

        self.topLayout.addWidget(self.returnButton, 0, Qt.AlignTop)
        self.topLayout.addWidget(self.menuButton, 0, Qt.AlignTop)

    def _updateAcrylicColor(self):
        if isDarkTheme():
            tintColor = QColor(32, 32, 32, 200)
            luminosityColor = QColor(0, 0, 0, 0)
        else:
            tintColor = QColor(255, 255, 255, 180)
            luminosityColor = QColor(255, 255, 255, 0)

        self.acrylicBrush.tintColor = tintColor
        self.acrylicBrush.luminosityColor = luminosityColor

    def widget(self, routeKey: str):
        if routeKey not in self.items:
            raise RouteKeyError(f"`{routeKey}` is illegal.")

        return self.items[routeKey].widget

    def addItem(
        self,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        text: str,
        onClick=None,
        selectable=True,
        position=NavigationItemPosition.TOP,
        tooltip: str = None,
        parentRouteKey: str = None,
    ):
        """add navigation item

        Parameters
        ----------
        routeKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        selectable: bool
            whether the item is selectable

        tooltip: str
            the tooltip of item

        parentRouteKey: str
            the route key of parent item, the parent widget should be `NavigationTreeWidget`
        """
        return self.insertItem(-1, routeKey, icon, text, onClick, selectable, position, tooltip, parentRouteKey)

    def addWidget(
        self,
        routeKey: str,
        widget: NavigationWidget,
        onClick=None,
        position=NavigationItemPosition.TOP,
        tooltip: str = None,
        parentRouteKey: str = None,
    ):
        """add custom widget

        Parameters
        ----------
        routeKey: str
            the unique name of item

        widget: NavigationWidget
            the custom widget to be added

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        tooltip: str
            the tooltip of widget

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidget`
        """
        self.insertWidget(-1, routeKey, widget, onClick, position, tooltip, parentRouteKey)

    def insertItem(
        self,
        index: int,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        text: str,
        onClick=None,
        selectable=True,
        position=NavigationItemPosition.TOP,
        tooltip: str = None,
        parentRouteKey=None,
    ):
        """insert navigation tree item

        Parameters
        ----------
        index: int
            the insert position of parent widget

        routeKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        selectable: bool
            whether the item is selectable

        tooltip: str
            the tooltip of item

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidget`
        """
        if routeKey in self.items:
            return

        w = NavigationTreeWidget(icon, text, selectable, self)
        self.insertWidget(index, routeKey, w, onClick, position, tooltip, parentRouteKey)
        return w

    def insertWidget(
        self,
        index: int,
        routeKey: str,
        widget: NavigationWidget,
        onClick=None,
        position=NavigationItemPosition.TOP,
        tooltip: str = None,
        parentRouteKey: str = None,
    ):
        """insert custom widget

        Parameters
        ----------
        index: int
            insert position

        routeKey: str
            the unique name of item

        widget: NavigationWidget
            the custom widget to be added

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        tooltip: str
            the tooltip of widget

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidget`
        """
        if routeKey in self.items:
            return

        self._registerWidget(routeKey, parentRouteKey, widget, onClick, tooltip)
        if parentRouteKey:
            self.widget(parentRouteKey).insertChild(index, widget)
        else:
            self._insertWidgetToLayout(index, widget, position)

    def addSeparator(self, position=NavigationItemPosition.TOP):
        """add separator

        Parameters
        ----------
        position: NavigationPostion
            where to add the separator
        """
        self.insertSeparator(-1, position)

    def insertSeparator(self, index: int, position=NavigationItemPosition.TOP):
        """add separator

        Parameters
        ----------
        index: int
            insert position

        position: NavigationPostion
            where to add the separator
        """
        separator = NavigationSeparator(self)
        self._insertWidgetToLayout(index, separator, position)

    def _registerWidget(self, routeKey: str, parentRouteKey: str, widget: NavigationWidget, onClick, tooltip: str):
        """register widget"""
        widget.clicked.connect(self._onWidgetClicked)

        if onClick is not None:
            widget.clicked.connect(onClick)

        widget.setProperty("routeKey", routeKey)
        widget.setProperty("parentRouteKey", parentRouteKey)
        self.items[routeKey] = NavigationItem(routeKey, parentRouteKey, widget)

        if self.displayMode in [NavigationDisplayMode.EXPAND, NavigationDisplayMode.MENU]:
            widget.setCompacted(False)

        if tooltip:
            widget.setToolTip(tooltip)
            widget.installEventFilter(NavigationToolTipFilter(widget, 1000))

    def _insertWidgetToLayout(self, index: int, widget: NavigationWidget, position: NavigationItemPosition):
        """insert widget to layout"""
        if position == NavigationItemPosition.TOP:
            widget.setParent(self)
            self.topLayout.insertWidget(index, widget, 0, Qt.AlignTop)
        elif position == NavigationItemPosition.SCROLL:
            widget.setParent(self.scrollWidget)
            self.scrollLayout.insertWidget(index, widget, 0, Qt.AlignTop)
        else:
            widget.setParent(self)
            self.bottomLayout.insertWidget(index, widget, 0, Qt.AlignBottom)

        widget.show()

    def removeWidget(self, routeKey: str):
        """remove widget

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        item = self.items.pop(routeKey)

        if item.parentRouteKey is not None:
            self.widget(item.parentRouteKey).removeChild(item.widget)

        if isinstance(item.widget, NavigationTreeWidgetBase):
            for child in item.widget.findChildren(NavigationWidget, options=Qt.FindChildrenRecursively):
                key = child.property("routeKey")
                if key is None:
                    continue

                self.items.pop(key)
                child.deleteLater()
                self.history.remove(key)

        item.widget.deleteLater()
        self.history.remove(routeKey)

    def setMenuButtonVisible(self, isVisible: bool):
        """set whether the menu button is visible"""
        self._isMenuButtonVisible = isVisible
        self.menuButton.setVisible(isVisible)

    def setReturnButtonVisible(self, isVisible: bool):
        """set whether the return button is visible"""
        self._isReturnButtonVisible = isVisible
        self.returnButton.setVisible(isVisible)

    def setCollapsible(self, on: bool):
        self._isCollapsible = on
        if not on and self.displayMode != NavigationDisplayMode.EXPAND:
            self.expand(False)

    def setExpandWidth(self, width: int):
        """set the maximum width"""
        if width <= 42:
            return

        self.expandWidth = width
        NavigationWidget.EXPAND_WIDTH = width - 10

    def setMinimumExpandWidth(self, width: int):
        """Set the minimum window width that allows panel to be expanded"""
        self.minimumExpandWidth = width

    def setAcrylicEnabled(self, isEnabled: bool):
        if isEnabled == self.isAcrylicEnabled():
            return

        self._isAcrylicEnabled = isEnabled
        self.setProperty("transparent", self._canDrawAcrylic())
        self.setStyle(QApplication.style())
        self.update()

    def isAcrylicEnabled(self):
        """whether the acrylic effect is enabled"""
        return self._isAcrylicEnabled

    def expand(self, useAni=True):
        """expand navigation panel"""
        self._setWidgetCompacted(False)
        self.expandAni.setProperty("expand", True)
        self.menuButton.setToolTip(self.tr("Close Navigation"))

        # determine the display mode according to the width of window
        # https://learn.microsoft.com/en-us/windows/apps/design/controls/navigationview#default
        expandWidth = self.minimumExpandWidth + self.expandWidth - 322
        if (self.window().width() >= expandWidth and not self.isMinimalEnabled) or not self._isCollapsible:
            self.displayMode = NavigationDisplayMode.EXPAND
        else:
            self.setProperty("menu", True)
            self.setStyle(QApplication.style())
            self.displayMode = NavigationDisplayMode.MENU

            # grab acrylic image
            if self._canDrawAcrylic():
                self.acrylicBrush.grabImage(QRect(self.mapToGlobal(QPoint()), QSize(self.expandWidth, self.height())))

            if not self._parent.isWindow():
                pos = self.parent().pos()
                self.setParent(self.window())
                self.move(pos)

            self.show()

        if useAni:
            self.displayModeChanged.emit(self.displayMode)
            self.expandAni.setStartValue(QRect(self.pos(), QSize(48, self.height())))
            self.expandAni.setEndValue(QRect(self.pos(), QSize(self.expandWidth, self.height())))
            self.expandAni.start()
        else:
            self.resize(self.expandWidth, self.height())
            self._onExpandAniFinished()

    def collapse(self):
        """collapse navigation panel"""
        if self.expandAni.state() == QPropertyAnimation.Running:
            return

        for item in self.items.values():
            w = item.widget
            if isinstance(w, NavigationTreeWidgetBase) and w.isRoot():
                w.setExpanded(False)

        self.expandAni.setStartValue(QRect(self.pos(), QSize(self.width(), self.height())))
        self.expandAni.setEndValue(QRect(self.pos(), QSize(48, self.height())))
        self.expandAni.setProperty("expand", False)
        self.expandAni.start()

        self.menuButton.setToolTip(self.tr("Open Navigation"))

    def toggle(self):
        """toggle navigation panel"""
        if self.displayMode in [NavigationDisplayMode.COMPACT, NavigationDisplayMode.MINIMAL]:
            self.expand()
        else:
            self.collapse()

    def setCurrentItem(self, routeKey: str):
        """set current selected item

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        for k, item in self.items.items():
            item.widget.setSelected(k == routeKey)

    def _onWidgetClicked(self):
        widget = self.sender()  # type: NavigationWidget
        if not widget.isSelectable:
            return self._showFlyoutNavigationMenu(widget)

        self.setCurrentItem(widget.property("routeKey"))

        isLeaf = not isinstance(widget, NavigationTreeWidgetBase) or widget.isLeaf()
        if self.displayMode == NavigationDisplayMode.MENU and isLeaf:
            self.collapse()
        elif self.isCollapsed():
            self._showFlyoutNavigationMenu(widget)

    def _showFlyoutNavigationMenu(self, widget: NavigationTreeWidget):
        """show flyout navigation menu"""
        if not (self.isCollapsed() and isinstance(widget, NavigationTreeWidget)):
            return

        if not widget.isRoot() or widget.isLeaf():
            return

        layout = QHBoxLayout()

        if self._canDrawAcrylic():
            view = AcrylicFlyoutViewBase()
            view.setLayout(layout)
            flyout = AcrylicFlyout(view, self.window())
        else:
            view = FlyoutViewBase()
            view.setLayout(layout)
            flyout = Flyout(view, self.window())

        # add navigation menu to flyout
        menu = NavigationFlyoutMenu(widget, view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(menu)

        # execuse flyout animation
        flyout.resize(flyout.sizeHint())
        pos = SlideRightFlyoutAnimationManager(flyout).position(widget)
        flyout.exec(pos, FlyoutAnimationType.SLIDE_RIGHT)

        menu.expanded.connect(lambda: self._adjustFlyoutMenuSize(flyout, widget, menu))

    def _adjustFlyoutMenuSize(self, flyout: Flyout, widget: NavigationTreeWidget, menu: NavigationFlyoutMenu):
        flyout.view.setFixedSize(menu.size())
        flyout.setFixedSize(flyout.layout().sizeHint())

        manager = flyout.aniManager
        pos = manager.position(widget)

        rect = self.window().geometry()
        w, h = flyout.sizeHint().width() + 5, flyout.sizeHint().height()
        x = max(rect.left(), min(pos.x(), rect.right() - w))
        y = max(rect.top() + 42, min(pos.y() - 4, rect.bottom() - h + 5))
        flyout.move(x, y)

    def isCollapsed(self):
        return self.displayMode == NavigationDisplayMode.COMPACT

    def eventFilter(self, obj, e: QEvent):
        if obj is not self.window() or not self._isCollapsible:
            return super().eventFilter(obj, e)

        if e.type() == QEvent.MouseButtonRelease:
            if not self.geometry().contains(e.pos()) and self.displayMode == NavigationDisplayMode.MENU:
                self.collapse()
        elif e.type() == QEvent.Resize:
            w = QResizeEvent(e).size().width()
            if w < self.minimumExpandWidth and self.displayMode == NavigationDisplayMode.EXPAND:
                self.collapse()
            elif (
                w >= self.minimumExpandWidth
                and self.displayMode == NavigationDisplayMode.COMPACT
                and not self._isMenuButtonVisible
            ):
                self.expand()

        return super().eventFilter(obj, e)

    def _onExpandAniFinished(self):
        if not self.expandAni.property("expand"):
            if self.isMinimalEnabled:
                self.displayMode = NavigationDisplayMode.MINIMAL
            else:
                self.displayMode = NavigationDisplayMode.COMPACT

            self.displayModeChanged.emit(self.displayMode)

        if self.displayMode == NavigationDisplayMode.MINIMAL:
            self.hide()
            self.setProperty("menu", False)
            self.setStyle(QApplication.style())
        elif self.displayMode == NavigationDisplayMode.COMPACT:
            self.setProperty("menu", False)
            self.setStyle(QApplication.style())

            for item in self.items.values():
                item.widget.setCompacted(True)

            if not self._parent.isWindow():
                self.setParent(self._parent)
                self.move(0, 0)
                self.show()

    def _setWidgetCompacted(self, isCompacted: bool):
        """set whether the navigation widget is compacted"""
        for item in self.findChildren(NavigationWidget):
            item.setCompacted(isCompacted)

    def layoutMinHeight(self):
        th = self.topLayout.minimumSize().height()
        bh = self.bottomLayout.minimumSize().height()
        sh = sum(w.height() for w in self.findChildren(NavigationSeparator))
        spacing = self.topLayout.count() * self.topLayout.spacing()
        spacing += self.bottomLayout.count() * self.bottomLayout.spacing()
        return 36 + th + bh + sh + spacing

    def _canDrawAcrylic(self):
        return self.acrylicBrush.isAvailable() and self.isAcrylicEnabled()

    def paintEvent(self, e):
        if not self._canDrawAcrylic() or self.displayMode != NavigationDisplayMode.MENU:
            return super().paintEvent(e)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(0, 1, self.width() - 1, self.height() - 1, 7, 7)
        path.addRect(0, 1, 8, self.height() - 1)
        self.acrylicBrush.setClipPath(path)

        self._updateAcrylicColor()
        self.acrylicBrush.paint()

        super().paintEvent(e)


class NavigationItemLayout(QVBoxLayout):
    """Navigation layout"""

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        for i in range(self.count()):
            item = self.itemAt(i)
            if isinstance(item.widget(), NavigationSeparator):
                geo = item.geometry()
                item.widget().setGeometry(0, geo.y(), geo.width(), geo.height())
