from machineConst import *

MINDIST = 10


class NclReader:

    def translate(self, inFilename, outFilename = ""):
        self.outFile = open(outFilename,'w')


        fp=open(inFilename,'rb')

        speed = 0
        waitForVect = False
        x,y,z,i,j,k = 0,0,0,0,0,0
        prevPoint = Point3D((0,0,0))
        for line in fp.readlines():
            words=line.decode('UTF-8').split()
            if len(words)>0:
                if words[0]== "RAPID":
                    speed = 0
                elif words[0]== "FEDRAT":
                    speed = float(words[2][:-1])
                elif words[0]== "GOTO":
                    x = float(words[2][:-1])
                    y = float(words[3][:-1])
                    z = float(words[4][:-1])
                    if((Point3D((x,y,z))-prevPoint).norm() > MINDIST):
                        waitForVect = True
                elif waitForVect:
                    i = float(words[0][:-1])
                    j = float(words[1][:-1])
                    k = float(words[2][:-1])
                    waitForVect = False
                    prevPoint = Point3D((x,y,z))

                    a,b = self.convertIJK(i,j,k)

                    self.outPoint(self.convert(x,y,z,a,b), speed)

        fp.close()

    def convertIJK(self,i,j,k):
        point = Point3D((i,j,k))
        #point.normalize()

        a = math.asin(point.y) - math.pi/2
        b = math.asin(point.x)
        return a,b

    def convert(self, x,y,z,a,b): 
        point = Point3D((x,y,z,a,b))
        point = rotationMatrix(AROTATIONVECTOR,OFFSTEFROMCENTERA,a) * point
        point = rotationMatrix(BROTATIONVECTOR,OFFSTEFROMCENTERB,b) * point
        return point
    
    def outPoint(self, point, f):
        msg  = " X" + str(point.x)
        msg += " Y" + str(point.y)
        msg += " Z" + str(point.z)
        msg += " A" + str(point.a)
        msg += " B" + str(point.b)

        if f == 0:
            self.outFile.write("G0" + msg + "\n")
        else:
            self.outFile.write("G1" + msg + " F" + str(f) + "\n")



        


def main():
    reader = NclReader()
    reader.translate("assets/finition.ncl","assets/finition.nc")



if __name__ == '__main__':
    main()