from commonFunctions import *

if __name__ == "__main__":    
    if len(sys.argv) == 3: 
        nTimesCrossValidate(10,int(sys.argv[1]),float(sys.argv[2]),21,8,True,False)
    else: 
        nTimesCrossValidate(10,20000,0.0001,21,8,True,False)

    
    