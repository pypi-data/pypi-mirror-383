from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar


class FigureWidget(QtWidgets.QWidget):
    """
    A Qt widget that contains a matplotlib figure canvas with an optional toolbar.
    Inherits from `QWidget`.

    Methods:
        `update_figure`: Updates the figure canvas if anything has changed.
        `show_toolbar`: Show or hide the navigation toolbar.
    """

    def __init__(self, blit: bool = False, include_toolbar: bool = True, parent=None):
        """
        Initializes the FigureWidget. This creates a matplotlib figure canvas
        and optionally includes a navigation toolbar.

        Args:
            blit (bool): If True, enables blitting for faster rendering.
            include_toolbar (bool): If True, includes a navigation toolbar
                with the canvas.
            parent: The parent widget for this widget.
        """
        super().__init__(parent)
        self.blit = blit
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = FigureCanvas()
        self.figure = self.canvas.figure
        # self.figure.set_layout_engine('tight') # slows down rendering ~2x
        # self.figure.tight_layout() # does not seem to do anything here
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setMaximumHeight(25)
        layout.addWidget(self.toolbar)
        self.toolbar.setVisible(include_toolbar)

        self.setLayout(layout)

    def update_figure(self) -> None:
        """
        Updates the figure canvas if anything has changed. If blitting is
        enabled, it will only redraw the parts of the figure that have changed.
        If not, it will redraw the entire canvas. NOTE that blitting requires
        the user to manage the background and artist updates manually, i.e., the
        user must call `canvas.copy_from_bbox()` and `canvas.restore_region()`
        at the appropriate times AND ensure that the artists are drawn before
        calling this method.
        """
        if not self.figure.stale:
            return
        if self.blit:
            self.canvas.blit()
            # self.canvas.blit(self.figure.bbox)
        else:
            self.canvas.draw_idle()
        self.canvas.flush_events()

    def show_toolbar(self, show: bool = True) -> None:
        """
        Show or hide the navigation toolbar.

        Args:
            show (bool): If True, shows the toolbar. If False, hides it.
        """
        self.toolbar.setVisible(show)
