import os
import struct
import time

from Utils3D import *
from Gcode import GcodeReader

from utils import *
from machineConst import *

ROTATIONCENTER = Point3D((263,815.2,-270)) #(y,z,x,)  #from stl origin
PATHOFFSET = Point3D((0,-76,0))


class Machine (Assembly):
    
    def __init__(self):
        super().__init__()

        self.rotationAnchor = Point3D((0,0,200))

        self.pathOffset = Point3D((PATHOFFSET.z,PATHOFFSET.x,PATHOFFSET.y))

        self.reader = GcodeReader(self)
        #self.reader.readfile("assets/Sans titre.Groupe1 [Contour1].nc")
        self.reader.readfile("assets/finition.nc")
        #self.reader.readfile("assets/test.nc")
        self.reader.rotate(rotationMatrix(self.v1,Point3D((0,0,0)), math.pi/2))
        self.reader.rotate(rotationMatrix(self.v2,Point3D((0,0,0)), -math.pi/2)  ) 
        self.reader.offset(ROTATIONCENTER + PATHOFFSET) 
        
        self.name = "Machine Assembly"
        self.bati=Object3D()
        self.bati.load_stl(os.path.abspath('')+'/assets/simu-bati.STL')
        self.bati.setColor((0,1,0))
        self.addObject(self.bati)

        self.broche=Assembly()
        self.broche.name = "broche"
        brochePart=Object3D()
        brochePart.load_stl(os.path.abspath('')+'/assets/simu-X.STL')
        brochePart.setColor((1,0,0))
        self.broche.addObject(brochePart)
        super().addObject(self.broche)

        outilPart=Object3D()
        outilPart.name = "outil"
        outilPart.load_stl(os.path.abspath('')+'/assets/outil_6.STL')
        outilPart.setColor((1,1,1))
        self.broche.addObject(outilPart)

        self.berceau=Assembly()
        self.berceau.name = "berceau"
        berceauPart=Object3D()
        berceauPart.load_stl(os.path.abspath('')+'/assets/simu-berceau.STL')
        berceauPart.setColor((1,0,0))
        self.berceau.addObject(berceauPart)
        super().addObject(self.berceau)

        self.bAxis=Assembly()
        bAxisPart=Object3D()
        bAxisPart.load_stl(os.path.abspath('')+'/assets/simu-B.STL')
        bAxisPart.setColor((0,1,0))
        self.bAxis.addObject(bAxisPart)
        self.bAxis.rotationAnchor = ROTATIONCENTER #815.2,270
        self.bAxis.v1 = Point3D((1,0,0))
        self.berceau.addObject(self.bAxis)
        
        self.aAxis=Assembly()
        aAxisPart=Object3D()
        aAxisPart.load_stl(os.path.abspath('')+'/assets/simu-A.STL')
        aAxisPart.setColor((0,0,1))
        self.aAxis.rotationAnchor = ROTATIONCENTER #815.2,270
        self.aAxis.v1 = Point3D((0,1,0))
        self.aAxis.addObject(aAxisPart)
        self.aAxis.addObject(self.reader)

        self.bAxis.addObject(self.aAxis)

        self.origine = Point3D((ORIGINEX,ORIGINEY,ORIGINEZ))
        self.center()

        self.rotate(rotationMatrix(self.v1,self.rotationAnchor, math.pi/2))
        self.rotate(rotationMatrix(self.v3,self.rotationAnchor, math.pi/2))
        self.rotate(rotationMatrix(self.v3,self.rotationAnchor, math.pi/6))

        self.x, self.y, self.z, self.a, self.b = 0,0,0,0,0

        self.dirX = True # will be deprecated, only for cinetest
        self.dirY = True
        self.dirZ = True
        self.dirA = True
        self.dirB = True

        self.g54 = G54

        self.state = state.READY
        self.maxSpeed = 1000
        self.currentSpeed = self.maxSpeed

        self.trajectory = [Point3D((0,0,0,0,0)),Point3D((0,0,0,0,0)),0,0]

    def run(self):
        now = round(time.time()*1000) - self.trajectory[2]
        if(now > self.trajectory[3]):
            self.state = state.READY
        elif(not self.trajectory[3]==0):
            if (now/self.trajectory[3] >= 1):
                self.pos(self.trajectory[0] + self.trajectory[1] )
            else:
                self.pos(self.trajectory[0] + self.trajectory[1] * (now/self.trajectory[3]) )

    def pos(self,point):
        self.X(point.x)
        self.Y(point.y)
        self.Z(point.z)
        self.A(point.a)
        self.B(point.b)


    def pos54(self,x,y,z,a,b,f=0):
        self.trajectory[0] = Point3D((self.x,self.y,self.z,self.a,self.b))
        self.trajectory[1] = Point3D((self.x,self.y,self.z,self.a,self.b))

        if (type(x) == int or type(x) == float):
            self.trajectory[1].x=x+self.g54[0]
        if (type(y) == int or type(y) == float):
            self.trajectory[1].y=y+self.g54[1]
        if (type(z) == int or type(z) == float):
            self.trajectory[1].z=z+self.g54[2]
        if (type(a) == int or type(a) == float):
            self.trajectory[1].a=a+self.g54[3]
        if (type(b) == int or type(b) == float):
            self.trajectory[1].b=b+self.g54[4]
        if (type(f) == int or type(f) == float):
            self.currentSpeed = f
            if self.currentSpeed <= 0:
                self.currentSpeed = self.maxSpeed

        self.trajectory[1] = self.trajectory[1]-self.trajectory[0]
        self.trajectory[2] = round(time.time()*1000)
        self.trajectory[3] = (self.trajectory[1].norm()*6000)/self.currentSpeed #TODO should be 60000
        
        self.state = state.MOVING
  
    def X(self, x):
        dist = self.x - x
        if abs(dist) > 0.001:
            self.berceau.offset(self.v1*dist)
            self.x = x
    
    def Y(self, y):
        dist = y - self.y
        if abs(dist) > 0.001:
            self.broche.offset(self.v3*dist)
            self.y = y

    def Z(self, z):
        dist = z - self.z
        if abs(dist) > 0.001:
            self.berceau.offset(self.v2*dist)
            self.z = z

    def A(self, a):
        if abs(a - self.a) > 0.001:
            self.aAxis.rotateV1(a - self.a) 
            self.a = a

    def B(self, b):
        if abs(b - self.b) > 0.001:
            self.bAxis.rotateV1(b - self.b) 
            self.b = b


def cinetest(machine):
    if(machine.dirX):
        machine.X(machine.x-1)
        if(machine.x < -500):
            machine.dirX = False
    else:
        machine.X(machine.x+1)
        if(machine.x > 0):
            machine.dirX = True
    if(machine.dirY):
        machine.Y(machine.y+1)
        if(machine.y > 500):
            machine.dirY = False
    else:
        machine.Y(machine.y-1)
        if(machine.y < 0):
            machine.dirY = True
    if(machine.dirZ):
        #machine.Z(machine.z-1)
        if(machine.z < -500):
            machine.dirZ = False
    else:
        #machine.Z(machine.z+1)
        if(machine.z > 0):
            machine.dirZ = True

    #machine.B(machine.b+0.05)
    #machine.A(machine.a+0.05)
