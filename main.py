#!/usr/bin/python

import io
import re
import sys

# Global constants

## Symbolic representation of Y86 Instruction Codes
INOP    = 0x0
IHALT   = 0x1
IRRMOVL = 0x2
IIRMOVL = 0x3
IRMMOVL = 0x4
IMRMOVL = 0x5
IOPL    = 0x6
IJXX    = 0x7
ICALL   = 0x8
IRET    = 0x9
IPUSHL  = 0xa
IPOPL   = 0xb
IIADDL  = 0xc
ILEAVE  = 0xd

## Symbolic represenations of Y86 function codes
FNONE   = 0x0

## Symbolic representation of Y86 Registers referenced
RESP    = 0x4
REBP    = 0x5
RNONE   = 0x8

## ALU Functions referenced explicitly
ALUADD  = 0x0
ALUSUB  = 0x1
ALUAND  = 0x2
ALUXOR  = 0x3

## Symbolic representation of Y86 status
SBUB    = 'STAT_BUB' # Bubble in stage
SAOK    = 'STAT_AOK' # Normal execution
SADR    = 'STAT_ADR' # Invalid memory address
SINS    = 'STAT_INS' # Invalid instruction
SHLT    = 'STAT_HLT' # Halt instruction encountered

## Jump function representations
FJMP    = 0x0
FJLE    = 0x1
FJL     = 0x2
FJE     = 0x3
FJNE    = 0x4
FJGE    = 0x5
FJG     = 0x6

# Processor Registers initializations

## Pipeline Register F
F_stat = SBUB
F_predPC = 0

## Intermediate Values in Fetch Stage
f_icode = INOP
f_ifun = FNONE
f_valC = 0x0
f_valP = 0x0
f_rA = RNONE
f_rB = RNONE
f_predPC = 0
f_stat = SBUB

## Pipeline Register D
D_stat = SBUB
D_icode = INOP
D_ifun = FNONE
D_rA = RNONE
D_rB = RNONE
D_valC = 0x0
D_valP = 0x0

## Intermediate Values in Decode Stage
d_srcA = RNONE
d_srcB = RNONE
d_dstE = RNONE
d_dstM = RNONE
d_valA = 0x0
d_valB = 0x0

## Pipeline Register E
E_stat = SBUB
E_icode = INOP
E_ifun = FNONE
E_valC = 0x0
E_valA = 0x0
E_valB = 0x0
E_dstE = RNONE
E_dstM = RNONE
E_srcA = RNONE
E_srcB = RNONE

## Intermediate Values in Execute Stage
e_valE = 0x0
e_dstE = RNONE
e_Cnd = False
e_setcc = False

## Pipeline Register M
M_stat = SBUB
M_icode = INOP
M_ifun = FNONE
M_Cnd = False   # M_Bch
M_valE = 0x0
M_valA = 0x0
M_dstE = RNONE
M_dstM = RNONE

## Intermediate Values in Memory Stage
m_valM = 0x0
m_stat = SBUB
mem_addr = 0x0
m_read = False
dmem_error = False

## Pipeline Register W
W_stat = SBUB
W_icode = INOP
W_ifun = FNONE
W_valE = 0x0
W_valM = 0x0
W_dstE = RNONE
W_dstM = RNONE

# Registers initialization
registers = {
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

def init(fin):
    p = 0x000
    for line in fin:
        addr, code = get_addr(line), get_code(line)

def main():
    fin = open('asum.yo', 'r')
    init(fin)

main()
