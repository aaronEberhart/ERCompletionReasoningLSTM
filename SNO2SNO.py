from commonFunctions import *    

    
if __name__ == "__main__":
    if len(sys.argv) == 3: 
        runOnce(open("SNO2SNOlog.txt","w"),int(sys.argv[1]),float(sys.argv[2]),21,8,False,False)
    else: 
        runOnce(open("SNO2SNOlog.txt","w"),20000,0.0001,21,8,False,False)
 