import json
import signal
from PyQt6 import QtWidgets, QtCore, QtGui
from .counter import LootCounter
from pathlib import Path


class LootOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._minimized = False
        self._normal_size = self.size()
        self._minimized_size = QtCore.QSize(300, 40)
        x, y = load_position()
        self.setWindowTitle("Loot Overlay")
        self.setGeometry(x, y, 300, 140)
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
            | QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.counter = LootCounter()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(500)

        self.title_edit = QtWidgets.QLineEdit(self)
        self.title_edit.setText(self.counter.title)
        self.title_edit.setFont(QtGui.QFont("Consolas", 12, QtGui.QFont.Weight.Bold))
        self.title_edit.setStyleSheet(
            "background: rgba(0,0,0,0); color: white; border: none;"
        )
        self.title_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.title_edit.setGeometry(18, 10, 120, 25)
        self.title_edit.editingFinished.connect(self.set_title)
        self.title_edit.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

        # ---- Buttons ----
        self.drop_btn = QtWidgets.QPushButton("Dropped", self)
        self.no_drop_btn = QtWidgets.QPushButton("No Drop :(", self)

        self.exit_btn = QtWidgets.QPushButton("X", self)
        self.reset_btn = QtWidgets.QPushButton("⟳", self)

        self.toggle_btn = QtWidgets.QPushButton("-", self)

        self._setup_buttons()

    # ---- Setup buttons styling ----
    def _setup_buttons(self):
        btn_style = """
        QPushButton {
            background-color: rgba(50,50,50,180);
            color: white;
            border-radius: 5px;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: rgba(100,100,100,200);
        }
        """
        self.drop_btn.setStyleSheet(btn_style)
        self.no_drop_btn.setStyleSheet(btn_style)

        self.drop_btn.setGeometry(10, 100, 130, 30)
        self.no_drop_btn.setGeometry(160, 100, 130, 30)

        self.drop_btn.clicked.connect(lambda: self.handle_run(drop=True))
        self.no_drop_btn.clicked.connect(lambda: self.handle_run(drop=False))

        self.exit_btn.setStyleSheet("""
        QPushButton {
            background-color: rgba(200,50,50,220);
            color: white;
            border-radius: 5px;
            font-weight: bold;
            font: 14px;
        }
        QPushButton:hover {
            background-color: rgba(255,80,80,255);
        }
        """)
        self.exit_btn.setGeometry(260, 10, 30, 25)
        self.exit_btn.clicked.connect(self.signal_close)

        # Reset button (requires double-click)

        self.reset_btn.setStyleSheet("""
        QPushButton {
            background-color: rgba(250,100,0,220);
            color: white;
            border-radius: 5px;
            font-weight: bold;
            font: 20px;
            padding: 0px 4px 6px 4px;
        }
        QPushButton:hover {
            background-color: rgba(255,80,80,255);
        }
        """)
        self.reset_btn.setGeometry(220, 10, 30, 25)
        self.reset_btn.setMouseTracking(True)
        self.reset_btn.mouseDoubleClickEvent = self.reset_counter

        self.toggle_btn.setGeometry(180, 10, 30, 25)
        self.toggle_btn.setFont(QtGui.QFont("Arial", 20))
        self.toggle_btn.clicked.connect(self.toggle_overlay)

    def reset_counter(self, event):
        self.counter.reset()
        self.update()

    def signal_close(self):
        signal.raise_signal(signal.SIGINT)

    def handle_run(self, drop: bool):
        self.counter.finish_run(drop=drop)
        self.update()

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        painter.setRenderHint(QtWidgets.QStylePainter.RenderHint.Antialiasing)

        bg = QtGui.QColor(0, 0, 0, 128)
        painter.setBrush(bg)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

        painter.setPen(QtCore.Qt.GlobalColor.white)
        painter.drawText(20, 50, f"Runs: {self.counter.total_runs}")
        painter.drawText(
            20,
            70,
            f"Drops: {self.counter.total_drops} ({self.counter.drop_rate():.1f}%)",
        )
        painter.drawText(20, 90, f"Avg time: {self.counter.avg_run_time:.1f}s")

    def cleanup(self):
        save_position(self.x(), self.y())
        self.timer.stop()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            self._dragging = True

    def mouseReleaseEvent(self, event):
        self._dragging = False

    def mouseMoveEvent(self, event):
        if getattr(self, "_dragging", False):
            new_pos = event.globalPosition().toPoint() - self._drag_pos

            # Get screen geometry
            screen = QtWidgets.QApplication.primaryScreen().availableGeometry()

            # Clamp so entire window stays inside the screen
            x = max(screen.left(), min(new_pos.x(), screen.right() - self.width()))
            y = max(screen.top(), min(new_pos.y(), screen.bottom() - self.height()))

            self.move(x, y)

    def set_title(self):
        """Change the overlay title dynamically."""
        self.counter.title = self.title_edit.text()
        self.update()

    def toggle_overlay(self):
        if self._minimized:
            # maximize
            self.resize(self._normal_size)
            self.toggle_btn.setText("-")  # show minimize icon
            self._minimized = False
        else:
            # minimize
            self._normal_size = self.size()  # store current size
            self.resize(self._minimized_size)
            self.toggle_btn.setText("+")  # show maximize icon
            self._minimized = True


CONFIG_FILE = Path.home() / ".loothelp.config"


def save_position(x, y):
    data = {"x": x, "y": y}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


def load_position():
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open() as f:
            data = json.load(f)
            return data.get("x", 100), data.get("y", 100)
    return 100, 100
