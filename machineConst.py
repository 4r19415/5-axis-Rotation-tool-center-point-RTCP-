from Utils3D import Point3D
from Utils3D import rotationMatrix
import math

OFFSTEFROMCENTERA = Point3D((0,0,0))
OFFSTEFROMCENTERB = Point3D((0,0,-76)) #-76
AROTATIONVECTOR = Point3D((0,0,-1))
BROTATIONVECTOR = Point3D((1,0,0))
G54 = [303.8,382,-402.2,math.pi/2,0]