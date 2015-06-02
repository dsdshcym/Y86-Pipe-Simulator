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

        run_file = QAction('Run', self)
        run_file.setShortcut('Ctrl+R')
        run_file.setStatusTip('Run a .yo file')
        run_file.triggered.connect(self.run)

        step = QAction('Step', self)
        step.setShortcut('Ctrl+S')
        step.setStatusTip('Run for one step')
        step.triggered.connect(self.step)

        back = QAction('Back', self)
        back.setShortcut('Ctrl+B')
        back.setStatusTip('Go back one step')
        back.triggered.connect(self.back)

        reset = QAction('Reset', self)
        reset.setShortcut('Alt+R')
        reset.setStatusTip('Reset a running processor')
        reset.triggered.connect(self.reset)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_file)
        processor_menu = menubar.addMenu('&Processor')
        processor_menu.addAction(run_file)
        processor_menu.addAction(step)
        processor_menu.addAction(back)
        processor_menu.addAction(reset)

    def show_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Load file', '~')

    def run(self):
        print('run')
        pass

    def step(self):
        print('step')
        pass

    def back(self):
        print('back')
        pass

    def reset(self):
        print('reset')
        pass

# if __name__ == '__main__':
app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
