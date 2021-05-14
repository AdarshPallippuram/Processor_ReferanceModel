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

def twos_cmpl(n):                       # Function to obtain 2's compliment (binary str i/p)
    N = int(n,2)^int('ffff',16)
    return '{:>16b}'.format(N+1)[-16:]

def b_to_d(b):                          # Function converts binary(b) to decimal(d)
    if b[0] == '1':
        n = twos_cmpl(b)
        return -int(n,2)
    else:
        return int(b,2)

def d_to_b(d):                          # Function converts decimal(d) to binary(b)
    N = abs(d)
    n = '{:>016b}'.format(N)
    if d < 0:
        return twos_cmpl(n)
    else:
        return n

def is_AC(x,y,c,b):                     # Function checking for AC (ALU Carry)
	if x < 0:
		x = 65536 + x
	if y < 0:
		y = 65536 + y
	if b == -1:
		b = 65535
	if x + y + c + b > 65535:
		return '1'
	else:
		return '0'

def astat_alu_wr(zvnc):
    bit_wr('0111',0,zvnc[0])            # AZ updating
    bit_wr('0111',1,zvnc[1])            # AV updating
    bit_wr('0111',2,zvnc[2])            # AN updating
    bit_wr('0111',3,zvnc[3])            # AC updating
        
def addcsubb(Rn_ad,Rx_ad,Ry_ad,is_sub,C):   # add, add with carry, sub, sub with borrow function
    Rx = b_to_d(get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(get_from_reg('0000'+Ry_ad))
    CI = int(get_from_reg('01111100')[12])
    zvnc = ['0','0','0','0']
    if is_sub == '1':
        if C == '1':
            Rn = Rx - Ry + CI - 1
            zvnc[3] = is_AC(Rx,-Ry,CI,-1)   # AC checking
        else:
            Rn = Rx - Ry
            zvnc[3] = is_AC(Rx,-Ry,0,0)     # AC checking
    else:
        if C == '1':
            Rn = Rx + Ry + CI
            zvnc[3] = is_AC(Rx,Ry,CI,0)     # AC checking
        else:
            Rn = Rx + Ry
            zvnc[3] = is_AC(Rx,Ry,0,0)      # AC checking
    Rn_b = d_to_b(Rn)                    
    if Rn_b[0] == '1':                  # AN checking
        zvnc[2] = '1'
    if int(Rn_b,2) == 0:                # AZ checking
        zvnc[0] = '1'
    if Rn not in range(-32768,32768):   # AV checking
        zvnc[1] = '1'
        if int(reg_bank['0111']['1011']) == 1:
            if Rn < -32768:
                Rn_b = d_to_b(-32768)
            else:
                Rn_b = d_to_b(32767)
    astat_alu_wr(zvnc)
    put_to_reg('0000'+Rn_ad,Rn_b)              # Rn reg updating
    

def comp(Rx_ad,Ry_ad):
    Rx = b_to_d(get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(get_from_reg('0000'+Ry_ad))
    zvnc = ['0','0','0','0']
    com = '0' 
    if Rx == Ry:
        zvnc[0] = '1'
    elif Rx < Ry:
        zvnc[2] = '1'
    else:
        com = '1'
    astat_alu_wr(zvnc)
    s = reg_bank['0111']['1100']
    sn = com + s[(15-15):(15-8)] + s[(15-7):]
    reg_bank['0111']['1100'] = sn       # ASTAT comp updating

def minmax(Rn_ad,Rx_ad,Ry_ad,m):
    Rx = b_to_d(get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(get_from_reg('0000'+Ry_ad))
    zvnc = ['0','0','0','0']
    if m == '1':
        Rn = max(Rx,Ry)
    else:
        Rn = min(Rx,Ry)
    put_to_reg('0000'+Rn_ad,d_to_b(Rn))
    if Rn == 0:
        zvnc[0] = '1'
    if Rn < 0:
        zvnc[2] = '1'
    astat_alu_wr(zvnc)

def negate(Rn_ad,Rx_ad):
    Rx = b_to_d(get_from_reg('0000'+Rx_ad))
    zvnc = ['0','0','0','0']
    Rn = -Rx
    if Rn == 0:
        zvnc[0] = '1'
        zvnc[3] = '1'
    if Rn < 0:
        zvnc[2] = '1'
    if Rn == 32768:
        zvnc[1] = '1'
        zvnc[2] = '1'
        if int(reg_bank['0111']['1011']) == 1:
            Rn = 32767
            zvnc[2] = '0'
    put_to_reg('0000'+Rn_ad,d_to_b(Rn))
    astat_alu_wr(zvnc)

def absolute(Rn_ad,Rx_ad):
    Rx = b_to_d(get_from_reg('0000'+Rx_ad))
    if Rx < 0:
        negate(Rn_ad,Rx_ad)
    else:
        put_to_reg('0000'+Rn_ad,d_to_b(Rx))
        if Rx == 0:
            zvnc = ['1','0','0','0']
        else:
            zvnc = ['0','0','0','0']
        astat_alu_wr(zvnc)

def logical(Rn_ad,Rx_ad,Ry_ad,op):
    Rxb = get_from_reg('0000'+Rx_ad)
    Rx = b_to_d(Rxb)
    Rn = 0
    if op[1] == '0':
        Ry = b_to_d(get_from_reg('0000'+Ry_ad))
        if op[4:] == '00':
            Rn = Rx & Ry
        elif op[4:] == '01':
            Rn = Rx | Ry
        else:
            Rn = Rx ^ Ry
    else:
        if op[2] == '1':
            Rn = Rx ^ (-1)
        elif op[4:] == '00':
            if '0' not in Rxb:
                Rn = 1
        else:
            if '1' in Rxb:
                Rn = 1
    put_to_reg('0000'+Rn_ad,d_to_b(Rn))   
    zvnc = ['0','0','0','0']
    if Rn == 0:
        zvnc[0] = '1'
    if d_to_b(Rn)[0] == '1':
        zvnc[2] = '1'
    astat_alu_wr(zvnc) 

def ALU(operation,Rn,Rx,Ry):
    process = {
        '000000': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000001': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000010': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000011': addcsubb(Rn,Rx,Ry,operation[-1],operation[-2]),
        '000101': comp(Rx,Ry),
        '001001': minmax(Rn,Rx,Ry,operation[-2]),
        '001011': minmax(Rn,Rx,Ry,operation[-2]),
        '010001': negate(Rn,Rx),
        '011001': absolute(Rn,Rx),
        '100000': logical(Rn,Rx,Ry,operation),
        '100001': logical(Rn,Rx,Ry,operation),
        '100010': logical(Rn,Rx,Ry,operation),
        '110000': logical(Rn,Rx,Ry,operation),
        '110001': logical(Rn,Rx,Ry,operation),
        '111000': logical(Rn,Rx,Ry,operation)
    }
    process[operation]

#--------------------------------------------------------
# Primary division of opcode
#--------------------------------------------------------

import time
def prime_fun(oc):                  # oc - opcode
    
    cu = {                          # cu - compute unit
        '00':ALU(oc[(31-22):(31-16)], oc[(31-16):(31-12)], oc[(31-12):(31-8)], oc[(31-8):(31-4)]),
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
        # print('rts')
        put_to_reg('01100011',get_from_reg('01100100'))
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