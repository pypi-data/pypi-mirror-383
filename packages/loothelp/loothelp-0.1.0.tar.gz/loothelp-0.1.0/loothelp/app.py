from PyQt6 import QtWidgets


class App(QtWidgets.QApplication):
    def exec(self):
        exit_code = super().exec()
        if not self.normal_exit:
            return exit_code
        return 0

    def quit(self):
        super().quit()
        self.normal_exit = True
