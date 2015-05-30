#!/usr/bin/python

import io
import re
import sys

TMAX = 2**31-1
TMIN = -TMAX -1

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

        # Conditions registers
        self.conditions = {
            'ZF': 0,
            'SF': 0,
            'OF': 0,
        }

        # Memory
        self.memory = {}
        self.memro = []

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
        ## Intermediate Values in Fetch Stage
        self.f_icode = self.INOP
        self.f_ifun = self.FNONE
        self.f_valC = 0x0
        self.f_valP = 0x0
        self.f_rA = self.RNONE
        self.f_rB = self.RNONE
        self.f_predPC = 0
        self.f_stat = self.SBUB

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
                   (self.E_dstM in (self.d_srcA, self.d_srcB)))
        if F_stall:
            return
        self.F_predPC = self.f_predPC
        self.F_stat = self.f_stat

    def fetch_log(self):
        self.output_file.write('FETCH:\n')
        self.output_file.write('\tF_predPC  = 0x%08x\n' % self.F_predPC)
        self.output_file.write('\n')

    def decode_stage(self):
        ## Intermediate Values in Decode Stage
        self.d_srcA = self.RNONE
        self.d_srcB = self.RNONE
        self.d_dstE = self.RNONE
        self.d_dstM = self.RNONE
        self.d_valA = 0x0
        self.d_valB = 0x0

        if self.D_icode in (self.IRRMOVL, self.IRMMOVL, self.IOPL, self.IPUSHL):
            self.d_srcA = self.D_rA
        elif self.D_icode in (self.IPOPL, self.IRET):
            self.d_srcA = self.RESP

        if self.D_icode in (self.IOPL, self.IRMMOVL, self.IMRMOVL):
            self.d_srcB = self.D_rB
        elif self.D_icode in (self.IPUSHL, self.IPOPL, self.ICALL, self.IRET):
            self.d_srcB = self.RESP

        if self.D_icode in (self.IRRMOVL, self.IIRMOVL, self.IOPL):
            self.d_dstE = self.D_rB
        elif self.D_icode in (self.IPUSHL, self.IPOPL, self.ICALL, self.IRET):
            self.d_dstE = self.RESP

        if self.D_icode in (self.IMRMOVL, self.IPOPL):
            self.d_dstM = self.D_rA

        if self.D_icode in (self.ICALL, self.IJXX):
            self.d_valA = self.D_valP
        elif self.d_srcA == self.e_dstE:
            self.d_valA = self.e_valE
        elif self.d_srcA == self.M_dstM:
            self.d_valA = self.m_valM
        elif self.d_srcA == self.M_dstE:
            self.d_valA = self.M_valE
        elif self.d_srcA == self.W_dstM:
            self.d_valA = self.W_valM
        elif self.d_srcA == self.W_dstE:
            self.d_valA = self.W_valE
        else:
            self.d_valA = self.registers[self.d_srcA]

        if self.d_srcB == self.e_dstE:
            self.d_valB = self.e_valE
        elif self.d_srcB == self.M_dstM:
            self.d_valB = self.m_valM
        elif self.d_srcB == self.M_dstE:
            self.d_valB = self.M_valE
        elif self.d_srcB == self.W_dstM:
            self.d_valB = self.W_valM
        elif self.d_srcB == self.W_dstE:
            self.d_valB = self.W_valE
        else:
            self.d_valB = self.registers[self.d_srcB]

    def decode_write(self):
        D_stall = (self.E_icode in (self.IMRMOVL, self.IPOPL)) and \
                  (self.E_dstM in (self.d_srcA, self.d_srcB))
        if D_stall:
            return

        D_bubble = (self.E_icode == self.IJXX and (not self.e_Cnd)) or \
                   ((not ((self.E_icode in (self.IMRMOVL, self.IPOPL)) \
                          and (self.E_dstM in (self.d_srcA, self.d_srcB)))) \
                    and (self.IRET in (self.D_icode, self.E_icode, self.M_icode)))
        if D_bubble:
            self.D_icode = self.INOP
            self.D_ifun  = self.FNONE
            self.D_rA    = self.RNONE
            self.D_rB    = self.RNONE
            self.D_valC  = 0x0
            self.D_valP  = 0x0
            self.D_stat  = self.SBUB
            return

        self.D_stat  = self.f_stat
        self.D_icode = self.f_icode
        self.D_ifun  = self.f_ifun
        self.D_rA    = self.f_rA
        self.D_rB    = self.f_rB
        self.D_valC  = self.f_valC
        self.D_valP  = self.f_valP

    def decode_log(self):
        self.output_file.write('DECODE:\n')
        self.output_file.write('\tD_icode  	= 0x%x\n' % self.D_icode)
        self.output_file.write('\tD_ifun  	= 0x%x\n' % self.D_ifun)
        self.output_file.write('\tD_rA  	= 0x%x\n' % self.D_rA)
        self.output_file.write('\tD_rB  	= 0x%x\n' % self.D_rB)
        self.output_file.write('\tD_valC  	= 0x%08x\n' % self.D_valC)
        self.output_file.write('\tD_valP  	= 0x%08x\n' % self.D_valP)
        self.output_file.write('\n')

    def execute_stage(self):
        self.e_valE = 0x0
        self.e_dstE = self.RNONE
        self.e_Cnd = False

        aluA = 0
        aluB = 0
        alufun = self.ALUADD

        if self.E_icode in (self.IRRMOVL, self.IOPL):
            aluA = self.E_valA
        elif self.E_icode in (self.IIRMOVL, self.IRMMOVL, self.IMRMOVL):
            aluA = self.E_valC
        elif self.E_icode in (self.ICALL, self.IPUSHL):
            aluA = -4
        elif self.E_icode in (self.IRET, self.IPOPL):
            aluA = 4

        if self.E_icode in (self.IRMMOVL, self.IMRMOVL, self.IOPL, self.ICALL, \
                            self.IPUSHL, self.IRET, self.IPOPL):
            aluB = self.E_valB
        elif self.E_icode in (self.IRRMOVL, self.IIRMOVL):
            aluB = 0

        if self.E_icode == self.IOPL:
            alufun = self.E_ifun

        set_cc = (self.E_icode == self.IOPL) and \
                 (self.m_stat not in (self.SADR, self.SINS, self.SHLT)) and \
                 (self.W_stat not in (self.SADR, self.SINS, self.SHLT))

        alu_result = 0

        if alufun == self.ALUADD:
            alu_result = aluB + aluA
        if alufun == self.ALUSUB:
            alu_result = aluB - aluA
        if alufun == self.ALUAND:
            alu_result = aluB & aluA
        if alufun == self.ALUXOR:
            alu_result = aluB ^ aluA

        if set_cc:
            self.conditions['ZF'] = 1 if alu_result == 0 else 0
            self.conditions['SF'] = 1 if alu_result < 0 else 0
            self.conditions['OF'] = 1 if (alu_result > TMAX) or (alu_result < TMIN) else 0

        if self.E_icode in (self.IJXX, self.IRRMOVL):
            zf = self.conditions['ZF']
            sf = self.conditions['SF']
            of = self.conditions['OF']
            if self.E_ifun == self.FJMP:
                self.e_Cnd = True
            if (self.E_ifun == self.FJL) and (sf ^ of == 1):
                self.e_Cnd = True
            if (self.E_ifun == self.FJLE) and ((sf ^ of) | zf == 1):
                self.e_Cnd = True
            if (self.E_ifun == self.FJE) and (zf == 1):
                self.e_Cnd = True
            if (self.E_ifun == self.FJNE) and (zf == 0):
                self.e_Cnd = True
            if (self.E_ifun == self.FJGE) and (sf ^ of == 0):
                self.e_Cnd = True
            if (self.E_ifun == self.FJG) and ((sf ^ of) | zf == 0):
                self.e_Cnd = True

        self.e_valE = alu_result
        self.e_dstE = self.RNONE if (self.E_icode == self.IRRMOVL and not self.e_Cnd) else self.E_dstE

    def execute_write(self):
        E_bubble = (self.E_icode == self.IJXX and not self.e_Cnd) or \
                   ((self.E_icode in (self.IMRMOVL, self.IPOPL)) and \
                    (self.E_dstM in (self.d_srcA, self.d_srcB)))
        if E_bubble:
            self.E_icode = self.INOP
            self.E_ifun  = self.FNONE
            self.E_valC  = 0x0
            self.E_valA  = 0x0
            self.E_valB  = 0x0
            self.E_dstE  = self.RNONE
            self.E_dstM  = self.RNONE
            self.E_srcA  = self.RNONE
            self.E_srcB  = self.RNONE
            self.E_stat  = self.SBUB
            return

        self.E_stat  = self.D_stat
        self.E_icode = self.D_icode
        self.E_ifun  = self.D_ifun
        self.E_valC  = self.D_valC
        self.E_valA  = self.d_valA
        self.E_valB  = self.d_valB
        self.E_dstE  = self.d_dstE
        self.E_dstM  = self.d_dstM
        self.E_srcA  = self.d_srcA
        self.E_srcB  = self.d_srcB

    def execute_log(self):
        self.output_file.write('EXECUTE:\n')
        self.output_file.write('\tE_icode   = 0x%x:\n' % self.E_icode)
        self.output_file.write('\tE_ifun    = 0x%x:\n' % self.E_ifun)
        self.output_file.write('\tE_valC    = 0x%08x:\n' % self.E_valC)
        self.output_file.write('\tE_valA    = 0x%08x:\n' % self.E_valA)
        self.output_file.write('\tE_valB    = 0x%08x:\n' % self.E_valB)
        self.output_file.write('\tE_dstE    = 0x%x:\n' % self.E_dstE)
        self.output_file.write('\tE_dstM    = 0x%x:\n' % self.E_dstM)
        self.output_file.write('\tE_srcA    = 0x%x:\n' % self.E_srcA)
        self.output_file.write('\tE_srcB    = 0x%x:\n' % self.E_srcB)
        self.output_file.write('\n')

    def memory_stage(self):
        ## Intermediate Values in Memory Stage
        self.m_valM = 0x0
        self.m_stat = self.SBUB
        self.mem_addr = 0x0
        self.m_read = False
        self.dmem_error = False

        if self.M_icode in (self.IRMMOVL, self.IPUSHL, self.ICALL, self.IMRMOVL):
            self.mem_addr = self.M_valE
        elif self.M_icode in (self.IPOPL, self.IRET):
            self.mem_addr = self.M_valA

        mem_read = self.M_icode in (self.IMRMOVL, self.IPOPL, self.IRET)

        mem_write = self.M_icode in (self.IRMMOVL, self.IPUSHL, self.ICALL)

        if mem_read:
            try:
                if self.mem_addr not in self.memory:
                    addr = self.mem_addr * 2
                    self.memory[self.mem_addr] = self.endian_parser(self.bin_code[addr: addr+8])
                    self.memro.append(self.mem_addr)
                self.m_valM = self.memory[self.mem_addr]
                self.m_read = True
            except:
                self.dmem_error = True

        if mem_write:
            try:
                if self.mem_addr in self.memro or self.mem_addr < 0:
                    raise Exception
                self.memory[mem_addr] = self.M_valA
            except:
                self.dmem_error = True

        self.m_stat = self.SADR if self.dmem_error else self.M_stat

    def memory_write(self):
        M_bubble = self.m_stat in (self.SADR, self.SINS, self.SHLT) or \
                   self.W_stat in (self.SADR, self.SINS, self.SHLT)

        if M_bubble:
            self.M_stat  = self.SBUB
            self.M_icode = self.INOP
            self.M_ifun  = self.FNONE
            self.M_Cnd   = False
            self.M_valE  = 0x0
            self.M_valA  = 0x0
            self.M_dstE  = self.RNONE
            self.M_dstM  = self.RNONE
            return

        self.M_stat  = self.E_stat
        self.M_icode = self.E_icode
        self.M_ifun  = self.E_ifun
        self.M_Cnd   = self.e_Cnd
        self.M_valE  = self.e_valE
        self.M_valA  = self.E_valA
        self.M_dstE  = self.e_dstE
        self.M_dstM  = self.E_dstM

    def memory_log(self):
        self.output_file.write('MEMORY:\n')
        self.output_file.write('\tM_icode   = 0x%x:\n' % self.M_icode)
        self.output_file.write('\tM_Bch     = %s:\n' % str(self.M_Cnd).lower())
        self.output_file.write('\tM_valE    = 0x%08x:\n' % self.M_valE)
        self.output_file.write('\tM_valA    = 0x%08x:\n' % self.M_valA)
        self.output_file.write('\tM_dstE    = 0x%x:\n' % self.M_dstE)
        self.output_file.write('\tM_dstM    = 0x%x:\n' % self.M_dstM)
        self.output_file.write('\n')


    def run_processor(self):
        for i in range(100):
            self.cycle += 1
            self.cycle_log()

            self.memory_write()
            self.execute_write()
            self.decode_write()
            self.fetch_write()

            self.fetch_stage()
            self.decode_stage()
            self.execute_stage()
            self.memory_stage()

            self.fetch_log()
            self.decode_log()
            self.execute_log()
            self.memory_log()

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
