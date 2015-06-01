#!/usr/bin/python

import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication, QFileDialog, QAction

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.init_menubar()

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

    def init_menubar(self):
        open_file = QAction('Load', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Load a .yo file')
        open_file.triggered.connect(self.show_file_dialog)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_file)

    def show_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Load file', '~')

        print fname

# if __name__ == '__main__':
app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
