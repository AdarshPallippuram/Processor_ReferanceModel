import os
import shutil

def run(a,folder_locate,i):
    if(a!="Owner.md"):
        os.mkdir(folder_locate+"p{} - ".format(i)+a[:-4])
        f=open(folder_locate+a,"rt")
        l=[]
        b=False
        for q in f:
            z=q.strip("\n")
            if(z.upper()==".MEMCHECK"):
                b=True
                continue
            if(b==True):
                l.append(z.lower())
        g=open(folder_locate+"e{}.txt".format(i),"wt")
        for j in range(0,65536):
            for k in range(len(l)):
                if(format(j,"04x")==l[k][:4]):
                    l99 = l[k].split()
                    g.write(l99[0]+'    '+l99[1]+"\n")
                    break
            else:
                g.write(format(j,"04x")+"\txxxx\n")
        f.close()
        g.close()
        shutil.copy(folder_locate+a,folder_locate+"/p{} - {}/instr.txt".format(i,a[:-4]))
        shutil.move(folder_locate+"e{}.txt".format(i),folder_locate+"/p{} - {}/expected.txt".format(i,a[:-4]))
        return folder_locate + "p{} - {}".format(i,a[:-4])