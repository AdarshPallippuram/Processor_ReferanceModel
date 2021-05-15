import Register

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

#--------------------------------------------------------

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
    Register.bit_wr('1100',0,zvnc[0])            # AZ updating
    Register.bit_wr('1100',1,zvnc[1])            # AV updating
    Register.bit_wr('1100',2,zvnc[2])            # AN updating
    Register.bit_wr('1100',3,zvnc[3])            # AC updating

#--------------------------------------------------------     
   
def addcsubb(Rn_ad,Rx_ad,Ry_ad,is_sub,C):   # add, add with carry, sub, sub with borrow function
    Rx = b_to_d(Register.get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(Register.get_from_reg('0000'+Ry_ad))
    CI = int(Register.get_from_reg('01111100')[12])
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
        if int(Register.reg_bank['0111']['1011']) == 1:
            if Rn < -32768:
                Rn_b = d_to_b(-32768)
            else:
                Rn_b = d_to_b(32767)
    astat_alu_wr(zvnc)
    Register.put_to_reg('0000'+Rn_ad,Rn_b)              # Rn reg updating

#--------------------------------------------------------    

def comp(Rx_ad,Ry_ad):
    Rx = b_to_d(Register.get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(Register.get_from_reg('0000'+Ry_ad))
    zvnc = ['0','0','0','0']
    com = '0' 
    if Rx == Ry:
        zvnc[0] = '1'
    elif Rx < Ry:
        zvnc[2] = '1'
    else:
        com = '1'
    astat_alu_wr(zvnc)
    s = Register.reg_bank['0111']['1100']
    sn = com + s[(15-15):(15-8)] + s[(15-7):]
    Register.reg_bank['0111']['1100'] = sn       # ASTAT comp updating

#--------------------------------------------------------

def minmax(Rn_ad,Rx_ad,Ry_ad,m):
    Rx = b_to_d(Register.get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(Register.get_from_reg('0000'+Ry_ad))
    zvnc = ['0','0','0','0']
    if m == '1':
        Rn = max(Rx,Ry)
    else:
        Rn = min(Rx,Ry)
    Register.put_to_reg('0000'+Rn_ad,d_to_b(Rn))
    if Rn == 0:
        zvnc[0] = '1'
    if Rn < 0:
        zvnc[2] = '1'
    astat_alu_wr(zvnc)

#--------------------------------------------------------

def negate(Rn_ad,Rx_ad):
    Rx = b_to_d(Register.get_from_reg('0000'+Rx_ad))
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
        if int(Register.reg_bank['0111']['1011']) == 1:
            Rn = 32767
            zvnc[2] = '0'
    Register.put_to_reg('0000'+Rn_ad,d_to_b(Rn))
    astat_alu_wr(zvnc)

#--------------------------------------------------------

def absolute(Rn_ad,Rx_ad):
    Rx = b_to_d(Register.get_from_reg('0000'+Rx_ad))
    if Rx < 0:
        negate(Rn_ad,Rx_ad)
    else:
        Register.put_to_reg('0000'+Rn_ad,d_to_b(Rx))
        if Rx == 0:
            zvnc = ['1','0','0','0']
        else:
            zvnc = ['0','0','0','0']
        astat_alu_wr(zvnc)

#--------------------------------------------------------

def logical(Rn_ad,Rx_ad,Ry_ad,op):
    Rxb = Register.get_from_reg('0000'+Rx_ad)
    Rx = b_to_d(Rxb)
    Rn = 0
    if op[1] == '0':
        Ry = b_to_d(Register.get_from_reg('0000'+Ry_ad))
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
    Register.put_to_reg('0000'+Rn_ad,d_to_b(Rn))   
    zvnc = ['0','0','0','0']
    if Rn == 0:
        zvnc[0] = '1'
    if d_to_b(Rn)[0] == '1':
        zvnc[2] = '1'
    astat_alu_wr(zvnc) 

#--------------------------------------------------------

def ALU(operation,Rn,Rx,Ry):
    prOpCodeess = {
        '000000': 0,
        '000001': 0,
        '000010': 0,
        '000011': 0,
        '000101': 1,
        '001001': 2,
        '001011': 2,
        '010001': 3,
        '011001': 4,
        '100000': 5,
        '100001': 5,
        '100010': 5,
        '110000': 5,
        '110001': 5,
        '111000': 5
    }

    if prOpCodeess[operation] == 0:
        return addcsubb(Rn,Rx,Ry,operation[-1],operation[-2])
    elif prOpCodeess[operation] == 1:
        return comp(Rx,Ry)
    elif prOpCodeess[operation] == 2:
        return minmax(Rn,Rx,Ry,operation[-2])
    elif prOpCodeess[operation] == 3:
        return negate(Rn,Rx)
    elif prOpCodeess[operation] == 4:
        return absolute(Rn,Rx)
    elif prOpCodeess[operation] == 5:
        return logical(Rn,Rx,Ry,operation)