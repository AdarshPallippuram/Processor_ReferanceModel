#--------------------------------------------------------
# Reg banks and uregs
#--------------------------------------------------------

reg_bank={
    "R":{"0000":"","0001":"","0010":"","0011":"","0100":"","0101":"","0110":"","0111":"","1000":"","1001":"","1010":"","1011":"","1100":"","1101":"","1110":"","1111":""},
    "I":{"0000":"","0001":"","0010":"","0011":"","0100":"","0101":"","0110":"","0111":"","1000":"","1001":"","1010":"","1011":"","1100":"","1101":"","1110":"","1111":""},
    "M":{"0000":"","0001":"","0010":"","0011":"","0100":"","0101":"","0110":"","0111":"","1000":"","1001":"","1010":"","1011":"","1100":"","1101":"","1110":"","1111":""},
    "0110":{"0000":"","0001":"","0011":"","0100":"","0101":""},
    "0111":{"1011":"","1100":"","1110":""}
}
reg={
    "0000":"R",
    "0001":"I",
    "0010":"M", 
    "0110":"0110",
    "0111":"0111"
}    
def put_to_reg(inst,val):
    reg_bank[reg[inst[0:4]]][inst[4:]]=val

def get_from_reg(inst):
    return reg_bank[reg[inst[0:4]]][inst[4:]]

def bit_wr(ureg,bit,val):                   # Bit writing function
    l = list(reg_bank['0111'][ureg])
    l[15-bit] = val
    reg_bank['0111'][ureg] = ''.join(l)

#--------------------------------------------------------
# ALU DESIGN
#--------------------------------------------------------

def twos_cmpl(n):
    N = int(n,2)^int('ffff',16)
    return '{:>16b}'.format(N+1)[-16:]

def b_to_d(b):
    if b[0] == '1':
        n = twos_cmpl(b)
        return -int(n,2)
    else:
        return int(b,2)

def d_to_b(d):
    N = abs(d)
    n = '{:>016b}'.format(N)
    if d < 0:
        return twos_cmpl(n)
    else:
        return n
        
def addcsubb(Rn_ad,Rx_ad,Ry_ad,is_sub,C):
    Rx = b_to_d(get_from_reg(Rx_ad))
    Ry = b_to_d(get_from_reg(Ry_ad))
    CI = int(get_from_reg('01111100')[12])
    if is_sub == '1':
        if C == '1':
            Rn = Rx - Ry + CI - 1
        else:
            Rn = Rx - Ry
    else:
        if C == '1':
            Rn = Rx + Ry + CI
        else:
            Rn = Rx + Ry
    Rn_b = d_to_b(Rn)
    zvnc = ['0','0','0','0']
    if Rn_b[0] == '1':                  # AN checking
        zvnc[2] = '1'
    if int(Rn_b,2) == 0:                # AZ checking
        zvnc[0] = '1'
    if Rn not in range(-32768,32768):   # AV checking
        zvnc[1] = '1'
    # Carry checking not done
    bit_wr('0111',0,zvnc[0])            # AZ updating
    bit_wr('0111',1,zvnc[1])            # AV updating
    bit_wr('0111',2,zvnc[2])            # AN updating
    bit_wr('0111',3,zvnc[3])            # AC updating
    put_to_reg(Rn_ad,Rn_b)              # Rn reg updating
    

def comp():
    

def ALU(operation,Rn,Rx,Ry):
    process = {
        '000000': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000001': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000010': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000011': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000101': comp(),
        '001001': ,
        '001011': ,
        '010001': ,
        '011001': ,
        '100000': ,
        '100001': ,
        '100010': ,
        '110000': ,
        '110001': ,
        '111000': 
    }
    if cond == 0:
        
    else:
        print('conditional')


#--------------------------------------------------------
# Primary division of opcode
#--------------------------------------------------------

import time
def prime_fun(oc):                  # oc - opcode
    
    cu = {                          # cu - compute unit
        '00':ALU(),
        '01':'MUL',
        '10':'SHIFTER'
    }

    if int(oc) == 0:
        # print('nop')
        time.sleep(3)

    elif int(oc[:9]) == 1:
        # print('idle')
        time.sleep(10)

    elif int(oc[:8]) == 1:
        print('rts')
        # put_to_reg('01100011',get_from_reg('01100100'))
        # deleting value in PCSTK not done

    elif int(oc[:8]) == 10:
        # print('PUSH PCSTK = <ureg>')
        put_to_reg('01100100',oc[8:16])

    elif int(oc[:8]) == 11:
        # print('<ureg> = POP PCSTK')
        put_to_reg(oc[8:16],get_from_reg('01100100'))
        # deleting value in PCSTK not done

    elif int(oc[:6]) == 11:
        #print('immediate data(16-bits) -> ureg')
        put_to_reg(oc[8:16],oc[16:])
        # print(oc[8:16],get_from_reg(oc[8:16]))

    elif int(oc[:6]) == 1:
        # print('IF condition ureg1 = ureg2')
        # ureg1 as 'dest' and ureg2 as 'source'
        put_to_reg(oc[8:16],get_from_reg(oc[16:23]))
    
    elif int(oc[:6]) == 1001:
        print('IF condition DM(Ia,Mb) <-> ureg')
    
    elif int(oc[:6]) == 1000:
        print('IF condition modify (Ia,Mb)')
    
    elif int(oc[:6]) == 1100:
        print('IF condition JUMP (Md,Ic)')
    
    elif int(oc[:6]) == 1101:
        print('IF condition JUMPR (Md,Ic)')

    elif int(oc[1]) == 1:
        # print('IF condition compute')
        cu[oc[6:8]]
        
    
prime_fun('00001100011001001010101010101010')