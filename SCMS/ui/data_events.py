from PyQt5.QtCore import QObject, pyqtSignal


class DataEvents(QObject):
    """Global app-wide signals for data changes."""

    slips_changed = pyqtSignal()
    settings_changed = pyqtSignal()  # Emitted when any system settings are saved


data_events = DataEvents()
