from commonFunctions import *

if __name__ == "__main__":
    if len(sys.argv) == 3: 
        runOnce(open("SNO2synlog.txt","w"),int(sys.argv[1]),float(sys.argv[2]),21,8,False,True)
    else: 
        runOnce(open("SNO2synlog.txt","w"),2000,0.001,21,8,False,True)