#!/usr/bin/python

import io
import re
import sys

class Y86Processor():
    def __init__(self, bin_code):
        # Global constants

        ## Symbolic representation of Y86 Instruction Codes
        self.INOP    = 0x0
        self.IHALT   = 0x1
        self.IRRMOVL = 0x2
        self.IIRMOVL = 0x3
        self.IRMMOVL = 0x4
        self.IMRMOVL = 0x5
        self.IOPL    = 0x6
        self.IJXX    = 0x7
        self.ICALL   = 0x8
        self.IRET    = 0x9
        self.IPUSHL  = 0xa
        self.IPOPL   = 0xb
        self.IIADDL  = 0xc
        self.ILEAVE  = 0xd

        ## Symbolic represenations of Y86 function codes
        self.FNONE   = 0x0

        ## Symbolic representation of Y86 Registers referenced
        self.RESP    = 0x4
        self.REBP    = 0x5
        self.RNONE   = 0x8

        ## ALU Functions referenced explicitly
        self.ALUADD  = 0x0
        self.ALUSUB  = 0x1
        self.ALUAND  = 0x2
        self.ALUXOR  = 0x3

        ## Symbolic representation of Y86 status
        self.SBUB    = 'STAT_BUB' # Bubble in stage
        self.SAOK    = 'STAT_AOK' # Normal execution
        self.SADR    = 'STAT_ADR' # Invalid memory address
        self.SINS    = 'STAT_INS' # Invalid instruction
        self.SHLT    = 'STAT_HLT' # Halt instruction encountered

        ## Jump function representations
        self.FJMP    = 0x0
        self.FJLE    = 0x1
        self.FJL     = 0x2
        self.FJE     = 0x3
        self.FJNE    = 0x4
        self.FJGE    = 0x5
        self.FJG     = 0x6

        # Processor Registers initializations

        ## Pipeline Register F
        self.F_stat = self.SBUB
        self.F_predPC = 0

        ## Intermediate Values in Fetch Stage
        self.f_icode = self.INOP
        self.f_ifun = self.FNONE
        self.f_valC = 0x0
        self.f_valP = 0x0
        self.f_rA = self.RNONE
        self.f_rB = self.RNONE
        self.f_predPC = 0
        self.f_stat = self.SBUB

        ## Pipeline Register D
        self.D_stat = self.SBUB
        self.D_icode = self.INOP
        self.D_ifun = self.FNONE
        self.D_rA = self.RNONE
        self.D_rB = self.RNONE
        self.D_valC = 0x0
        self.D_valP = 0x0

        ## Intermediate Values in Decode Stage
        self.d_srcA = self.RNONE
        self.d_srcB = self.RNONE
        self.d_dstE = self.RNONE
        self.d_dstM = self.RNONE
        self.d_valA = 0x0
        self.d_valB = 0x0

        ## Pipeline Register E
        self.E_stat = self.SBUB
        self.E_icode = self.INOP
        self.E_ifun = self.FNONE
        self.E_valC = 0x0
        self.E_valA = 0x0
        self.E_valB = 0x0
        self.E_dstE = self.RNONE
        self.E_dstM = self.RNONE
        self.E_srcA = self.RNONE
        self.E_srcB = self.RNONE

        ## Intermediate Values in Execute Stage
        self.e_valE = 0x0
        self.e_dstE = self.RNONE
        self.e_Cnd = False
        self.e_setcc = False

        ## Pipeline Register M
        self.M_stat = self.SBUB
        self.M_icode = self.INOP
        self.M_ifun = self.FNONE
        self.M_Cnd = False   # M_Bch
        self.M_valE = 0x0
        self.M_valA = 0x0
        self.M_dstE = self.RNONE
        self.M_dstM = self.RNONE

        ## Intermediate Values in Memory Stage
        self.m_valM = 0x0
        self.m_stat = self.SBUB
        self.mem_addr = 0x0
        self.m_read = False
        self.dmem_error = False

        ## Pipeline Register W
        self.W_stat = self.SBUB
        self.W_icode = self.INOP
        self.W_ifun = self.FNONE
        self.W_valE = 0x0
        self.W_valM = 0x0
        self.W_dstE = self.RNONE
        self.W_dstM = self.RNONE

        # Registers initialization
        self.registers = {
            0x0: 0,
            0x1: 0,
            0x2: 0,
            0x3: 0,
            0x4: 0,
            0x5: 0,
            0x6: 0,
            0x7: 0,
            0xf: 0
        }

        self.bin_code = bin_code
        self.addr_len = len(self.bin_code) / 2 - 1

    def run_processor(self):
        pass

addr_re = re.compile(r"(?<=0x).*?(?=:)")
code_re = re.compile(r"(?<=:\s)\w+")

def get_addr(string):
    search_result = addr_re.search(string)
    if search_result:
        return int(search_result.group(0), 16)
    return None

def get_code(string):
    search_result = code_re.search(string)
    if search_result:
        return search_result.group(0)
    return None

def init(input_file):
    fin = open(input_file, 'r')
    p = 0x000
    bin_code = ''
    for line in fin:
        addr, code = get_addr(line), get_code(line)
        bin_len = len(bin_code)
        if addr is not None:
            addr *= 2
            if addr < bin_len:
                print("Init Error")
                sys.exit(1)
            if code is not None:
                if addr > bin_len:
                    bin_code += '0' * (addr - bin_len)
                bin_code += code
    return bin_code

def main():
    input_file = 'asum.yo'
    bin_code = init(input_file)
    processor = Y86Processor(bin_code)
    processor.run_processor()

main()
