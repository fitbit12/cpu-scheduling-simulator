import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from PyQt6.QtWidgets import QHeaderView


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())