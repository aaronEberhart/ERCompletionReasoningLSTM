import re

def EQtoSC(line,new):
    if "ObjectIntersectionOf" in line[1]: x = intersectionSplit(line,new)
    else: x = "SubClassOf({} {})\nSubClassOf({} {})".format(line[0],line[1],line[1],line[0])
    #print(x)
    return x

'''
B ≡ A ⊓ ∃S.D

B ≡ A ⊓ X2
X2 ≡ ∃S.D

B ⊑ A
B ⊑ X2
A ⊓ X2 ⊑ B
X2 ⊑ ∃S.D
∃S.D ⊑ X2


A ≡ B ⊓ C ⊓ ∃S.D

A ≡ B ⊓ X1
X1 ≡ C ⊓ X2
X2 ≡ ∃S.D

A ⊑ B
A ⊑ X1
B ⊓ X1 ⊑ A
X1 ⊑ C
X1 ⊑ X2
C ⊓ X2 ⊑ X1
X2 ⊑ ∃S.D
∃S.D ⊑ X2
'''
def intersectionSplit(line,new):
    newLine = [line[0]]
    newLine.extend(line[1][21:-1].split(" ",1))
    x = ""
    if canEasySplit(line[1]):
        #print("easy\t",line)
                
        while separable(newLine[-1]):
            if not "ObjectIntersectionOf" in newLine[-1]:
                rem = newLine[-1]
                newLine.extend(newLine[-1].split(" ",1))
                newLine.remove(rem)
            else:
                pass
        for C in newLine:
            if C in new.keys(): pass
            else: new[C] = "sep:X{}".format(len(new)+1)
        if len(newLine) == 3:
            '''
            B ⊑ A
            B ⊑ X
            A ⊓ X ⊑ B
            X ⊑ ∃S.D
            ∃S.D ⊑ X
            '''
            if isExistential(newLine[-1]):
                x = "SubClassOf({} {})\nSubClassOf({} {})\nSubClassOf(ObjectIntersectionOf({} {}) {})\nSubClassOf({} {})\nSubClassOf({} {})\n".format(newLine[0],newLine[1],newLine[0],new[newLine[-1]],newLine[1],new[newLine[-1]],newLine[0],new[newLine[-1]],newLine[-1],newLine[-1],new[newLine[-1]])
            else:
                raise
        else:
            '''
            A ≡ B ⊓ C ⊓ ∃S.D
            
            A ⊑ B
            A ⊑ X1
            B ⊓ X1 ⊑ A
            X1 ⊑ C
            X1 ⊑ X2
            C ⊓ X2 ⊑ X1
            X2 ⊑ ∃S.D
            ∃S.D ⊑ X2
            '''
            X1 = "ObjectIntersectionOf({} {})".format(newLine[2],newLine[3])
            X1r = "ObjectIntersectionOf({} {})".format(newLine[3],newLine[2])
            
            if X1 in new.keys() or X1r in new.keys(): pass
            else: new[X1] = "sep:X{}".format(len(new)+1)
            
            X2 = newLine[3]
            concept = True
            if isExistential(X2): 
                concept = False
                if X2 in new.keys(): pass
                else: new[X2] = "sep:X{}".format(len(new)+1)
                '''
                X2 ⊑ ∃S.D
                ∃S.D ⊑ X2
                '''
                x = x + "SubClassOf({} {})\n".format(new[X2],newLine[3])
                x = x + "SubClassOf({} {})\n".format(newLine[3],new[X2])                
                
            #
            '''
            A ⊑ B
            A ⊑ X1
            '''
            x = x + "SubClassOf({} {})\n".format(newLine[0],newLine[1])
            x = x + "SubClassOf({} {})\n".format(newLine[0],new[X1])
            '''
            B ⊓ X1 ⊑ A
            C ⊓ X2 ⊑ X1
            '''
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[1],new[X1],newLine[0])
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[2],X2 if concept else new[X2],new[X1])            
            '''
            X1 ⊑ C
            X1 ⊑ X2
            '''
            x = x + "SubClassOf({} {})\n".format(new[X1],newLine[2])
            x = x + "SubClassOf({} {})\n".format(new[X1],X2 if concept else new[X2])
            #print(newLine)#print(x,"\n")
    else:
        if newLine[2][0] != 'O':
            '''
            A ≡ B ⊓ C ⊓ ∃R.D ⊓ ∃S.E
            
            A ⊑ B
            A ⊑ X1
            B ⊓ X1 ⊑ A
            X1 ⊑ C
            X1 ⊑ X2
            C ⊓ X2 ⊑ X1
            X2 ⊑ X3
            X2 ⊑ X4
            X3 ⊓ X4 ⊑ X2
            X3 ⊑ ∃R.D
            ∃R.D ⊑ X3
            X4 ⊑ ∃S.E
            ∃S.E ⊑ X4
            '''
            y = newLine[2].split(" ",1)
            z = y[1].split(" ",2)[-1]
            y[1] = " ".join(y[1].split(" ",2)[:2])
            y.append(z)
            del newLine[2]
            newLine.extend(y)
            
            X3 = newLine[3]
            if X3 in new.keys(): pass
            else: new[X3] = "sep:X{}".format(len(new)+1)
            
            X4 = newLine[4]
            if X4 in new.keys(): pass
            else: new[X4] = "sep:X{}".format(len(new)+1)
            
            X2 = "ObjectIntersectionOf({} {})".format(newLine[3],newLine[4])
            X2r = "ObjectIntersectionOf({} {})".format(newLine[4],newLine[3])
            
            if X2 in new.keys() or X2r in new.keys(): pass
            else: new[X2] = "sep:X{}".format(len(new)+1)

            X1 = "ObjectIntersectionOf({} {})".format(newLine[2],X2)
            X12 = "ObjectIntersectionOf({} {})".format(newLine[2],X2r)
            X1r = "ObjectIntersectionOf({} {})".format(X2,newLine[2])
            X12r = "ObjectIntersectionOf({} {})".format(X2r,newLine[2])
            
            if X1 in new.keys() or X1r in new.keys() or X12 in new.keys() or X12r in new.keys(): pass
            else: new[X1] = "sep:X{}".format(len(new)+1)            
            
            '''
            A ⊑ B
            A ⊑ X1
            X1 ⊑ C
            X1 ⊑ X2
            X2 ⊑ X3
            X2 ⊑ X4
            '''
            x = x + "SubClassOf({} {})\n".format(newLine[0],newLine[1])
            x = x + "SubClassOf({} {})\n".format(newLine[0],new[X1])
            x = x + "SubClassOf({} {})\n".format(new[X1],newLine[2])
            x = x + "SubClassOf({} {})\n".format(new[X1],new[X2])
            x = x + "SubClassOf({} {})\n".format(new[X2],new[X3])
            x = x + "SubClassOf({} {})\n".format(new[X2],new[X4])            
            '''
            B ⊓ X1 ⊑ A
            C ⊓ X2 ⊑ X1
            X3 ⊓ X4 ⊑ X2
            '''
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[1],new[X1],newLine[0])
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[2],new[X2],new[X1])
            x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(new[X3],new[X4],new[X2])
            '''
            X3 ⊑ ∃R.D
            ∃R.D ⊑ X3
            '''
            x = x + "SubClassOf({} {})\n".format(new[X3],newLine[3])
            x = x + "SubClassOf({} {})\n".format(newLine[3],new[X3])  
            '''
            X4 ⊑ ∃S.E
            ∃S.E ⊑ X4
            '''
            x = x + "SubClassOf({} {})\n".format(new[X4],newLine[4])
            x = x + "SubClassOf({} {})\n".format(newLine[4],new[X4])
            
            #print(newLine)
        else:
            
            while stillSplittable(newLine[-1]):
                #print(newLine)
                y = newLine[-1][21:-1].split(" ",1)
                #print(y)
                newLine.pop(-1)
                newLine.append(y[0])
                newLine.append(y[1])
                #            
            
            if newLine[-1].count(' ') > 1:
                y = newLine[-1][21:-1].split(" ",1)
                newLine.pop(-1)
                newLine.append(y[0])
                newLine.append(y[1])
                
            #print(newLine)
            
            last = newLine[-1]
            if last in new.keys(): pass
            else: new[last] = "sep:X{}".format(len(new)+1)
            
            '''
            last ⊑ ∃R.C
            ∃R.C ⊑ last
            '''
            x = x + "SubClassOf({} {})\n".format(new[last],newLine[-1])
            x = x + "SubClassOf({} {})\n".format(newLine[-1],new[last])
            
            newLine[-1] = new[last]
            
            #print(newLine)
            
            while len(newLine) > 2:
                if len(newLine[-2]) > 7:
                    Y = "ObjectIntersectionOf({} {})".format(newLine[-2],newLine[-1])
                    Yr = "ObjectIntersectionOf({} {})".format(newLine[-1],newLine[-2])
                    
                    if Y in new.keys() or Yr in new.keys(): pass
                    else: 
                        new[Y] = "sep:X{}".format(len(new)+1) 
                        '''
                        Y ⊑ B
                        Y ⊑ X
                        B ⊓ X ⊑ Y
                        '''
                        x = x + "SubClassOf({} {})\n".format(new[Y],newLine[-1])
                        x = x + "SubClassOf({} {})\n".format(new[Y],newLine[-2])
                        x = x + "SubClassOf(ObjectIntersectionOf({} {}) {})\n".format(newLine[-2],newLine[-1],new[Y])
                    
                    newLine.pop(-1)
                    newLine[-1] = new[Y]
                    
                    #print(newLine)
                else:
                    last = "ObjectSomeValuesFrom({} {})".format(newLine[-2],newLine[-1])
                    if last in new.keys(): pass
                    else: 
                        new[last] = "sep:X{}".format(len(new)+1)
                        '''
                        last ⊑ ∃R.C
                        ∃R.C ⊑ last
                        '''
                        x = x + "SubClassOf({} {})\n".format(new[last],last)
                        x = x + "SubClassOf({} {})\n".format(last,new[last])
                    #print(x)
                    newLine.pop(-1)
                    newLine[-1] = new[last]
                    
                    #print(newLine)
            
            x = x + "SubClassOf({} {})\nSubClassOf({} {})\n".format(newLine[0],newLine[1],newLine[1],newLine[0])#"EquivalentClasses({} {})".format(line[0],line[1])
    
    return x


def stillSplittable(string):
    #print(string)
    pattern1 = re.compile("^.*(ObjectIntersectionOf)+.*$")
    pattern2 = re.compile("^.*(ObjectSomeValuesFrom){2,}.*$")
    val = pattern1.match(string) != None or pattern2.match(string) != None   
    return val

def isExistential(string):
    return "ObjectSomeValuesFrom" in line

def separable(string):
    pattern = re.compile("^[a-z]{3}:[A-Z]{1}[0-9]{5}\s")
    return pattern.match(string) != None

def canEasySplit(line):
    if not "ObjectSomeValuesFrom" in line: return True
    if line.count("ObjectSomeValuesFrom") == 1:
        return line.rfind("ObjectSomeValuesFrom") > line.rfind("ObjectIntersectionOf")
    #print(line)
    return False

pattern = re.compile("EquivalentClasses+")

file = open("SNOMED2012fs.owl","r")
file2 = open("SNOrMED2012fs.owl","w")

new = {}

for line in file:
    if pattern.match(line) != None: file2.write(EQtoSC(line[18:-2].split(" ",1),new))
    else: file2.write(line)

file.close()
file2.close()