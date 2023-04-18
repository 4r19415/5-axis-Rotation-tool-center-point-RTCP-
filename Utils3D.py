import os, math
import struct

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from itertools import chain

from utils import *

class rotationMatrix():

    def __init__(self,vector,anchor,a):
        if(type(vector)==int):
            self.M = [[1,0,0],[0,1,0],[0,0,1]]
            self.anchor = Point3D((0,0,0))
            self.vector = 0
        else:
            c,s=math.cos(a),math.sin(a)
            nC = 1-c
            self.vector = vector
            self.vector.normalize()
            self.anchor = anchor

            self.M = [[c + (self.vector.x**2*nC) , 
                                (self.vector.x*self.vector.y*nC) - (self.vector.z*s) ,
                                        (self.vector.x*self.vector.z*nC) + (self.vector.y*s)],

                    [(self.vector.x*self.vector.y*nC) + (self.vector.z*s),
                                c + (self.vector.y**2*nC),
                                        (self.vector.y*self.vector.z*nC) - (self.vector.x*s)],

                    [(self.vector.x*self.vector.z*nC) - (self.vector.y*s),
                                (self.vector.y*self.vector.z*nC) + (self.vector.x*s),
                                        c + (self.vector.z**2*nC),]]

        # self.M = [[1,0,0],[0,c,-s],[0,s,c]] # around x
        # self.M = [[c,0,s],[0,1,0],[-s,0,c]] # around y
        # self.M = [[c,-s,0],[s,c,0],[0,0,1]] # around Z

    def __str__(self):
        msg = "[ %f %f %f\n  %f %f %f\n  %f %f %f ]\n" % (self.M[0][0],self.M[0][1],self.M[0][2],
                                                          self.M[1][0],self.M[1][1],self.M[1][2],
                                                          self.M[2][0],self.M[2][1],self.M[2][2])
        msg += bcolors.HEADER +  str( self.anchor ) + bcolors.ENDC + "\n"
        msg += bcolors.WARNING +  str( self.vector ) + bcolors.ENDC
        return msg
    
    def __rmul__(self, other):
        print("rotationMatrix __rmul__  not suported !")
    
    def unitMul(self, other):
        if(type(other) == Point3D):

            x = other.x * self.M[0][0] + other.y * self.M[0][1] + other.z * self.M[0][2]
            y = other.x * self.M[1][0] + other.y * self.M[1][1] + other.z * self.M[1][2]
            z = other.x * self.M[2][0] + other.y * self.M[2][1] + other.z * self.M[2][2]
            newPoint = Point3D((x,y,z,other.a,other.b))
            return newPoint

        else:
            print("rotationMatrix unitMul(" + str(type(other)) + ") not suported !")

    def __mul__(self, other):
        if(type(other) == Point3D):
            newPoint = self.unitMul(other - self.anchor) + self.anchor
            return newPoint
        
        elif(type(other) == rotationMatrix):
            #TODO, test if they have the same anchor
            p = rotationMatrix(0,0,0)
            p.anchor = self.anchor

            for i in range(3):
                for j in range(3):
                    p.M[i][j] = 0
                    for k in range(3):
                        p.M[i][j] += self.M[i][k]*other.M[k][j]

            return p

        elif(type(other) == Triangle3D):
            p1 = self *other.points[0]
            p2 = self *other.points[1]
            p3 = self *other.points[2]
            newTri = Triangle3D((p1.x,p1.y,p1.z),
                                (p2.x,p2.y,p2.z),
                                (p3.x,p3.y,p3.z),
                                other.color)
            return newTri

        else:
            print("rotationMatrix x " + str(type(other)) + " not suported !")

    def transpose(self):
        p = rotationMatrix(0,0,0)
        p.anchor = self.anchor
        for i in range(3):
                for j in range(3):
                    p.M[i][j] = self.M[j][i]
        return p
    
#class for a 3d point
class Point3D:
    def __init__(self,p):
        self.point_size=0.5
        self.x=p[0]
        self.y=p[1]
        self.z=p[2]
        self.a=0
        self.b=0
        if(len(p)>=5):
            self.a=p[3]
            self.b=p[4]

    def __add__(self,other):
        return  Point3D((self.x+other.x, self.y+other.y, self.z+other.z,
                         self.a+other.a, self.b+other.b))
    
    def __neg__(self):
        return Point3D( (-self.x, -self.y, -self.z, -self.a, -self.b) )
    
    def __sub__(self,other):
        return self + (-other)
    
    def __str__(self):
        if ((self.a == 0) & (self.b == 0)):
            return "< %f %f %f >" % (self.x,self.y,self.z)
        else:
            return "< %f %f %f %f %f >" % (self.x,self.y,self.z,self.a,self.b)
      
    def glvertex(self):
        glVertex3f(self.x,self.y,self.z)

    def norm(self):
        return math.sqrt( self.x*self.x+ self.y*self.y+ self.z*self.z)
    
    def scale(self,v):
        self.x*=v; self.y*=v; self.z*=v; self.a*=v; self.b*=v

    def __mul__(self, other):
        if(type(other) == int or type(other) == float):
            return Point3D((other*self.x,other*self.y,other*self.z,other*self.a,other*self.b))
        else:
            print("Point3D x " + str(type(other)) + " not suported")

    def normalize(self):
        self.scale(1/self.norm())
    
    def offset(self, p):
        self.x+=p.x
        self.y+=p.y
        self.z+=p.z
    
    def rotate(self, M):
        tempPt = M*self
        self.x,self.y,self.z = tempPt.x, tempPt.y, tempPt.z

