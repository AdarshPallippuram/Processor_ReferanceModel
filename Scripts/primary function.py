
import time
def prime_fun(oc):                  # oc - opcode
    
    cu = {                          # cu - compute unit
        #'00':ALU(oc[0],),
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

    elif int(oc[1:6]) == 1:
        # print('IF condition ureg1 = ureg2')
        # ureg1 as 'dest' and ureg2 as 'source'
        put_to_reg(oc[8:16],get_from_reg(oc[16:23]))
    
    elif int(oc[1:6]) == 1001:
        print('IF condition DM(Ia,Mb) <-> ureg')
    
    elif int(oc[1:6]) == 1000:
        print('IF condition modify (Ia,Mb)')
    
    elif int(oc[1:6]) == 1100:
        print('IF condition JUMP (Md,Ic)')
    
    elif int(oc[1:6]) == 1101:
        print('IF condition JUMPR (Md,Ic)')

    elif int(oc[1]) == 1:
        # print('IF condition compute')
        cu[oc[6:8]]
        