"""
abracatabra
===========
A package for creating tabbed plot windows with matplotlib in a Qt environment.

Windows can be created with one or more tab groups. Each tab group can contain
one or more tabs, where is tab is a matplotlib Figure. The library provides
functions to show all open windows, update them, and a fun `abracatabra`
function to display all windows with a magical touch.

This package provides:
- `TabbedPlotWindow`: The main class for creating and managing tabbed plot windows.
- `show_all_windows`: Displays all open tabbed plot windows.
- `update_all_windows`: Updates all open tabbed plot windows.
- `abracatabra`: A fun function to display all open tabbed plot windows.
- `is_interactive`: Checks if the current environment is interactive (e.g., IPython or Jupyter).
- `__version__`: The version of the abracatabra package.
"""

from .tabbed_plot_window import TabbedPlotWindow, is_interactive
from .__about__ import __version__


def show_all_windows(tight_layout: bool = False, block: bool | None = None) -> None:
    """
    Shows all created windows.

    Args:
        tight_layout (bool): If True, applies a tight layout to all figures.
        block (bool): If True, block and run the GUI until all windows are
            closed, either individually or by pressing <ctrl+c> in the terminal.
            If False, the function returns immediately after showing the windows
            and you are responsible for ensuring the GUI event loop is running
            (interactive environments do this for you).
            Defaults to False in interactive environments, otherwise True.
    See Also
    -----
    `abracatabra()` : shows all created windows with a touch of magic!
    `update_all_windows()` : updates all open tabbed plot windows.
    `is_interactive()` : checks if the current environment is interactive.
    """
    TabbedPlotWindow.show_all(tight_layout, block)


def update_all_windows(delay_seconds: float = 0.0) -> float:
    """
    Updates all open tabbed plot windows. This is similar to pyplot.pause()
    and is generally used to update the figure in a loop, e.g., an animation.
    This function only updates active tabs in each window, so inactive tabs are
    skipped to save time.

    Args:
        delay_seconds (float): The minimum delay in seconds before returning. If
            windows are updated faster than this, this function will block until
            `delay_seconds` seconds have passed. If the windows take longer than
            `delay_seconds` seconds to update, the function execution time will
            be greater than `delay_seconds`.
    Returns:
        update_time (float): The amount of time (seconds) taken to update the
            windows.
    See Also
    -----
    `show_all_windows()` : shows all created windows.
    `abracatabra()` : shows all created windows with a touch of magic!
    """
    return TabbedPlotWindow.update_all(delay_seconds)


def abracatabra(
    tight_layout: bool = False, block: bool | None = None, verbose: bool = True
) -> None:
    """
    A more fun equivalent to `show_all_windows()`. Shows all created windows.

    Args:
        tight_layout (bool): If True, applies a tight layout to all figures.
        block (bool): If True, block and run the GUI until all windows are
            closed, either individually or by pressing <ctrl+c> in the terminal.
            If False, the function returns immediately after showing the windows
            and you are responsible for ensuring the GUI event loop is running
            (interactive environments do this for you).
            Defaults to False in interactive environments, otherwise True.
        verbose (bool): If True, prints a message when showing windows.
    See Also
    -----
    `show_all_windows()` : shows all created windows.
    `update_all_windows()` : updates all open tabbed plot windows.
    `is_interactive()` : checks if the current environment is interactive.
    """
    if verbose:
        print("Abracatabra! 🪄✨")
    for window in TabbedPlotWindow._registry.values():
        window.qt.setWindowIcon(window._icon2)
    TabbedPlotWindow.show_all(tight_layout, block)


__all__ = [
    "TabbedPlotWindow",
    "show_all_windows",
    "update_all_windows",
    "abracatabra",
    "is_interactive",
    "__version__",
]
