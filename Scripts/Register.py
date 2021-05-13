reg_bank={
    "R":{"0000":"0000000010000010","0001":"0111000010101010","0010":"XXXX","0011":"1111111011111101","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "I":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "M":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "0110":{"0000":"XXXX","0001":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX"},
    "0111":{"1011":"XXXX","1100":"XXXX","1110":"XXXX"}
}
reg={
    "0000":"R",
    "0001":"I",
    "0010":"M",
    "0110":"0110",
    "0111":"0111"
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
def put_to_reg(inst,val):
    reg_bank[reg[inst[0:4]]][inst[4:]]=val
    #reg_bank.get(reg.get(inst[0:4]))[dec(inst[4:])]=val

def get_from_reg(inst):
    return reg_bank[reg[inst[0:4]]][inst[4:]]
    #return(reg_bank.get(reg.get(inst[0:4]))[dec(inst[4:])])

#print(compliment("1111000010101010"))