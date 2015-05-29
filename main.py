#!/usr/bin/python

import io
import re
import sys

class Y86Processor():
    def __init__(self, bin_code, output_file):
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

        ## Symbolic represenations of Y86 function codes
        self.FNONE   = 0x0

        ## Symbolic representation of Y86 Registers referenced
        self.RESP    = 0x4
        self.RNONE   = 0x8

        ## ALU Functions referenced explicitly
        self.ALUADD  = 0x0
        self.ALUSUB  = 0x1
        self.ALUAND  = 0x2
        self.ALUXOR  = 0x3

        ## Symbolic representation of Y86 status
        self.SBUB    = 'BUB' # Bubble in stage
        self.SAOK    = 'AOK' # Normal execution
        self.SADR    = 'ADR' # Invalid memory address
        self.SINS    = 'INS' # Invalid instruction
        self.SHLT    = 'HLT' # Halt instruction encountered

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
        }

        self.bin_code = bin_code
        self.output_file = output_file
        self.addr_len = len(self.bin_code) / 2 - 1

        self.cycle = -1

    def endian_parser(self, s):
        correct_string = s[6] + s[7] + s[4] + s[5] + s[2] + s[3] + s[0] + s[1]
        ans = int(correct_string, 16)
        return ans

    def cycle_log(self):
        self.output_file.write('Cycle_%d\n--------------------\n' % self.cycle)

    def fetch_stage(self):
        ## Initialization
        self.f_icode = self.INOP
        self.f_ifun = self.FNONE
        self.f_rA = self.RNONE
        self.f_rB = self.RNONE
        self.f_valC = 0x0
        self.f_valP = 0x0

        ## What address should instruction be fetched at
        f_pc = self.F_predPC # Default: Use predicted value of PC
        if (self.M_icode == self.IJXX) and (not self.M_Cnd):
            f_pc = self.M_valA # Mispredicted branch. Fetch at incremented PC
        elif (self.W_icode == self.IRET):
            f_pc = self.W_valM # Completion of RET instruction.

        saved_pc = f_pc
        bin_p = f_pc * 2
        imem_error = False

        ## Check if imem_error
        if (f_pc > self.addr_len) or (f_pc < 0):
            imem_error = True
        else:
            imem_code = int(self.bin_code[bin_p], 16)
            imem_ifun = int(self.bin_code[bin_p+1], 16)
            bin_p += 2
            f_pc += 1

        ## Determine icode of fetched instruction
        self.f_icode = self.INOP if imem_error else imem_code
        ## Determine ifun
        self.f_ifun = self.FNONE if imem_error else imem_ifun

        # Is instruction valid?
        instr_valid = self.f_ifun in (self.INOP, self.IHALT, self.IRRMOVL, \
                                      self.IIRMOVL, self.IRMMOVL, self.IMRMOVL, \
                                      self.IOPL, self.IJXX, self.ICALL, \
                                      self.IRET, self.IPUSHL, self.IPOPL)

        # Does fetched instruction require a regid byte?
        need_regids = self.f_icode in (self.IRRMOVL, self.IOPL, self.IPUSHL, \
                                       self.IPOPL, self.IIRMOVL, self.IRMMOVL, \
                                       self.IMRMOVL)

        # Does fetched instruction require a constant word?
        need_valC = self.f_icode in (self.IIRMOVL, self.IRMMOVL, self.IMRMOVL, \
                                     self.IJXX, self.ICALL)

        if instr_valid:
            try:
                if need_regids:
                    self.f_rA = int(self.bin_code[bin_p], 16)
                    self.f_rB = int(self.bin_code[bin_p+1], 16)
                    bin_p += 2
                    f_pc += 1
                    if ((self.f_rA not in self.registers) and (self.f_rA != self.RNONE))\
                       or ((self.f_rB not in self.registers) and (self.f_rB != self.RNONE)):
                        raise IndexError
                if need_valC:
                    self.f_valC = self.endian_parser(self.bin_code[bin_p: bin_p+8])
                    bin_p += 8
                    f_pc += 4
            except IndexError:
                imem_error = True

        self.f_valP = f_pc
        self.f_predPC = self.f_valC if self.f_icode in (self.IJXX, self.ICALL) else self.f_valP

        # Determine status code for fetched instruction
        self.f_stat = self.SAOK # Default
        if self.f_icode == self.IHALT:
            self.f_stat = self.SHLT
        if not instr_valid:
            self.f_stat = self.SINS
        if imem_error:
            self.f_stat = self.SADR

    def fetch_write(self):
        F_bubble = False
        F_stall = (self.IRET in (self.D_icode, self.E_icode, self.M_icode)) or \
                  ((self.E_icode in (self.IMRMOVL, self.IPOPL)) and \
                   (self.e_dstM in (self.d_srcA, self.d_srcB)))
        if F_stall:
            return
        self.F_predPC = self.f_predPC
        self.F_stat = self.f_stat

    def fetch_log(self):
        self.output_file.write('FETCH:\n')
        self.output_file.write('  F_predPC  = 0x%08x\n' % self.F_predPC)
        self.output_file.write('\n')

    def run_processor(self):
        for i in range(100):
            self.cycle += 1
            self.cycle_log()
            self.fetch_stage()
            self.fetch_log()
            self.fetch_write()

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
    output_file = open('asum.out', 'w')
    bin_code = init(input_file)
    processor = Y86Processor(bin_code, output_file)
    processor.run_processor()

main()
