from qtpy.QtWidgets import QFrame
from .base import PyDMWidget, PostParentClassInitSetup
from pydm.utilities import ACTIVE_QT_WRAPPER, QtWrapperTypes

if ACTIVE_QT_WRAPPER == QtWrapperTypes.PYSIDE6:
    from PySide6.QtCore import Property
else:
    from PyQt5.QtCore import pyqtProperty as Property


class PyDMFrame(QFrame, PyDMWidget):
    """
    QFrame with support for alarms
    This class inherits from QFrame and PyDMWidget.

    Parameters
    ----------
    parent : QWidget
        The parent widget for the Label
    init_channel : str, optional
        The channel to be used by the widget.
    """

    def __init__(self, parent=None, init_channel=None):
        QFrame.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)

        self._disable_on_disconnect = False
        self.alarmSensitiveBorder = False

        # Execute setup calls that must be done here in the widget class's __init__,
        # and after it's parent __init__ calls have completed.
        # (so we can avoid pyside6 throwing an error, see func def for more info)
        PostParentClassInitSetup(self)

    # On pyside6, we need to expilcity call pydm's base class's eventFilter() call or events
    # will not propagate to the parent classes properly.
    def eventFilter(self, obj, event):
        return PyDMWidget.eventFilter(self, obj, event)

    def readDisableOnDisconnect(self) -> bool:
        """
        Whether or not the PyDMFrame should be disabled in case the
        channel is disconnected.

        Returns
        -------
        disable : bool
            The configured value
        """
        return self._disable_on_disconnect

    def setDisableOnDisconnect(self, new_val) -> None:
        """
        Whether or not the PyDMFrame should be disabled in case the
        channel is disconnected.

        Parameters
        ----------
        new_val : bool
            The new configuration to use
        """
        if self._disable_on_disconnect != bool(new_val):
            self._disable_on_disconnect = new_val
            self.check_enable_state()

    disableOnDisconnect = Property(bool, readDisableOnDisconnect, setDisableOnDisconnect)

    def check_enable_state(self):
        """
        Checks whether or not the widget should be disable.
        This method also disables the widget and add a Tool Tip
        with the reason why it is disabled.
        """
        if hasattr(self, "_disable_on_disconnect") and self._disable_on_disconnect:
            PyDMWidget.check_enable_state(self)
        else:
            self.setEnabled(True)
