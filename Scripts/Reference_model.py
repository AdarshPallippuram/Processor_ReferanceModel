import time
import Final_Assembler
import Register
import Shifter
import ALU

def primary(OpCode):                  # OpCode - opcode
    
    if int(OpCode) == 0:
        # print('nop')
        time.sleep(3)

    elif int(OpCode[:9]) == 1:
        # print('idle')
        time.sleep(10)

    elif int(OpCode[:8]) == 1:
        # print('rts')
        Register.put_to_reg('01100011',Register.get_from_reg('01100100'))
        # deleting value in PCSTK not done

    elif int(OpCode[:8]) == 10:
        # print('PUSH PCSTK = <ureg>')
        Register.put_to_reg('01100100',OpCode[8:16])

    elif int(OpCode[:8]) == 11:
        # print('<ureg> = POP PCSTK')
        Register.put_to_reg(OpCode[8:16],Register.get_from_reg('01100100'))
        # deleting value in PCSTK not done

    elif int(OpCode[:6]) == 11:
        #print('immediate data(16-bits) -> ureg')
        Register.put_to_reg(OpCode[8:16],OpCode[16:32])
        # print(OpCode[8:16],Register.get_from_reg(OpCode[8:16]))

    elif int(OpCode[1:6]) == 1:
        # print('IF condition ureg1 = ureg2')
        # ureg1 as 'dest' and ureg2 as 'source'
        Register.put_to_reg(OpCode[8:16],Register.get_from_reg(OpCode[16:23]))
    
    elif int(OpCode[1:6]) == 1001:
        print('IF condition DM(Ia,Mb) <-> ureg')
    
    elif int(OpCode[1:6]) == 1000:
        print('IF condition modify (Ia,Mb)')
    
    elif int(OpCode[1:6]) == 1100:
        print('IF condition JUMP (Md,Ic)')
    
    elif int(OpCode[1:6]) == 1101:
        print('IF condition JUMPR (Md,Ic)')

    elif int(OpCode[1]) == 1:
        # print('IF condition compute')
        if OpCode[6:8] == '00':
            ALU.ALU(OpCode[(31-22):(31-16)], OpCode[(31-16):(31-12)], OpCode[(31-12):(31-8)], OpCode[(31-8):(31-4)])
        elif OpCode[6:8] == '01':
            print('MUL')
        else:
           Shifter.shifter(OpCode[9:27])
#--------------------------------------------------------  
# Register dump
#--------------------------------------------------------

b='opcode.txt'
f=open(b,"rt")
z= r'C:\Users\alanm\OneDrive\Desktop\VS_code\Processor_ReferanceModel\ALU test files\dump files\d'+Final_Assembler.xyz+'.txt'
g=open(z,"wt")
l=[]
for i in f:
    l.append(i.strip("\n"))
i=0
while(i<len(l)):
    primary(l[i])
    i=i+1
    
for i in range(3):
    a=format(i,"04b")
    for j in range(16):
        b=format(j,"04b")
        try:
            g.write("{}{} : {}".format(Register.reg[a],j,Register.ubin_to_hex(Register.reg_bank[Register.reg[a]][b])))
        except:
            g.write("{}{} : {}".format(Register.reg[a],j,Register.reg_bank[Register.reg[a]][b]))
        g.write("\n")
for i in Register.reg_name.keys():
    g.write("{} : {}".format(i,Register.reg_bank[Register.reg_name[i][0:4]][Register.reg_name[i][4:]]))
    g.write("\n")
print("Register values stored in {}.txt".format(z))

        