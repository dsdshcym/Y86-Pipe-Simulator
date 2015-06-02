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
        self.processor = Y86Processor()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(15)

        self.init_processor_info()

        self.init_textarea()

        self.setLayout(self.grid)

    def init_textarea(self):
        self.src_text = QTextEdit()
        self.grid.addWidget(self.src_text, 5, 12, 10, 12)

    def init_processor_info(self):
        fetch = QLabel('Fetch:')
        F_predPC = QLabel('F_predPC:')
        self.F_predPC_text = QLineEdit()
        self.F_predPC_text.setReadOnly(True)

        self.grid.addWidget(fetch, 2, 0)
        self.grid.addWidget(F_predPC, 3, 0)
        self.grid.addWidget(self.F_predPC_text, 3, 1)

        decode  = QLabel('Decode:')
        D_icode = QLabel('D_icode:')
        D_ifun  = QLabel('D_ifun:')
        D_rA    = QLabel('D_rA:')
        D_rB    = QLabel('D_rB:')
        D_valC  = QLabel('D_valC:')
        D_valP  = QLabel('D_valP:')
        self.D_icode_text = QLineEdit()
        self.D_ifun_text  = QLineEdit()
        self.D_rA_text    = QLineEdit()
        self.D_rB_text    = QLineEdit()
        self.D_valC_text  = QLineEdit()
        self.D_valP_text  = QLineEdit()

        self.D_icode_text.setReadOnly(True)
        self.D_ifun_text.setReadOnly(True)
        self.D_rA_text.setReadOnly(True)
        self.D_rB_text.setReadOnly(True)
        self.D_valC_text.setReadOnly(True)
        self.D_valP_text.setReadOnly(True)

        self.grid.addWidget(decode, 4, 0)
        self.grid.addWidget(D_icode, 5, 0)
        self.grid.addWidget(self.D_icode_text, 5, 1)
        self.grid.addWidget(D_ifun, 5, 2)
        self.grid.addWidget(self.D_ifun_text, 5, 3)
        self.grid.addWidget(D_rA, 6, 0)
        self.grid.addWidget(self.D_rA_text, 6, 1)
        self.grid.addWidget(D_rB, 6, 2)
        self.grid.addWidget(self.D_rB_text, 6, 3)
        self.grid.addWidget(D_valC, 7, 0)
        self.grid.addWidget(self.D_valC_text, 7, 1)
        self.grid.addWidget(D_valP, 7, 2)
        self.grid.addWidget(self.D_valP_text, 7, 3)

        execute = QLabel('Execute:')
        E_icode = QLabel('E_icode:')
        E_ifun  = QLabel('E_ifun:')
        E_valC  = QLabel('E_valC:')
        E_valA  = QLabel('E_valA:')
        E_valB  = QLabel('E_valB:')
        E_dstE  = QLabel('E_dstE:')
        E_dstM  = QLabel('E_dstM:')
        E_srcA  = QLabel('E_srcA:')
        E_srcB  = QLabel('E_srcB:')
        self.execute_text = QLineEdit()
        self.E_icode_text = QLineEdit()
        self.E_ifun_text  = QLineEdit()
        self.E_valC_text  = QLineEdit()
        self.E_valA_text  = QLineEdit()
        self.E_valB_text  = QLineEdit()
        self.E_dstE_text  = QLineEdit()
        self.E_dstM_text  = QLineEdit()
        self.E_srcA_text  = QLineEdit()
        self.E_srcB_text  = QLineEdit()

        self.execute_text.setReadOnly(True)
        self.E_icode_text.setReadOnly(True)
        self.E_ifun_text.setReadOnly(True)
        self.E_valC_text.setReadOnly(True)
        self.E_valA_text.setReadOnly(True)
        self.E_valB_text.setReadOnly(True)
        self.E_dstE_text.setReadOnly(True)
        self.E_dstM_text.setReadOnly(True)
        self.E_srcA_text.setReadOnly(True)
        self.E_srcB_text.setReadOnly(True)

        self.grid.addWidget(execute, 8, 0)
        self.grid.addWidget(E_icode, 9, 0)
        self.grid.addWidget(E_ifun, 9, 2)
        self.grid.addWidget(E_valC, 10, 0)
        self.grid.addWidget(E_valA, 10, 2)
        self.grid.addWidget(E_valB, 10, 4)
        self.grid.addWidget(E_dstE, 11, 0)
        self.grid.addWidget(E_dstM, 11, 2)
        self.grid.addWidget(E_srcA, 11, 4)
        self.grid.addWidget(E_srcB, 11, 6)
        self.grid.addWidget(self.E_icode_text, 9, 1)
        self.grid.addWidget(self.E_ifun_text, 9, 3)
        self.grid.addWidget(self.E_valC_text, 10, 1)
        self.grid.addWidget(self.E_valA_text, 10, 3)
        self.grid.addWidget(self.E_valB_text, 10, 5)
        self.grid.addWidget(self.E_dstE_text, 11, 1)
        self.grid.addWidget(self.E_dstM_text, 11, 3)
        self.grid.addWidget(self.E_srcA_text, 11, 5)
        self.grid.addWidget(self.E_srcB_text, 11, 7)

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

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_UI()

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
        open_file.triggered.connect(self.main_widget.show_file_dialog)

        run_file = QAction('Run', self)
        run_file.setShortcut('Ctrl+R')
        run_file.setStatusTip('Run a .yo file')
        run_file.triggered.connect(self.main_widget.run)

        step = QAction('Step', self)
        step.setShortcut('Ctrl+S')
        step.setStatusTip('Run for one step')
        step.triggered.connect(self.main_widget.step)

        back = QAction('Back', self)
        back.setShortcut('Ctrl+B')
        back.setStatusTip('Go back one step')
        back.triggered.connect(self.main_widget.back)

        reset = QAction('Reset', self)
        reset.setShortcut('Alt+R')
        reset.setStatusTip('Reset a running processor')
        reset.triggered.connect(self.main_widget.reset)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_file)
        processor_menu = menubar.addMenu('&Processor')
        processor_menu.addAction(run_file)
        processor_menu.addAction(step)
        processor_menu.addAction(back)
        processor_menu.addAction(reset)

# if __name__ == '__main__':
app = QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec_())