#class for a 3d face on a model
class Triangle3D:
    points=None

    def __init__(self,p1,p2,p3,c=(0,0,0)):
        #3 points of the triangle
        self.points=Point3D(p1),Point3D(p2),Point3D(p3)
        self.color=c

    def __str__(self):
        msg = str(self.points[0]) +" "+ str(self.points[1]) +" "+ str(self.points[2])
        return  msg

    def offset(self, p):
        for cP in self.points:
            cP.offset(p)
    
    def rotate(self, M):
        for cP in self.points:
            cP.rotate(M)

class Assembly:
    def __init__(self):
        self.objects = []
        self.origine = Point3D((0,0,0))
        self.name = ""
        self.rotationAnchor = Point3D((0,0,0))

        self.v1 = Point3D((1,0,0))
        self.v2 = Point3D((0,1,0))
        self.v3 = Point3D((0,0,1))

        self.rotation = rotationMatrix(0,0,0)
        self.projection = rotationMatrix(0,0,0)
        self.unprojection = rotationMatrix(0,0,0)

    def addObject(self,newObject):
        self.objects.append(newObject)
    
    def offset(self, p):
        for obj in self.objects:
            obj.offset(p)
        self.origine = self.origine + p
        self.rotationAnchor = self.rotationAnchor + p

    def center(self):
        self.offset(-self.origine)

    def rotateV1(self, a):
        m = rotationMatrix(self.v1, self.rotationAnchor, a)

        self.rotate(m)

    
    def rotate(self, M):
        for obj in self.objects:
            obj.rotate(M)
        self.origine.rotate(M)
        self.rotationAnchor.rotate(M)
        self.v1 = M.unitMul(self.v1)
        self.v2 = M.unitMul(self.v2)
        self.v3 = M.unitMul(self.v3)

    def get_triangles(self):
        for obj in self.objects:
            if ((type(obj) == Assembly) or (type(obj) == Object3D)):
                for tri in obj.get_triangles():
                    yield tri

    
    def __str__ (self):
        msg = "Assembly: " 
        msg += self.name + " " + str(self.origine)
        for obj in self.objects:
            msg += "\n  |-- "
            msg += str(obj)
        return msg


class Object3D:

    def __init__(self):
        self.triangles=[]
        self.origine = Point3D((0,0,0))
        self.name = ""
      
    #return the faces of the triangles
    def get_triangles(self):
        if self.triangles:
            for face in self.triangles:
                yield face

    def setColor(self,c):
        if self.triangles:
            for face in self.triangles:
                face.color = c
  
    #load stl file detects if the file is a text file or binary file
    def load_stl(self,filename):
        #read start of file to determine if its a binay stl file or a ascii stl file
        fp=open(filename,'rb')
        h=fp.read(80)
        type=h[0:5]
        fp.close()

        self.name = filename

        if type=='solid':
            #print ("reading text file"+str(filename))
            self.load_text_stl(filename)
        else:
            #print ("reading binary stl file "+str(filename,))
            self.load_binary_stl(filename)
  
    #read text stl match keywords to grab the points to build the triangles
    def load_text_stl(self,filename):
        fp=open(filename,'r')

        for line in fp.readlines():
            words=line.split()
            if len(words)>0:
                if words[0]=='solid':
                    self.name=words[1]

                if words[0]=='facet':
                    center=[0.0,0.0,0.0]
                    triangle=[]
                    normal=(eval(words[2]),eval(words[3]),eval(words[4]))
                  
                if words[0]=='vertex':
                    triangle.append((eval(words[1]),eval(words[2]),eval(words[3])))
                  
                  
                if words[0]=='endloop':
                    #make sure we got the correct number of values before storing
                    if len(triangle)==3:
                        self.triangles.append(Triangle3D(triangle[0],triangle[1],triangle[2],normal))
        fp.close()

    #load binary stl file check wikipedia for the binary layout of the file
    #we use the struct library to read in and convert binary data into a format we can use
    def load_binary_stl(self,filename):
        fp=open(filename,'rb')
        h=fp.read(80)

        l=struct.unpack('I',fp.read(4))[0]
        count=0
        while True:
            try:
                p=fp.read(12)
                if len(p)==12:
                    n=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]
                  
                p=fp.read(12)
                if len(p)==12:
                    p1=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                p=fp.read(12)
                if len(p)==12:
                    p2=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                p=fp.read(12)
                if len(p)==12:
                    p3=struct.unpack('f',p[0:4])[0],struct.unpack('f',p[4:8])[0],struct.unpack('f',p[8:12])[0]

                new_tri=(n,p1,p2,p3)

                if len(new_tri)==4:
                    tri=Triangle3D(p1,p2,p3,n)
                    self.triangles.append(tri)
                count+=1
                fp.read(2)

                if len(p)==0:
                    break
            except EOFError:
                break
        fp.close()

    def offset(self, p):
        for tri in self.triangles:
            tri.offset(p)
        self.origine = self.origine + p

    def center(self):
        self.offset(-self.origine)
    
    def rotate(self, M):
        for tri in self.triangles:
            tri.rotate(M)
        self.origine.rotate(M)

    def strTriangles(self):
        msg = ""
        for tri in self.triangles:
            msg += str(tri)
        return  msg

    def __str__(self):
        return("object : " + self.name + str(self.origine) +
                " " + str(len(self.triangles)))