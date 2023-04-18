from machineConst import *

class GcodeReader():
    def __init__(self, out):
        self.out = out
        self.buff = []
        self.line = 0

    def readfile(self, filename):
        fp=open(filename,'rb')
        self.buff = fp.readlines()
        fp.close()
        self.points = []
        x,y,z,a,b, = 0,0,0,0,0

        for line in self.buff:
            words=line.decode('UTF-8').split()
            if len(words)>0:
                if words[0]=='G0' or words[0]=='G1':
                    for i in range(len(words)-1):
                        if words[i+1][0] == "X":
                            x = float(words[i+1][1:])
                        elif words[i+1][0] == "Y":
                            y = float(words[i+1][1:])
                        elif words[i+1][0] == "Z":
                            z = float(words[i+1][1:])
                        elif words[i+1][0] == "A":
                            a = float(words[i+1][1:])
                        elif words[i+1][0] == "B":
                            b = float(words[i+1][1:])

                    point = Point3D((x,y,z,a,b))
                    point = rotationMatrix(BROTATIONVECTOR,OFFSTEFROMCENTERB,-b) * point
                    point = rotationMatrix(AROTATIONVECTOR,OFFSTEFROMCENTERA,-a) * point
                    self.points.append(point)

    def offset(self, p):
        for pt in self.points:
            pt.offset(p)
    
    def rotate(self, M):
        for pt in self.points:
            pt.rotate(M)       

    def doLine(self): 
        if self.line < len(self.buff):         
            words=self.buff[self.line].decode('UTF-8').split()
            if len(words)>0:
                if words[0]=='G0' or words[0]=='G1':
                    x,y,z,a,b,f = 'a','a','a','a','a','a'
                    if words[0]=='G0':
                        f = 0
                    for i in range(len(words)-1):
                        if words[i+1][0] == "X":
                            x = float(words[i+1][1:])
                        elif words[i+1][0] == "Y":
                            y = float(words[i+1][1:])
                        elif words[i+1][0] == "Z":
                            z = float(words[i+1][1:])
                        elif words[i+1][0] == "A":
                            a = float(words[i+1][1:])
                        elif words[i+1][0] == "B":
                            b = float(words[i+1][1:])
                        elif words[i+1][0] == "F":
                            f = float(words[i+1][1:])
                        else:
                            print("not understood: G + " + str(words[i+1][0]) +" "+ str(words[i+1][1:]))
                    
                    self.out.pos54(x,y,z,a,b,f)

                else:
                    pass # TODO re put that
                    #print("Gcode not understood: " + str(words))
            self.line += 1 
            return 0
        else:
            return 1


def main():
    reader = GcodeReader(0)
    reader.readfile("assets/Sans titre.Groupe1 [Contour1].nc")
    while not reader.doLine():
        pass



if __name__ == '__main__':
    main()