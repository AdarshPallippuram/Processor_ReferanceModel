import Register

def signed_mul(num1,num2,x,y):
    comp1=0
    comp2 =0
    if(x==1 and num1[0]=="1"):
        num1 = Register.compliment(num1)
        comp1 = 1
    else:
        num1= int(num1,2)
    if(y==1 and num2[0]=="1"):
        num2 = Register.compliment(num2)
        comp2 = 1
    else:
        num2 = int(num2,2)
    product = format(num1*num2,'040b')
    if(comp1^comp2):
        product = Register.compliment40(product)
        product = format(product,'040b')
        x=len(product.split('1')[0])
        product = '1'*x + product[x:]
    return product


def unsigned_mul(num1,num2):
    n1 = int(num1,2)
    n2 = int(num2,2)
    product = format(n1*n2,'040b')
    return product

def multi(op):
    MRF = ['0010000000000000001000000000000000000000']
    MR2 = MRF[-1][0:8]
    MR1 = MRF[-1][8:24]
    MR0 = MRF[-1][24:40]
    Rn = "0000"+ op[7:11]
    Rx = "0000"+ op[11:15]
    Ry = "0000"+ op[15:19]
    if(op[0:2]=="00"):
        if(op[2]=="0"):     
            if(op[17:19]=="00"): #rn = mr0
                rn = MR0[0:16]
                Register.put_to_reg(Rn,MR0[0:16])
            elif(op[17:19]=="01"): #rn = mr1
                rn = MR1[0:16]
                Register.put_to_reg(Rn,MR1[0:16])
            elif(op[17:19]=="10"): #rn = mr2
                rn = "00000000"+MR2
                Register.put_to_reg(Rn,"00000000"+MR2)
            elif(op[17:19]=="11"): #rn = sat mrf
                
                if(op[4:6]=="01" and "1" in MRF[-1][0:8]):
                    rn = Register.hex_to_ubin40("00ffffffff")[0:16]  #unsigned fractional
                if(op[4:6]=="00"and "1" in MRF[-1][0:24]):
                    rn = Register.hex_to_ubin40("000000ffff")[0:16]  #unsigned integer
                if(op[4:6]=="11" and "1" in MRF[-1][0:9] and "0" in MRF[-1][0:9]):
                    rn = Register.hex_to_ubin40("007fffffff")
                if(op[4:6]=="10" and "1" in MRF[-1][0:25] and "0" in MRF[-1][0:25]):
                    rn = Register.hex_to_ubin40("0000007fff")
            Register.put_to_reg(Rn,rn[0:16])
            return rn
            
            
        else:
            if(op[17:19]=="00"):
                MR0 =Register.get_from_reg(Rx)
                MRF.append(MR2+MR1+MR0)
                
            elif(op[17:19]=="01"):
                MR1 = Register.get_from_reg(Rx)
                MRF.append(MR2+MR1+MR0)
                
            elif(op[17:19]=="10"):
                MR2 ="00000000"+ Register.get_from_reg(Rx)
                MRF.append(MR2+MR1+MR0)
                
            elif(op[17:19]=="11"):
                if(op[4:6]=="01" and "1" in MRF[-1][0:8]):
                    mr = Register.hex_to_ubin40("00ffffffff")  #unsigned fractional
                    MRF.append(mr)
                elif(op[4:6]=="00"and "1" in MRF[-1][0:24]):
                    mr = Register.hex_to_ubin40("000000ffff")  #unsigned integer
                    MRF.append(mr)
            
                elif(op[4:6]=="11" and "1" in MRF[-1][0:9] and "0" in MRF[-1][0:9]):
                    mr = Register.hex_to_ubin40("007fffffff")
                    MRF.append(mr)
                elif(op[4:6]=="10" and "1" in MRF[-1][0:25] and "0" in MRF[1][0:25]):
                    mr = Register.hex_to_ubin40("0000007fff")
                    MRF.append(mr)
            return MRF


    elif(op[0:2]=="01"):  # rx*ry
        if(op[2]=="0"):    #rn = rx*ry
            if(op[3:5]=="00"): #unsigned multiplication
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                rn = unsigned_mul(rx,ry)[24:40]
                Register.put_to_reg(Rn,unsigned_mul(rx,ry)[24:40])
                
    
            if(op[3:5]!="00"): #signed multiplication
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                Register.put_to_reg(Rn,signed_mul(rx,ry,op[3],op[4])[24:40])
                rn = signed_mul(rx,ry,op[3],op[4])[24:40]
            
            return rn
                
           
            
            
        else: #mr=rx*ry
            if(op[3:5]=="00"): #unsigned multiplicatiopn
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                
                MRF.append(unsigned_mul(rx,ry))
                return MRF[-1]
    
            if(op[3:5]!="00"): #signed multiplication
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)

                MRF.append(signed_mul(rx,ry,op[3],op[4]))
                return MRF[-1]
            

    elif(op[0:2]=="10"):   # mr+rx*ry
        if(op[2]=="0"):  #rn = mr+ rx*ry
            
            if(op[3:5]=="00"): 
                rx= Register.get_from_reg(Rx)
                ry= Register.get_from_reg(Ry)
                rn = int(MRF[-1][0:16],2)+int(unsigned_mul(rx,ry)[24:40])
                rn = format(rn,'016b')
                Register.put_to_reg(Rn,rn)
                return rn
                
    
            if(op[3:5]!="00"): #signed multiplication
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                rn = int(MRF[-1][0:16],2)+int(signed_mul(rx,ry,op[3],op[4])[24:40])
                rn = format(rn,'016b')
                Register.put_to_reg(Rn,rn)
                return rn
                
                
        else:       #mr = mr+rx*ry
            if(op[3:5]=="00"): 
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                rn = int(MRF[-1],2)+int(unsigned_mul(rx,ry),2)
                rn = format(rn,'040b')
                MRF.append(rn)
                return MRF
    
            if(op[3:5]!="00"): #signed multiplication
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                rn = int(MRF[-1],2)+int(signed_mul(rx,ry),2)
                rn = format(rn,'040b')
                MRF.append(rn)
                return MRF
            

    else:                   #rn = mr-rx*ry
        if(op[2]=="0"):
            if(op[3:5]=="00"): 
                rx= Register.get_from_reg(Rx)
                ry= Register.get_from_reg(Ry)
                rn = int(MRF[-1][0:16],2)-int(unsigned_mul(rx,ry)[24:40])
                rn = format(rn,'016b')
                Register.put_to_reg(Rn,rn)
                return rn
                
    
            if(op[3:5]!="00"): #signed multiplication
                rx= Register.get_from_reg(Rx)
                ry= Register.get_from_reg(Ry)
                rn = int(MRF[-1][0:16],2)-int(signed_mul(rx,ry)[24:40])
                rn = format(rn,'016b')
                Register.put_to_reg(Rn,rn)
                return rn
                
        else:
            if(op[3:5]=="00"):
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                rn = int(MRF[-1],2)-int(unsigned_mul(rx,ry),2)
                rn = format(rn,'040b')
                MRF.append(rn)
                return MRF
    
            if(op[3:5]!="00"): #signed multiplication
                rx=Register.get_from_reg(Rx)
                ry=Register.get_from_reg(Ry)
                rn = int(MRF[-1],2)-int(signed_mul(rx,ry),2)
                rn = format(rn,'040b')
                MRF.append(rn)
                return MRF
    
    
     
f = open("instruction_out.txt", "r")
for x in f:
    print(multi(x[8:24]))
                   
