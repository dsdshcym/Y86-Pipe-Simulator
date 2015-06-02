#!/usr/bin/python

import io
import sys
import re
from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QApplication,
                             QFileDialog, QAction, QTextEdit, QMessageBox,
                             QGridLayout, QLabel, QLineEdit, QWidget)
from processor import Y86Processor

class MainWidget(QWidget):

    def __init__(self):
        super(MainWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(15)

        self.init_processor_info()

        self.init_textarea()

        self.setLayout(self.grid)

    def init_textarea(self):
        self.src_text = QTextEdit()
        self.grid.addWidget(self.src_text, 3, 0, 10, 0)

    def init_processor_info(self):
        fetch = QLabel('Fetch:')
        F_predPC = QLabel('F_predPC')

        self.grid.addWidget(fetch, 2, 0)
        self.grid.addWidget(F_predPC, 3, 0)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_UI()
        self.processor = Y86Processor()

    def init_UI(self):
        self.main_widget = MainWidget()

        self.init_menubar()

        self.setCentralWidget(self.main_widget)

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

    def show_warning_message(self, string):
        message_box = QMessageBox()
        message_box.setText(string)
        message_box.exec_()

    def show_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Load file', '~')
        fname = fname[0]

        file_suffix = re.search(r"(?<=\.).*$", fname)

        if not file_suffix:
            self.show_warning_message('Please choose a .yo file')
            return
        else:
            file_suffix = file_suffix.group(0)
            if file_suffix != 'yo':
                self.show_warning_message('Please choose a .yo file')
                return

        f = open(fname, 'r')

        with f:
            data = f.readlines()
            self.processor.set_input_file(data)
            self.src_text.setText(''.join(line for line in data))

        f.close()

    def run(self):
        print('run')
        self.processor.run_processor()
        return

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
