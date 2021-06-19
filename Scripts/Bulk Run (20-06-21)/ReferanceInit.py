import configparser
import re
import sys
from ReferanceModel import Referance_Model
import os
from datetime import datetime
from shutil import copyfile,rmtree
from Assembler import Primary
import cProfile,pstats,io
PM_LOCATE=""
DM_LOCATE=""
def profile(fnc):
    def inner(*args,**kwargs):
        pr=cProfile.Profile()
        pr.enable()
        retval=fnc(*args,**kwargs)
        pr.disable()
        s=io.StringIO()
        sortby='cumulative'
        ps=pstats.Stats(pr,stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return(retval)
    return(inner)
def assembler(INST_LOCATE):
    try:
        g=open(INST_LOCATE,"rt")
    except Exception as e:
        print(e)
        return 0
    f=open(PM_LOCATE,"wt")
    f.write(format(int(16*"1"+16*"0",2),"08X")+"\n")
    l=[]
    for i in g:
        l.append(i.strip("\n"))
    i=0
    while(i<len(l)):
        instr=l[i]
        i=i+1
        if(re.match(".memcheck[ ]?",instr.lower())):
            break
        if(re.match(".CALL[ ]?[(][ ]?[0-9,A-F]+[ ]?[)][ ]?",instr.upper())):
            f.write(format(int(16*"1"+format(int(re.findall("[0-9,A-F]+",instr)[1],16),"016b"),2),"08X")+"\n")
            instr=l[i]
            i=i+1
            if(re.match(".memcheck[ ]?",instr.lower())):
                break
        if("#" in instr):
            inst = re.split("#",instr)[0]
            if(re.match("^[ ]*#",instr)):
                continue
        elif("/*" in instr):
            inst = instr.split("/")[0]
            if(re.match("^[/][*]",instr)):
                while("*/" not in instr):
                    instr=l[i]
                    i=i+1
                continue
        else:
            inst = instr
        if(len(inst)>2 and inst!=" " and inst!="\n" and inst!="\t" and inst!=""):
            OpCode=Primary(inst)
        else:
            continue
        if("ERROR" in OpCode):
            print("Faulty instruction : {}\nAt location: {}\n".format(instr,INST_LOCATE))
            f.close()
            g.close()
            return 0   
        else:
            f.write(format(int(OpCode,2),"08X"))
            f.write("\n")
        if("/*" in instr):
            while("*/" not in instr):
                instr=l[i]
                i=i+1
    f.close()
    g.close()
    return 1
def memchk(MEM_LOCATE):
    find=".memcheck"
    mem_file=open(MEM_LOCATE,'r')
    dm_file=open(DM_LOCATE,'r')
    tlines = [line.replace(' ', '').replace('\t','').strip() for line in mem_file.readlines()]
    dlines = [line.replace(' ', '').replace('\t','').strip() for line in dm_file.readlines()]
    try:
        slines=list(filter(None,[x.lower() for x in tlines[[line.lower() for line in tlines].index(find)+1:]]))
        if not len(set(slines)-set(dlines)):
            return 0
        else:
            return 1
    except Exception as e:
        return 1
@profile
def main():
    global PM_LOCATE
    global DM_LOCATE
    startTime = datetime.now()
    file_count=0
    valid_count=0
    fail_mfile=[]
    cnfg = configparser.ConfigParser()
    cnfg.optionxform = str
    cnfg.read('Path.ini')
    if cnfg.has_section('PATHS'):
        DIR=cnfg.get('PATHS','DIR',raw=True)
        PM_LOCATE=cnfg.get('PATHS','PM_LOCATE',raw=True)
        DM_LOCATE=cnfg.get('PATHS','DM_LOCATE',raw=True)
        DMrdfl_LOCATE=cnfg.get('PATHS','DMrdfl_LOCATE',raw=True)
        MEMfail_LOCATE=cnfg.get('PATHS','MEMfail_LOCATE',raw=True)
    else:
        print("Error! PATHS configurations not found. Run Confiqure_Path.py.")
        os.system('pause')
        sys.exit()
    if cnfg.has_section('IDENTIFIER'):
        idntfr=cnfg.get('IDENTIFIER','idntfr',raw=True)
    else:
        print("Error! IDENTIFIER configurations not found. Run Confiqure_Path.py.")
        os.system('pause')
        sys.exit()
    if cnfg.has_section('AVOID'):
        avoid=cnfg.options('AVOID')
    else:
        print("Error! AVOID configurations not found. Run Confiqure_Path.py.")
        os.system('pause')
        sys.exit()
    try:
        rmtree(MEMfail_LOCATE)
    except:
        pass
    os.makedirs(MEMfail_LOCATE)
    a=[]
    for root,directories,files in os.walk(DIR):
            for name in files:	    
                if not name in avoid:
                    file_count+=1
                    if assembler(os.path.join(root,name)):
                        valid_count+=1
                        print("File No. "+ str(file_count))
                        print(os.path.join(root,name))
                        if(name[0]==idntfr):
                            copyfile("SAC/DMrd_files/{}".format(name),os.path.join("SAC","dm_file.txt"))
                        else:
                            h=open("SAC/dm_file.txt","wt")
                            for i in range(65536):
                                h.write(format(i,"04x")+"\txxxx\n")
                            h.close()
                        try:
                            Referance_Model()
                        except Exception as e:
                            a.append(e)
                        if(memchk(os.path.join(root,name))):
                            fail_mfile.append(os.path.join(root,name))
                            copyfile(DM_LOCATE,os.path.join(MEMfail_LOCATE,"DMfail_"+re.split(r'/|\\',os.path.join(root,name))[-2]+"_"+name))
                            print("Mismatch in DM file")
                        else:
                            print("DM Files match")
                        #os.remove("SAC/dm_file.txt")
                        #os.remove("SAC/pm_file.txt")
    print("{} No. out of {} files ran successfully".format(valid_count,file_count))
    if(len(fail_mfile)): 
        print("\n\nFailed Files due to memcheck data mismatch : ")#, *fail_mfile, sep="\n")
        for i in range(len(fail_mfile)):
            print(fail_mfile[i])
    else:
        print("\n\nAll tests successfully passed in MEMCHECK\n")
    print("\n\nTime Analysis:\nStart time: {}\nStop Time: {}\nTime taken to execute the script: {}".format(startTime,datetime.now(),(datetime.now() - startTime)))
    os.system('pause')
if(__name__=="__main__"):
    main()