#!/usr/bin/python

import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_UI()

    def init_UI(self):
        WINDOW_WIDTH = 800
        WINDOW_HEIGHT = 800
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.center()
        self.setWindowTitle('Test GUI')
        self.show()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)

# if __name__ == '__main__':
app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
