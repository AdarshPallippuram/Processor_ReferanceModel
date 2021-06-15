import os
import time
import Assembler
import Processor
import Memcheck

# a=input("Enter Folder Name : ")
a='tests'
start=time.time()

PM_LOCATE=os.path.dirname(__file__)+"/"+a+"/"
arr0 = os.listdir(PM_LOCATE)
for folder in arr0:
    folder_locate = PM_LOCATE + folder + '/'
    arr1 = os.listdir(folder_locate)
    i = 0
    for file in arr1:
        folder_path = Memcheck.run(file,folder_locate,i)
        Assembler.run(folder_path)
        Processor.run(folder_path)
        i += 1

end=time.time()
print("Time taken to complete program = %s"%(end-start))