import sys
import signal
from PyQt6 import QtCore
from loothelp.overlay import LootOverlay
from loothelp.app import App


def main():
    app = App(sys.argv)
    overlay = LootOverlay()

    def handle_signal(signum, frame):
        QtCore.QTimer.singleShot(0, overlay.cleanup)
        QtCore.QTimer.singleShot(10, app.quit)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    overlay.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
