
reg_bank={
    "R":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "I":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "M":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "0110":{"0000":"XXXX","0001":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX"},
    "0111":{"1011":"0000000000000000","1100":"0000000000000000","1110":"0000000000000000"}
}
reg={
    "0000":"R",
    "0001":"I",
    "0010":"M", 
    "0110":"0110",
    "0111":"0111"
}    
reg_name={
    "FADDR":"01100000",
    "DADDR":"01100001",
    "PC":"01100011",
    "PCSTK":"01100100",
    "PCSTKP":"01100101",
    "MODE1":"01111011",
    "ASTAT":"01111100",
    "STKY":"01111110"
    }

def hex_to_ubin(hnum):
    bnum = format(int(hnum,16),'016b')
    return bnum

def ubin_to_hex(bnum):
    hnum=format(int(bnum,2),'04X')
    return hnum

def int_to_hex(num):
    hnum=format(num,"04X")
    return hnum

def compliment(num):
    s=-2**15
    for i in range(15):
        s=s+(int(num[15-i])*2**i)
    return(-s)

def compliment40(num):
    s=-2**39
    for i in range(39):
        s=s+(int(num[39-i])*2**i)
    return(-s)

def put_to_reg(inst,val):
    reg_bank[reg[inst[0:4]]][inst[4:]]=val

def get_from_reg(inst):
    return reg_bank[reg[inst[0:4]]][inst[4:]]

def bit_wr(ureg,bit,val):                   # Bit writing function
    l = list(reg_bank['0111'][ureg])
    l[15-bit] = val
    reg_bank['0111'][ureg] = ''.join(l)