from PyQt5.QtCore import QObject, pyqtSignal


class DataEvents(QObject):
    """Global app-wide signals for data changes."""

    slips_changed = pyqtSignal()


data_events = DataEvents()
