#!/usr/bin/python

import io
import sys
import re
from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QApplication,
                             QFileDialog, QAction, QTextEdit, QMessageBox,
                             QGridLayout, QLabel, QLineEdit, QWidget,
                             QPushButton, QInputDialog, QSlider)
from PyQt5.QtCore import QTimer, Qt
from processor import Y86Processor, special_hex

class MainWidget(QWidget):

    def __init__(self):
        super(MainWidget, self).__init__()
        self.processor = Y86Processor()
        self.current_step = 0
        self.timer_interval = 1
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(5)

        self.init_processor_info()

        self.init_textarea()

        self.init_buttons()

        self.setLayout(self.grid)

    def init_textarea(self):
        asum_code = QLabel('<h2>Code:</h2>')
        self.grid.addWidget(asum_code, 20, 0)
        self.src_text = QTextEdit()
        self.src_text.setReadOnly(True)
        self.grid.addWidget(self.src_text, 21, 0, 20, 20)

    def init_buttons(self):
        control = QLabel('<h2>Control:</h2>')
        self.grid.addWidget(control, 12, 8)

        load_button = QPushButton('Load')
        load_button.clicked.connect(self.show_file_dialog)
        self.grid.addWidget(load_button, 13, 8)

        run_button = QPushButton('Run')
        run_button.clicked.connect(self.run)
        self.grid.addWidget(run_button, 14, 8)

        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset)
        self.grid.addWidget(reset_button, 14, 9)

        step_button = QPushButton('Step')
        step_button.clicked.connect(self.step)
        self.grid.addWidget(step_button, 15, 8)

        back_button = QPushButton('Back')
        back_button.clicked.connect(self.back)
        self.grid.addWidget(back_button, 15, 9)

        set_interval_button = QPushButton('Interval')
        set_interval_button.clicked.connect(self.show_set_interval_dialog)
        self.grid.addWidget(set_interval_button, 16, 8)

    def init_fetch(self):
        fetch = QLabel('<b>Fetch:</b>')
        F_predPC = QLabel('F_predPC:')
        self.F_predPC_text = QLineEdit()
        self.F_predPC_text.setReadOnly(True)

        self.grid.addWidget(fetch, 2, 0)
        self.grid.addWidget(F_predPC, 3, 0)
        self.grid.addWidget(self.F_predPC_text, 3, 1)


    def init_decode(self):
        decode  = QLabel('<b>Decode:</b>')
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

    def init_execute(self):
        execute = QLabel('<b>Execute:</b>')
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

    def init_memory(self):
        memory = QLabel('<b>Memory:</b>')
        M_icode = QLabel('M_icode:')
        M_Bch   = QLabel('M_Bch:')
        M_valE  = QLabel('M_valE:')
        M_valA  = QLabel('M_valA:')
        M_dstE  = QLabel('M_dstE:')
        M_dstM  = QLabel('M_dstM:')

        self.M_icode_text = QLineEdit()
        self.M_Bch_text   = QLineEdit()
        self.M_valE_text  = QLineEdit()
        self.M_valA_text  = QLineEdit()
        self.M_dstE_text  = QLineEdit()
        self.M_dstM_text  = QLineEdit()

        self.M_icode_text.setReadOnly(True)
        self.M_Bch_text.setReadOnly(True)
        self.M_valE_text.setReadOnly(True)
        self.M_valA_text.setReadOnly(True)
        self.M_dstE_text.setReadOnly(True)
        self.M_dstM_text.setReadOnly(True)

        self.grid.addWidget(memory, 12, 0)
        self.grid.addWidget(M_icode, 13, 0)
        self.grid.addWidget(M_Bch, 13, 2)
        self.grid.addWidget(M_valE, 14, 0)
        self.grid.addWidget(M_valA, 14, 2)
        self.grid.addWidget(M_dstE, 15, 0)
        self.grid.addWidget(M_dstM, 15, 2)
        self.grid.addWidget(self.M_icode_text, 13, 1)
        self.grid.addWidget(self.M_Bch_text, 13, 3)
        self.grid.addWidget(self.M_valE_text, 14, 1)
        self.grid.addWidget(self.M_valA_text, 14, 3)
        self.grid.addWidget(self.M_dstE_text, 15, 1)
        self.grid.addWidget(self.M_dstM_text, 15, 3)

    def init_write_back(self):
        write_back = QLabel('<b>Write Back:</b>')
        W_icode = QLabel('W_icode:')
        W_valE  = QLabel('W_valE:')
        W_valM  = QLabel('W_valM:')
        W_dstE  = QLabel('W_dstE:')
        W_dstM  = QLabel('W_dstM:')

        self.W_icode_text = QLineEdit()
        self.W_valE_text  = QLineEdit()
        self.W_valM_text  = QLineEdit()
        self.W_dstE_text  = QLineEdit()
        self.W_dstM_text  = QLineEdit()

        self.W_icode_text.setReadOnly(True)
        self.W_valE_text.setReadOnly(True)
        self.W_valM_text.setReadOnly(True)
        self.W_dstE_text.setReadOnly(True)
        self.W_dstM_text.setReadOnly(True)

        self.grid.addWidget(write_back, 16, 0)
        self.grid.addWidget(W_icode, 17, 0)
        self.grid.addWidget(W_valE, 18, 0)
        self.grid.addWidget(W_valM, 18, 2)
        self.grid.addWidget(W_dstE, 19, 0)
        self.grid.addWidget(W_dstM, 19, 2)
        self.grid.addWidget(self.W_icode_text, 17, 1)
        self.grid.addWidget(self.W_valE_text, 18, 1)
        self.grid.addWidget(self.W_valM_text, 18, 3)
        self.grid.addWidget(self.W_dstE_text, 19, 1)
        self.grid.addWidget(self.W_dstM_text, 19, 3)

    def init_cpu_conditions(self):
        conditions = QLabel('<h2>Conditions:</h2>')
        self.grid.addWidget(conditions, 1, 8)

        ZF = QLabel('ZF:')
        SF = QLabel('SF:')
        OF = QLabel('OF:')

        self.ZF_text = QLineEdit()
        self.SF_text = QLineEdit()
        self.OF_text = QLineEdit()
        self.ZF_text.setReadOnly(True)
        self.SF_text.setReadOnly(True)
        self.OF_text.setReadOnly(True)

        self.grid.addWidget(ZF, 2, 8)
        self.grid.addWidget(self.ZF_text, 2, 9)
        self.grid.addWidget(SF, 2, 10)
        self.grid.addWidget(self.SF_text, 2, 11)
        self.grid.addWidget(OF, 2, 12)
        self.grid.addWidget(self.OF_text, 2, 13)

    def init_register_files(self):
        register_files = QLabel('<h2>Register File:</h2>')
        self.grid.addWidget(register_files, 3, 8)

        eax = QLabel('%eax:')
        ecx = QLabel('%ecx:')
        edx = QLabel('%edx:')
        ebx = QLabel('%ebx:')
        esp = QLabel('%esp:')
        ebp = QLabel('%ebp:')
        esi = QLabel('%esi:')
        edi = QLabel('%edi:')

        self.grid.addWidget(eax, 4, 8)
        self.grid.addWidget(ecx, 4, 10)
        self.grid.addWidget(edx, 5, 8)
        self.grid.addWidget(ebx, 5, 10)
        self.grid.addWidget(esp, 6, 8)
        self.grid.addWidget(ebp, 6, 10)
        self.grid.addWidget(esi, 7, 8)
        self.grid.addWidget(edi, 7, 10)

        self.eax_text = QLineEdit()
        self.ecx_text = QLineEdit()
        self.edx_text = QLineEdit()
        self.ebx_text = QLineEdit()
        self.esp_text = QLineEdit()
        self.ebp_text = QLineEdit()
        self.esi_text = QLineEdit()
        self.edi_text = QLineEdit()

        self.eax_text.setReadOnly(True)
        self.ecx_text.setReadOnly(True)
        self.edx_text.setReadOnly(True)
        self.ebx_text.setReadOnly(True)
        self.esp_text.setReadOnly(True)
        self.ebp_text.setReadOnly(True)
        self.esi_text.setReadOnly(True)
        self.edi_text.setReadOnly(True)

        self.grid.addWidget(self.eax_text, 4, 9)
        self.grid.addWidget(self.ecx_text, 4, 11)
        self.grid.addWidget(self.edx_text, 5, 9)
        self.grid.addWidget(self.ebx_text, 5, 11)
        self.grid.addWidget(self.esp_text, 6, 9)
        self.grid.addWidget(self.ebp_text, 6, 11)
        self.grid.addWidget(self.esi_text, 7, 9)
        self.grid.addWidget(self.edi_text, 7, 11)

    def init_processor_info(self):
        processor_info = QLabel('<h2>Registers:</h2>')
        self.grid.addWidget(processor_info, 1, 0)
        cycle = QLabel('<b>Cycle:</b>')
        self.cycle_text = QLineEdit()
        self.cycle_text.setReadOnly(True)
        self.grid.addWidget(cycle, 0, 0)
        self.grid.addWidget(self.cycle_text, 0, 1)

        self.init_fetch()
        self.init_decode()
        self.init_execute()
        self.init_memory()
        self.init_write_back()

        self.init_cpu_conditions()
        self.init_register_files()

        self.update_processor_info()

    def update_processor_info(self, step=-1):
        if step == -1:
            self.cycle_text.setText('0')
            self.ZF_text.setText('0')
            self.SF_text.setText('0')
            self.OF_text.setText('0')
            self.eax_text.setText('0x00000000')
            self.ecx_text.setText('0x00000000')
            self.edx_text.setText('0x00000000')
            self.ebx_text.setText('0x00000000')
            self.esp_text.setText('0x00000000')
            self.ebp_text.setText('0x00000000')
            self.esi_text.setText('0x00000000')
            self.edi_text.setText('0x00000000')
            self.F_predPC_text.setText('0x0')
            self.D_icode_text.setText('0x0')
            self.D_ifun_text.setText('0x0')
            self.D_rA_text.setText('0x8')
            self.D_rB_text.setText('0x8')
            self.D_valC_text.setText('0x00000000')
            self.D_valP_text.setText('0x00000000')
            self.E_icode_text.setText('0x0')
            self.E_ifun_text.setText('0x0')
            self.E_valC_text.setText('0x00000000')
            self.E_valA_text.setText('0x00000000')
            self.E_valB_text.setText('0x00000000')
            self.E_dstE_text.setText('0x8')
            self.E_dstM_text.setText('0x8')
            self.E_srcA_text.setText('0x8')
            self.E_srcB_text.setText('0x8')
            self.M_icode_text.setText('0x0')
            self.M_Bch_text.setText('0x0')
            self.M_valE_text.setText('0x00000000')
            self.M_valA_text.setText('0x00000000')
            self.M_dstE_text.setText('0x8')
            self.M_dstM_text.setText('0x8')
            self.W_icode_text.setText('0x0')
            self.W_valE_text.setText('0x00000000')
            self.W_valM_text.setText('0x00000000')
            self.W_dstE_text.setText('0x8')
            self.W_dstM_text.setText('0x8')
        else:
            try:
                self.cycle_text.setText(str(step))
                self.ZF_text.setText(str(self.processor.log[step]['condition_code']['ZF']))
                self.SF_text.setText(str(self.processor.log[step]['condition_code']['SF']))
                self.OF_text.setText(str(self.processor.log[step]['condition_code']['OF']))
                self.eax_text.setText(special_hex(self.processor.log[step]['registers'][0]))
                self.ecx_text.setText(special_hex(self.processor.log[step]['registers'][1]))
                self.edx_text.setText(special_hex(self.processor.log[step]['registers'][2]))
                self.ebx_text.setText(special_hex(self.processor.log[step]['registers'][3]))
                self.esp_text.setText(special_hex(self.processor.log[step]['registers'][4]))
                self.ebp_text.setText(special_hex(self.processor.log[step]['registers'][5]))
                self.esi_text.setText(special_hex(self.processor.log[step]['registers'][6]))
                self.edi_text.setText(special_hex(self.processor.log[step]['registers'][7]))
                self.F_predPC_text.setText(self.processor.log[step]['F_predPC'])
                self.D_icode_text.setText(self.processor.log[step]['D_icode'])
                self.D_ifun_text.setText(self.processor.log[step]['D_ifun'])
                self.D_rA_text.setText(self.processor.log[step]['D_rA'])
                self.D_rB_text.setText(self.processor.log[step]['D_rB'])
                self.D_valC_text.setText(self.processor.log[step]['D_valC'])
                self.D_valP_text.setText(self.processor.log[step]['D_valP'])
                self.E_icode_text.setText(self.processor.log[step]['E_icode'])
                self.E_ifun_text.setText(self.processor.log[step]['E_ifun'])
                self.E_valC_text.setText(self.processor.log[step]['E_valC'])
                self.E_valA_text.setText(self.processor.log[step]['E_valA'])
                self.E_valB_text.setText(self.processor.log[step]['E_valB'])
                self.E_dstE_text.setText(self.processor.log[step]['E_dstE'])
                self.E_dstM_text.setText(self.processor.log[step]['E_dstM'])
                self.E_srcA_text.setText(self.processor.log[step]['E_srcA'])
                self.E_srcB_text.setText(self.processor.log[step]['E_srcB'])
                self.M_icode_text.setText(self.processor.log[step]['M_icode'])
                self.M_Bch_text.setText(self.processor.log[step]['M_Bch'])
                self.M_valE_text.setText(self.processor.log[step]['M_valE'])
                self.M_valA_text.setText(self.processor.log[step]['M_valA'])
                self.M_dstE_text.setText(self.processor.log[step]['M_dstE'])
                self.M_dstM_text.setText(self.processor.log[step]['M_dstM'])
                self.W_icode_text.setText(self.processor.log[step]['W_icode'])
                self.W_valE_text.setText(self.processor.log[step]['W_valE'])
                self.W_valM_text.setText(self.processor.log[step]['W_valM'])
                self.W_dstE_text.setText(self.processor.log[step]['W_dstE'])
                self.W_dstM_text.setText(self.processor.log[step]['W_dstM'])
            except IndexError:
                self.show_warning_message('Run time error')

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
            self.processor.run_processor()

        f.close()

    def show_set_interval_dialog(self):
        val, ok = QInputDialog.getInt(self, 'Set Running interval', 'Enter the interval value:')
        if ok:
            try:
                self.timer_interval = val
            except:
                self.show_warning_message('Invalid value')

    def run_helper(self):
        if self.current_step == self.processor.cycle:
            self.run_timer.stop()
            self.show_warning_message('Process finished')
            return
        self.current_step += 1
        self.update_processor_info(self.current_step)

    def run(self):
        if not self.processor.log:
            self.show_warning_message('Please choose a .yo file first')
            return
        self.current_step = 0
        self.run_timer = QTimer()
        self.run_timer.timeout.connect(self.run_helper)
        self.run_timer.start(self.timer_interval)
        return

    def step(self):
        if not self.processor.log:
            self.show_warning_message('Please choose a .yo file first')
            return
        if self.current_step == self.processor.cycle:
            self.show_warning_message('Process finished')
            return
        self.current_step += 1
        self.update_processor_info(self.current_step)
        pass

    def back(self):
        if not self.processor.log:
            self.show_warning_message('Please choose a .yo file first')
            return
        if self.current_step == 0:
            self.show_warning_message('This is the first cycle')
            return
        self.current_step -= 1
        self.update_processor_info(self.current_step)
        pass

    def reset(self):
        if not self.processor.log:
            self.show_warning_message('Please choose a .yo file first')
            return
        self.current_step = 0
        self.update_processor_info(self.current_step)
        pass

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_UI()

    def init_UI(self):
        self.main_widget = MainWidget()

        self.init_menubar()

        self.setCentralWidget(self.main_widget)

        WINDOW_WIDTH = 1280
        WINDOW_HEIGHT = 720
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.center()
        self.setWindowTitle('Y86 Pipeline Simulator')
        self.show()

        test = QTextEdit()
        test.setGeometry(100, 100, 100, 100)
        test.show()

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
