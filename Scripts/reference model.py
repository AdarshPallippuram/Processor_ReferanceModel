# if the test data of register dump is in the format <addr><\t><data>, then change the condition of if statement in 
# line 266 to if(i!=j)
# The file opening logic has been written keeping into consideration that the test files have the format
# - a1 - left shift                     //This is the parent folder
#   - a_p1.txt                          //Holds the instructions
#   - a1.txt                            //Holds the data memory output
# The path is defined such that no change needs to be made there. The tesing files should be put in their own folders
# inside a "Test" folder, i.e a1 - left shift is inside a folder "Test" in the script directory
import os
import time
path=os.path.dirname(__file__)+"/Test/"          
#---------------------------------------------------------------------------
# Reg banks, uregs and related dictionaries and functions
#---------------------------------------------------------------------------

reg_bank={
    "R":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "I":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "M":{"0000":"XXXX","0001":"XXXX","0010":"XXXX","0011":"XXXX","0100":"XXXX","0101":"XXXX","0110":"XXXX","0111":"XXXX","1000":"XXXX","1001":"XXXX","1010":"XXXX","1011":"XXXX","1100":"XXXX","1101":"XXXX","1110":"XXXX","1111":"XXXX"},
    "0110":{"0000":"0000000000000000","0001":"0000000000000000","0011":"0000000000000000","0100":"0000000000000000","0101":"0000000000000000"},
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
            R_val[0]=R_val[0][0]*shift+R_val[0]
            R_val[0]=R_val[0][0:16]
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
        #print('IF condition DM(Ia,Mb) <-> ureg')
        i_data=format(int(get_from_reg("00010"+OpCode[19:22]),2),"04x")
        m_data=get_from_reg("00100"+OpCode[22:25])
        h=open(path+_b+"/dm_file.txt","rt")
        if(OpCode[25]=="1"):
            #print("write to dm")
            ureg_data=format(int(get_from_reg(OpCode[8:16]),2),"04x")
            i=open(path+_b+"/dm_file2.txt","wt")
            for j in h:
                if (i_data in j):
                    j=i_data+"\t"+ureg_data+"\n"
                i.write(j)
            h.close()
            i.close()
            os.remove(path+_b+"/dm_file.txt")
            os.rename(path+_b+"/dm_file2.txt",path+_b+"/dm_file.txt")
        else:
            #print("Read from Dm")
            for j in h:
                if(i_data in j):
                    ureg_data=j.split("\t")[-1].strip("\n")
            put_to_reg(OpCode[8:16],ureg_data.upper())
            h.close()
        i_data=format(int(i_data,16)+int(m_data,2),"016b")
        put_to_reg("00010"+OpCode[19:22],i_data)
    elif int(OpCode[1:6]) == 1000:
        print('IF condition modify (Ia,Mb)')
        i_data=get_from_reg("00010"+OpCode[19:22])
        m_data=get_from_reg("00100"+OpCode[22:25])
        i_data=format(int(i_data,2)+int(m_data,2),"016b")
        put_to_reg("00010"+OpCode[19:22],i_data)
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

_b=input("Enter name of OpCode folder:")
f=open(path+_b+"/pm_file.txt","rt")
g=open(path+_b+"/reg_dump.txt","wt")
h=open(path+_b+"/dm_file.txt","wt")
for i in range(65536):
    h.write(format(i,"04x")+"\txxxx\n")
h.close()
start=time.time()
l=[]
for i in f:
    l.append(i.strip("\n"))
i=0
while(i<len(l)):
    if(l[i][0]=="0"):
        s=1
    else:
        s=condition(l[i][27:])
    if(s==1):
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
print("Register values stored in reg_dump.txt")
print("Data Memory dumped in dm_file.txt")
f=open(path+_b+"/dm_file.txt","rt")
g=open(path+_b+"/"+_b[0:2]+".txt","rt")
__o=True
for i,j in zip(f,g):
    if("xxxx" in i and "xxxx" in j):
        continue
    if(i[5:]!=j):
        __o=False
        print("Error in {}".format(i[0:5]))
if(__o==False):
    print("Difference exist between Verilog Simulation and Referance Model output")
else:
    print("Verilog Simulation and Referance model outputs are equal")
end=time.time()
print("Time taken to complete program = %s"%(end-start))
