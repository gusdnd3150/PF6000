import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from wpms.initUi import InitWindow
import conf.logconfig as logger

# app = QApplication(sys.argv)
# myWindow = InitWindow()
# app.exec_()


def main():
    app = QApplication(sys.argv)
    main_window = InitWindow()
    main_window.show()
    app.exec_()

if __name__ == '__main__':
    main()