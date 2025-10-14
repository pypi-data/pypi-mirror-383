from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets

from .figure_widget import FigureWidget


class TabbedFigureWidget(QtWidgets.QTabWidget):
    """
    A Qt widget that can contains multiple tabs, each with a matplotlib Figure.
    This class inherits from QTabWidget in order to create a tabbed interface.

    Methods:
        `add_figure_tab`: Adds a new tab with a matplotlib Figure.
        `set_tab_position`: Sets the position of the tab bar.
        `set_tab_fontsize`: Sets the font size of the tab bar.
    """

    def __init__(self, autohide: bool, position: str = "top", fontsize: int = 8):
        """
        Initializes the TabbedFigureWidget.

        Args:
            autohide (bool): If True, the tab bar will auto-hide when there is
                only one tab.
            position (str): The position of the tab bar. Can be 'top', 'bottom',
                'left', or 'right' as well as 'north', 'south', 'east', or
                'west' (only first character is checked).
            fontsize (int): The font size of the tab labels.
        """
        super().__init__()
        tabbar = self.tabBar()
        assert isinstance(tabbar, QtWidgets.QTabBar)
        tabbar.setAutoHide(autohide)
        tabbar.setContentsMargins(0, 0, 0, 0)
        self.set_tab_position(position)
        self.set_tab_fontsize(fontsize)
        self._figure_widgets: dict[str, FigureWidget] = {}

    def add_figure_tab(
        self, tab_id: str | int, blit: bool = False, include_toolbar: bool = True
    ) -> Figure:
        """
        Adds a new tab to the widget with the given title/tab_id, which
        creates and returns a matplotlib Figure. Tabs are displayed in the
        order they are added.

        Args:
            tab_id (str|int): The title/ID of the tab. If the tab ID already
                exists, the existing Figure from that tab will be returned.
            blit (bool): If True, enables blitting for faster rendering on the
                Figure in this tab.
            include_toolbar (bool): If True, includes a navigation toolbar
                with the Figure in this tab.
        """
        new_tab = FigureWidget(blit, include_toolbar)
        id_ = str(tab_id)
        if id_ in self._figure_widgets:
            return self._figure_widgets[id_].figure
        self._figure_widgets[id_] = new_tab
        idx = self.currentIndex()
        super().addTab(new_tab, id_)
        self.setCurrentWidget(new_tab)  # activate tab to auto size figure
        self.setCurrentIndex(idx)  # switch back to original tab
        return new_tab.figure

    def set_tab_position(self, position: str = "top") -> None:
        """
        Sets the position of the tab bar.

        Args:
            position (str): The position of the tab bar. Can be 'top', 'bottom',
                'left', or 'right' as well as 'north', 'south', 'east', or
                'west' (only first character is checked).
        """
        char = position[0].lower()
        if char in ["b", "s"]:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        elif char in ["l", "w"]:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        elif char in ["r", "e"]:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.East)
        else:
            self.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)

    def set_tab_fontsize(self, fontsize: int) -> None:
        """
        Sets the font size of the tab bar.

        Args:
            fontsize (int): The font size to set for the tab bar.
        """
        tabbar = self.tabBar()
        assert isinstance(tabbar, QtWidgets.QTabBar)
        font = tabbar.font()
        font.setPointSize(fontsize)
        tabbar.setFont(font)
