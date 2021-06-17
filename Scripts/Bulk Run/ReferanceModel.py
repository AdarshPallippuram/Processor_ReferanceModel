# The file opening logic has been written keeping into consideration that the test files have the format
# - a1 - left shift                     //This is the parent folder
#   - a_p1.txt                          //Holds the instructions
#   - a1.txt                            //Holds the data memory output
# The path is defined such that no change needs to be made there. The tesing files should be put in their own folders
# inside a "Test" folder, i.e a1 - left shift is inside a folder "Test" in the script directory
import os
path="SAC/"
#---------------------------------------------------------------------------
# Reg banks, uregs and related dictionaries and functions
#---------------------------------------------------------------------------

reg_bank={}
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
def put_to_reg(addr,val):
    if(addr=="01111011"):
        val=15*"0"+val[-1]
    reg_bank[reg[addr[0:4]]][addr[4:]]=val
def get_from_reg(addr):
    return reg_bank[reg[addr[0:4]]][addr[4:]]

#---------------------------------------------------------------------------
# Miscellaneous Functions
#---------------------------------------------------------------------------

def hex_to_ubin(hnum):
    return format(int(hnum,16),'0'+str(len(hnum)*4)+'b')
def ubin_to_hex(bnum):
    return format(int(bnum,2),'0'+str(len(bnum)//4)+'X')
def int_to_hex(num):
    return format(num,"04X")
def compliment(num):
    return format((int(num,2)^int(len(num)*"1",2))+1,"0"+str(len(num))+"b")[-len(num):]
def b_to_d(b):                          # Function converts binary(b) to decimal(d)
    if b[0] == '1':
        return -int(compliment(b),2)
    else:
        return int(b,2)
def d_to_b(d):                          # Function converts decimal(d) to binary(b)
    n = '{:>016b}'.format(abs(d))[-16:]
    if d < 0:
        return compliment(n)
    else:
        return n
def bit_wr(ureg,bit,val):                   # Bit writing function
    l = list(reg_bank['0111'][ureg])
    l[15-bit] = val
    reg_bank['0111'][ureg] = ''.join(l)
def fbin_to_decimal(num,s1): # ARgumnets are the binary number as string and the signed/!unsigned bit of the operand
    s1=int(s1)
    a=0
    if(len(num)>16):
        a=num[:8]
        num=num[8:]
    if(s1==1 and a=="11111111" and num[0]=="0"):
        val=-1
    elif(s1==1 and a=="00000000" and num[0]=="1"):
        val=1
    else:
        val=int(num[0])*(-s1)
    n=len(num)
    for i in range(s1,n):
        val=val+int(num[i])*2**(-i-1+s1)
    if(s1==1 and a=="11111111" and num[0]=="0"):
        val=-1+val
    elif(s1==1 and a=="00000000" and num[0]=="1"):
        val=1+val
    return(val)
def decimal_to_fbin(num,s1):
    s1=int(s1)
    if(num>=0):
        val="00000000"+s1*"0"
    else:
        val="11111111"+s1*"1"
        num=num+1
    while(len(val)<40):
        num=num*2
        if(num>=1):
            num=num-1
            val=val+"1"
        else:
            val=val+"0"
    return(val)

#---------------------------------------------------------------------------
# ALU
#---------------------------------------------------------------------------

def is_AC(x,y,c,b):                     # Function checking for AC (ALU Carry)
	if x < 0:
		x = 65536 + x
	if y < 0:
		y = 65536 + y
	# if b == -1:
		# b = 65535
	if x + y + c + b > 65535:
		return '1'
	else:
		return '0'

def astat_alu_wr(zvnc):
    bit_wr('1100',0,zvnc[0])            # AZ updating
    bit_wr('1100',1,zvnc[1])            # AV updating
    bit_wr('1100',2,zvnc[2])            # AN updating
    bit_wr('1100',3,zvnc[3])            # AC updating

#--------------------------------------------------------     
   
def addcsubb(Rn_ad,Rx_ad,Ry_ad,is_sub,C):   # add, add with carry, sub, sub with borrow function
    Rx = b_to_d(get_from_reg('0000'+Rx_ad))
    Ry = b_to_d(get_from_reg('0000'+Ry_ad))
    CI = int(get_from_reg('01111100')[12])
    zvnc = ['0','0','0','0']
    if is_sub == '1':
        if Ry == -32768:
            Ry = 32768
        if C == '1':
            if (Rx == -32768) and (Ry == 32768):
                Rn = 0 + CI - 1
            else:  
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
    if Rn not in range(-32768,32768):   # AV checking
        zvnc[1] = '1'
        if int(reg_bank['0111']['1011']) == 1:  # Checking for ALU sat bit
            if Rn < -32768:
                Rn_b = d_to_b(-32768)
            else:
                Rn_b = d_to_b(32767)
    if Rn_b[0] == '1':                  # AN checking
        zvnc[2] = '1'
    if int(Rn_b,2) == 0:                # AZ checking
        zvnc[0] = '1'
    astat_alu_wr(zvnc)
    put_to_reg('0000'+Rn_ad,Rn_b)              # Rn reg updating

#--------------------------------------------------------    

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

#--------------------------------------------------------

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

#--------------------------------------------------------

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

#--------------------------------------------------------

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

#--------------------------------------------------------

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
#---------------------------------------------------------------------------
# Multiplier
#---------------------------------------------------------------------------
def fmul(num1,num2,x=0,y=0):
    num1=fbin_to_decimal(num1,y)
    num2=fbin_to_decimal(num2,x)
    product=num1*num2
    return product
def signed_mul(num1,num2,x,y):
    comp1=0
    comp2 =0
    if(x=='1' and num1[0]=="1"):
        num1 = int(compliment(num1),2)
        comp1 = 1
    else:
        num1= int(num1,2)
    if(y=='1' and num2[0]=="1"):
        num2 = int(compliment(num2),2)
        comp2 = 1
    else:
        num2 = int(num2,2)
    product = format(num1*num2,'040b')
    if(comp1^comp2):
        product = int(compliment(product),2)
        product = format(product,'040b')
        x=len(product.split('1')[0])
        product = '1'*x + product[x:]
    return product
def unsigned_mul(num1,num2):
    n1 = int(num1,2)
    n2 = int(num2,2)
    product = format(n1*n2,'040b')
    return product
mrf="0000000000000000000000000000000000000000"
u_or_s=0
def multi(op):
    global mrf
    global u_or_s
    mrf1="0000000000000000000000000000000000000000"
    mr2=mrf[0:8]
    mr1 = mrf[8:24]
    mr0 = mrf[24:40]
    Rn = "0000"+ op[7:11]
    Rx = "0000"+op[11:15]
    Ry = "0000"+ op[15:19]
    rx= get_from_reg(Rx)
    ry= get_from_reg(Ry)
    mv="0"
    mn="0"
    if(op[0:2]=="00"):
        rn=get_from_reg(Rn)
        mn="0"
        mv="0"
        if(op[2]=="0" and op[17:]!="11"):
            if(op[17:]=="00"): #rn = mr0
                rn = mr0
            elif(op[17:]=="01"): #rn = mr1
                rn = mr1
            elif(op[17:]=="10"): #rn = mr2
                rn = 8*mr2[0]+mr2
        elif(op[2]=="1" and op[17:]!="11"):
            mr0=16*"0"
            mr1=16*"0"
            mr2=8*"0"
            if(op[17:]=="00"):
                mr0 =get_from_reg(Rx)
            elif(op[17:]=="01"):
                mr1 = get_from_reg(Rx)
                mr2=8*mr1[0]
            elif(op[17:]=="10"):
                mr2 =get_from_reg(Rx)[8:]
            mrf1=(mr2+mr1+mr0)
        elif(op[17:]=="11"):
            if(op[4:6]=="01" and "1" in mrf[0:8]):      #unsigned fractional
                mrf1=hex_to_ubin("00ffffffff")
                if(op[2]=="0"):
                    rn=mrf1[8:24]
            elif(op[4:6]=="00"and "1" in mrf[0:24]):    #unsigned integer
                mrf1=hex_to_ubin("000000ffff")
                if(op[2]=="0"):
                    rn=mrf1[-16:]
            elif(op[4:6]=="11" and "1" in mrf[0:9] and "0" in mrf[0:9]): 
                if(mrf[0]=="0"):
                    mrf1 = hex_to_ubin("007fffffff")
                else:
                    mrf1 = hex_to_ubin("ff80000000")
                if(op[2]=="0"):
                    rn=mrf1[8:24]
            elif(op[4:6]=="10" and "1" in mrf[0:25] and "0" in mrf[0:25]): 
                if(mrf[0]=="0"):
                    mrf1 = hex_to_ubin("0000007fff")
                else:
                    mrf1 = hex_to_ubin("ffffff8000")
                if(op[2]=="0"):
                    rn=mrf1[-16:]
            elif(op[2]=="0"):
                if(op[5]=="0"):
                    mrf1=mrf
                    rn=mrf[-16:]
                else:
                    mrf1=mrf
                    rn=mrf[8:24]
            if((int(op[3])|int(op[4]))==1 and mrf1[0]=="1"):
                mn="1"
    else:
        if(op[5]=="1"): #signed fractional multiplication with both numbers signed
            mrf1=decimal_to_fbin(fmul(rx,ry,op[3],op[4]),int(op[3])|int(op[4]))
        elif(op[3:5]=="00"): #unsigned multiplicatiopn
            mrf1=unsigned_mul(rx,ry)
        else:                               #signed multiplication
            mrf1=signed_mul(rx,ry,op[4],op[3])
        if(op[5]=="1" and op[6]=="1"):
            if(mrf1[-16]=="0"):
                mrf1=mrf1[-40:-16]+16*"0"
            else:
                if("1" not in mrf1[-15:]):
                    mrf1=mrf1[-40:-16]
                    if(mrf[-1]=="0"):
                        mrf1=mrf1+16*"0"
                    else:
                        n=len(mrf1.split("0")[-1])
                        mrf1=mrf1[-24:-1-n]+"1"+n*"0"+16*"0"
                else:
                    mrf1=mrf1[-40:-16]
                    mrf1=format(int(mrf1,2)+1,"024b")+16*"0"
        if(op[0:2]=="10"):   # mr+rx*ry
            val=0
            if(op[5]=="1"):
                mrf1=fbin_to_decimal(mrf,int(op[3])|int(op[4]))+fbin_to_decimal(mrf1,int(op[3])|int(op[4]))
                if(mrf1<(-1)):
                    if(int(op[3])|int(op[4])==1):
                        val=int("ff80000000",16)
                    mrf1=mrf1+1
                if(mrf1>1):
                    if(int(op[3])|int(op[4])==1):
                        val=int("007fffffff",16)
                    mrf1=mrf1-1
                mrf1=format(val+int(decimal_to_fbin(mrf1,int(op[3])|int(op[4])),2),"040b")[-40:]
                if((mrf[:8]!=mrf1[:8]) and (u_or_s == 1) and (int(op[3])|int(op[4])==0)):
                    mrf1=mrf[:8]+mrf1[8:]
            elif(op[3:5]=="00"): 
                mrf1 = int(mrf,2)+int(mrf1,2)
                mrf1 = format(mrf1,'040b')
            else: #signed multiplication
                mrf1 = int(mrf,2)+int(mrf1,2)
                mrf1 = format(mrf1,'040b')
        elif(op[0:2]=="11"):                   #rn = mr-rx*ry
            val=0
            if(op[5]=="1"):
                mrf1= fbin_to_decimal(mrf,int(op[3])|int(op[4]))-fbin_to_decimal(mrf1,int(op[3])|int(op[4]))
                if(mrf1<(-1)):
                    if(int(op[3])|int(op[4])==1):
                        val=int("ff80000000",16)
                    mrf1=mrf1+1
                if(mrf1>1):
                    if(int(op[3])|int(op[4])==1):
                        val=int("007fffffff",16)
                    mrf1=mrf1-1
                mrf1=format(val+int(decimal_to_fbin(mrf1,int(op[3])|int(op[4])),2),"040b")[-40:]
                if((mrf[:8]!=mrf1[:8]) and (u_or_s == 1) and (int(op[3])|int(op[4])==0)):
                    mrf1=mrf[:8]+mrf1[8:]
            elif(op[3:5]=="00"):
                mrf1 = int(mrf,2)-int(mrf1,2)
                mrf1 = format(mrf1,'040b')
            else: #signed multiplication
                mrf1 = int(mrf,2)-int(mrf1,2)
                mrf1 = format(mrf1,'040b')
            if(mrf1[0]=="-"):
                mrf1=compliment(mrf1)
        u_or_s=int(op[3])|int(op[4])
        if(int(op[3])|int(op[4])==1):
            if(mrf1[0:8]=="11111111"):
                mn="1"
        if(op[5]=="1"):
            if(int(op[3])|int(op[4])==1):
                if(("1" in mrf1[0:17]) and ("0" in mrf1[0:17])):
                    mv="1"
            else:
                if(("1" in mrf1[0:16]) and ("0" in mrf1[0:16])):
                    mv="1"
        else:
            if(int(op[3])|int(op[4])==1):
                if(("1" in mrf1[0:25]) and ("0" in mrf1[0:25])):
                    mv="1"
            else:
                if(("1" in mrf1[0:24]) and ("0" in mrf1[0:24])):
                    mv="1"
        if(op[5]=="1"):
            rn=mrf1[8:24]
        else:
            rn=mrf1[24:]
    if(op[2]=="0"):
        put_to_reg(Rn,rn)
    else:
        mrf=mrf1[-40:]
    flag=get_from_reg("01111100")
    put_to_reg("01111100",flag[0:10]+mv+mn+flag[12:])

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
        temp=R_val[0]
        if(R_val[1][0]=="1"):
            shift=int(compliment(R_val[1]),2)
            R_val[0]=R_val[0][0]*shift+R_val[0]
            R_val[0]=R_val[0][0:16]
        else:
            shift=int(R_val[1][1:],2)
            R_val[0]=format(int(R_val[0],2)*(2**(shift)),"016b")
            R_val[0]=R_val[0][-16:]
        put_to_reg(R[0],R_val[0])
        if(temp[0]!=R_val[0][0]):
            sv="1"
        if(int(R_val[0],2)==0):
            sz="1"
    elif(inst[1:3]=="01"):
        if(R_val[1][0]=="1"):
            shift=int(compliment(R_val[1]),2)%16
            put_to_reg(R[0],R_val[0][16-shift:]+R_val[0][0:16-shift])
            
        else:
            shift=int(R_val[1][1:],2)%16
            put_to_reg(R[0],R_val[0][shift:]+R_val[0][0:shift])
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
# Primary Classification
#---------------------------------------------------------------------------

def primary(OpCode):
    if int(OpCode[:8]) == 10:                                                                   #PUSH PCSTK = <ureg>
        if(int(get_from_reg("01111110"))==1):
            put_to_reg('01100100',get_from_reg(OpCode[8:16]))
            put_to_reg("01111110",format(2,"016b"))
            put_to_reg("01100101",format(1,"016b"))     #PCSTKP
        else:
            put_to_reg("01100101","000001001")           #PCSTKP
            put_to_reg("01111110",format(4,"016b"))
    elif int(OpCode[:8]) == 11:                                                                 #<ureg> = POP PCSTK
        put_to_reg(OpCode[8:16],get_from_reg('01100100'))
        put_to_reg("01111110",format(1,"016b"))
        put_to_reg("01100101",format(0,"016b"))     #PCSTKP
    elif int(OpCode[:6]) == 11:                                                                 #ureg = immediate data(16-bits)
        if(OpCode[8:16]=="01100100"):                                                           #PCSTK = immediate data(16-bits)
            if(int(get_from_reg("01111110"))==1):
                put_to_reg('01100100',OpCode[16:])
                put_to_reg("01111110",format(2,"016b"))
                put_to_reg("01100101",format(1,"016b"))     #PCSTKP
            else:
                put_to_reg("01100101","000001001")           #PCSTKP
                put_to_reg("01111110",format(4,"016b"))
        else:                                                                                   #ureg(other than PCSTK) = immediate data(16-bits)
            put_to_reg(OpCode[8:16],OpCode[16:])
    elif int(OpCode[1]) == 1:                                                                   #IF condition compute
        if(OpCode[6:8]=="00"):
            ALU(OpCode[(31-22):(31-16)], OpCode[(31-16):(31-12)], OpCode[(31-12):(31-8)], OpCode[(31-8):(31-4)])
        elif(OpCode[6:8]=="01"):
            multi(OpCode[8:27])
        else:
            shifter(OpCode[9:27])
    elif int(OpCode[2:6]) == 1:                                                                 #IF condition ureg1 = ureg2
        if(OpCode[8:16]=="01100100"):                                                           #PCSTK = ureg
            if(int(get_from_reg("01111110"))==1):
                put_to_reg('01100100',get_from_reg(OpCode[16:24]))
                put_to_reg("01111110",format(2,"016b"))
                put_to_reg("01100101",format(1,"016b"))     #PCSTKP
            else:
                put_to_reg("01100101","000001001")           #PCSTKP
                put_to_reg("01111110",format(4,"016b"))
        else:                                                                                   #ureg1(other than PCSTK) = ureg2
            put_to_reg(OpCode[8:16],get_from_reg(OpCode[16:24]))
    elif int(OpCode[2:6]) == 1001:                                                              #IF condition DM(Ia,Mb) <-> ureg
        i_data=get_from_reg("00010"+OpCode[19:22])
        if(i_data!="XXXX"):
            i_data=format(int(i_data,2),"04x")
        m_data=get_from_reg("00100"+OpCode[22:25])
        h=open(path+"/dm_file.txt","rt")
        if(OpCode[25]=="1"):                                                                    #DM(Ia,Mb) = ureg
            ureg_data=get_from_reg(OpCode[8:16])
            if(ureg_data!="XXXX" and i_data!="XXXX"):
                ureg_data=format(int(ureg_data,2),"04x")
                i=open(path+"/dm_file2.txt","wt")
                for j in h:
                    if (i_data in j[:4]):
                        j=i_data+"\t"+ureg_data+"\n"
                    i.write(j)
                h.close()
                i.close()
                os.remove(path+"/dm_file.txt")
                os.rename(path+"/dm_file2.txt",path+"/dm_file.txt")
            if(not h.closed):
                h.close()
        else:                                                                                   #urg = DM(Ia,Mb)
            for j in h:
                if(i_data.upper() in j[0:4].upper()):
                    ureg_data=j.split("\t")[-1].strip("\n")
            if(ureg_data!="xxxx"):
                put_to_reg(OpCode[8:16],format(int(ureg_data,16),"016b"))
            else:
                put_to_reg(OpCode[8:16],"XXXX")
            h.close()
        if(m_data!="XXXX" and i_data!="XXXX"):
            i_data=int(i_data,16)+int(m_data,2)
            if(i_data>65536):
                i_data=i_data-65536
            i_data=format(i_data,"016b")
        else:
            i_data="XXXX"
        put_to_reg("00010"+OpCode[19:22],i_data)
    elif int(OpCode[1:6]) == 1000:                                                              #IF condition modify (Ia,Mb)
        i_data=get_from_reg("00010"+OpCode[19:22])
        m_data=get_from_reg("00100"+OpCode[22:25])
        if(m_data!="XXXX"):
            i_data=int(i_data,2)+int(m_data,2)
            if(i_data>65536):
                i_data=i_data-65536
        else:
            i_data="XXXX"
        i_data=format(i_data,"016b")
        put_to_reg("00010"+OpCode[19:22],i_data)

#---------------------------------------------------------------------------
# Condition
#---------------------------------------------------------------------------

def condition(a):
    ASTAT=get_from_reg("01111100")
    if(a[2:]=="111"):
        val=1
    elif(a[1:]=="0000"):
        val=int(a[0])^int(ASTAT[-1])
    elif(a[1:]=="0001"):
        val=int(a[0])^int(ASTAT[13])
    elif(a[1:]=="0010"):
        val=int(a[0])^(int(ASTAT[13])|int(ASTAT[-1]))
    elif(a[1:]=="0011"):
        val=int(a[0])^int(ASTAT[12])
    elif(a[1:]=="0100"):
        val=int(a[0])^int(ASTAT[14])
    elif(a[1:]=="1000"):
        val=int(a[0])^int(ASTAT[10])
    elif(a[1:]=="1001"):
        val=int(a[0])^int(ASTAT[11])
    elif(a[1:]=="1010"):
        val=int(a[0])^int(ASTAT[9])
    elif(a[1:]=="1011"):
        val=int(a[0])^int(ASTAT[8])
    return val

#---------------------------------------------------------------------------
# Main Function
#---------------------------------------------------------------------------
def Referance_Model():
    global reg_bank
    reg_bank = {
        "R":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
        "I":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
        "M":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
        "0110":{"0000":"0000000000000000","0001":"0000000000000000","0011":"0000000000000000","0100":"XXXX","0101":"0000000000000000"},
        "0111":{"1011":"0000000000000000","1100":"0000000000000000","1110":"0000000000000001"}
    }
    f=open(path+"/pm_file.txt","rt")
    l=[]
    u=False
    for i in f:
        i=hex_to_ubin(i.strip("\n"))
        if(i[:16]!="1"*16):
            l.append(i.strip("\n"))
    i=0
    while(i<len(l)):
        jump=False
        if(l[i][0]=="0"):
            s=1
        else:
            s=condition(l[i][27:])
        if(s==1):
            if int(l[i][:8]) == 1:
                if(int(get_from_reg("01111110"))==1):
                    i=get_from_reg("01100100")
                    put_to_reg('01100100',"XXXX")
                    put_to_reg("01111110",format(1,"016b"))
                    put_to_reg("01100101",format(0,"016b"))     #PCSTKP
            if int(l[i][3:6]) == 100:                                                   #IF condition JUMP (Md,Ic)
                jump=True
                M=int(get_from_reg("00101"+l[i][22:25]),2)
                I=int(get_from_reg("00011"+l[i][19:22]),2)
                i=I+M
                put_to_reg("01100000",format(i,"016b"))     #FADDR
            if int(l[i][3:6]) == 101:                                                   #IF condition CALL (Md,Ic)
                jump=True
                M=int(get_from_reg("00101"+l[i][22:25]),2)
                I=int(get_from_reg("00011"+l[i][19:22]),2)
                if(int(get_from_reg("01111110"))==1):
                    put_to_reg("01100100",format(i+1,"016b"))     #PCSTK
                    i=I+M
                    put_to_reg("01100000",format(i,"016b"))     #FADDR
                    put_to_reg("01111110",format(2,"016b"))
                    put_to_reg("01100101",format(1,"016b"))     #PCSTKP
                else:
                    put_to_reg("01111110",format(4,"016b"))
            if((jump==False) or ((jump==True) and (i<len(l)))):
                if(i<len(l)-1):
                    put_to_reg("01100000",format(i+1,"016b"))   #FADDR
                    put_to_reg("01100001",format(i,"016b"))     #DADDR  
                put_to_reg("01100011",format(i-1,"016b"))         #PC
                primary(l[i])
            else:
                continue
        i=i+1