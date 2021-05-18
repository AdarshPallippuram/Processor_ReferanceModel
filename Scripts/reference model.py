import time

#---------------------------------------------------------------------------
# Reg banks, uregs and related dictionaries and functions
#---------------------------------------------------------------------------

reg_bank={
    "R":{"0000":"0000000000000010","0001":"0111000010101010","0010":"0000000000010000","0011":"1111111011111101","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "I":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "M":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "0110":{"0000":"XXXX","0001":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX"},
    "0111":{"1011":"XXXX","1100":"0000000000000000","1110":"XXXX"}
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
    "STKY":"01111110"}
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
def get_from_reg(inst):
    return reg_bank[reg[inst[0:4]]][inst[4:]]

#---------------------------------------------------------------------------
# ALU
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Multiplier
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
# Shifter
#---------------------------------------------------------------------------

def shifter(inst):
    R=["0000"+inst[6:10],"0000"+inst[10:14]]
    sz="0"
    sv="0"
    if(inst[1]=="0"):
        R.append("0000"+inst[14:])
    R_val=[]
    i=1
    while(i<len(R)):
        R_val.append(get_from_reg(R[i]))
        i+=1
    if(inst[1:3]=="00"):
        if(R_val[1][0]=="1"):
            shift=compliment(R_val[1])
            R_val[0]=format(int(R_val[0],2)//(2**shift),"016b")
        else:
            shift=int(R_val[1][1:],2)
            R_val[0]=format(int(R_val[0],2)*(2**(shift+1)),"016b")
            R_val[0]=R_val[0][-17:-1]
            if(shift>0):
                sv="1"
        put_to_reg(R[0],R_val[0])
        if(int(R_val[0],2)==0):
            sz="1"
    elif(inst[1:3]=="01"):
        if(R_val[1][0]=="1"):
            shift=compliment(R_val[1])%16
            put_to_reg(R[0],R_val[0][shift:]+R_val[0][0:shift])
        else:
            shift=int(R_val[1][1:],2)%16
            put_to_reg(R[0],R_val[0][16-shift:]+R_val[0][0:16-shift])
        if(int(R_val[0],2)==0):
            sz="1"
    elif(inst[1:3]=="10"):
        val=format(len(R_val[0].split("1")[0]),"016b")
        put_to_reg(R[0],val)
        if(R_val[0][0]=="1"):
            sz="1"
        if(int(val,2)==16):
            sv="1"
    elif(inst[1:3]=="11"):
        val=format(len(R_val[0].split("0")[0]),"016b")
        put_to_reg(R[0],val)
        if(R_val[0][0]=="0"):
            sz="1"
        if(int(val,2)==16):
            sv="1"
    flag=get_from_reg("01111100")
    put_to_reg("01111100",flag[:8]+sz+sv+flag[10:])

#---------------------------------------------------------------------------
# Primarry Classification
#---------------------------------------------------------------------------

def primary(OpCode):
    if int(OpCode) == 0:
        # print('nop')
        time.sleep(3)
    elif int(OpCode[:9]) == 1:
        # print('idle')
        time.sleep(10)
    elif int(OpCode[:8]) == 1:
        #print('rts')
        # put_to_reg('01100011',get_from_reg('01100100'))
        # deleting value in PCSTK not done
        put_to_reg('01100100',"XXXX")
    elif int(OpCode[:8]) == 10:
        # print('PUSH PCSTK = <ureg>')
        put_to_reg('01100100',OpCode[8:16])
    elif int(OpCode[:8]) == 11:
        # print('<ureg> = POP PCSTK')
        put_to_reg(OpCode[8:16],get_from_reg('01100100'))
        # deleting value in PCSTK not done
        put_to_reg('01100100',"XXXX")
    elif int(OpCode[:6]) == 11:
        #print('immediate data(16-bits) -> ureg')
        put_to_reg(OpCode[8:16],OpCode[16:])
        # print(OpCode[8:16],get_from_reg(OpCode[8:16]))
    elif int(OpCode[1:6]) == 1:
        # print('IF condition ureg1 = ureg2')
        # ureg1 as 'dest' and ureg2 as 'source'
        put_to_reg(OpCode[8:16],get_from_reg(OpCode[16:23]))
    elif int(OpCode[1:6]) == 1001:
        print('IF condition DM(Ia,Mb) <-> ureg')
    elif int(OpCode[1:6]) == 1000:
        print('IF condition modify (Ia,Mb)')
        put_to_reg("00010"+OpCode[19:22],get_from_reg("00100"+OpCode[22:25]))
    elif int(OpCode[1:6]) == 1100:
        print('IF condition JUMP (Md,Ic)')
    elif int(OpCode[1:6]) == 1101:
        print('IF condition JUMPR (Md,Ic)')
    elif int(OpCode[1]) == 1:
        # print('IF condition compute')
        if(OpCode[6:8]=="00"):
            print("ALU")
        elif(OpCode[6:8]=="01"):
            print("Multiplier")
        else:
            shifter(OpCode[9:27])

#---------------------------------------------------------------------------
# Main Function
#---------------------------------------------------------------------------

b=input("Enter name of OpCode file:")
f=open(b,"rt")
z=input("Enter name of register dump file:")
g=open(z,"wt")
start=time.time()
l=[]
for i in f:
    l.append(i.strip("\n"))
i=0
while(i<len(l)):
    #ADD Conditions
    primary(l[i])
    i=i+1
for i in range(3):
    a=format(i,"04b")
    for j in range(16):
        b=format(j,"04b")
        value=reg_bank[reg[a]][b]
        if(value!="XXXX"):
            value=ubin_to_hex(value)
        g.write("{}{} : {}".format(reg[a],j,value))
        g.write("\n")
for i in reg_name.keys():
    value=reg_bank[reg_name[i][0:4]][reg_name[i][4:]]
    if(value!="XXXX"):
        value=ubin_to_hex(value)
    g.write("{} : {}".format(i,value))
    g.write("\n")
print("Register values stored in {}.txt".format(z))
end=time.time()
print("Time taken to complete program = %s"%(end-start))
