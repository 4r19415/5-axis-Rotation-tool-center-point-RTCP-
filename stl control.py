# by Oliver Marks
#from https://www.linux.com/training-tutorials/python-stl-model-loading-and-display-opengl/cd 
import os
import struct
import time


from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *

from Utils3D import *
from utils import *
from machine import *


class draw_scene:

    objects = []

    def __init__(self,style=1):
        self.init_shading()

    def addObject(self, object):
        self.objects.append(object)

    #solid model with a light / shading
    def init_shading(self):
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH) 
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
      
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)   
        glLight(GL_LIGHT0, GL_POSITION,  (-1, -1, 0, 0))     
        #glLight(GL_LIGHT0,   GL_AMBIENT,  (0.5, 0.5, 0.5, 0))    
        glMatrixMode(GL_MODELVIEW)

        pygame.display.set_caption('5 Axis simu')
      
    def resize(self,width, height):
        if height==0:
            height=1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0*width/height, 0.1, 5000.0)
        #gluLookAt(0.0,0.0,45.0,0,0,0,0,40.0,0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
      
        glTranslatef(0,0, -1000)
        glBegin(GL_TRIANGLES)
        for obj in self.objects:
            for tri in obj.get_triangles():
                glColor3f(tri.color[0],tri.color[1],tri.color[2])
                p1 = tri.points[0]
                p2 = tri.points[1]
                p3 = tri.points[2]
                a1 = p2 - p3
                a2 = p1 - p3
                norm = (a1.y*a2.z-a2.y*a1.z) , (a1.z*a2.x)-(a2.z*a1.x) , (a1.x*a2.y)-(a2.x*a1.y)

                glNormal3f(norm[0],norm[1],norm[2])
                glVertex3f(p1.x,p1.y,p1.z)
                glVertex3f(p2.x,p2.y,p2.z)
                glVertex3f(p3.x,p3.y,p3.z)
        glEnd()

        if type(obj) == Machine:
            glBegin(GL_LINES)
            glColor3f(1,1,1)
            for i in range(len(obj.reader.points)-1):
                glVertex3f(obj.reader.points[i-1].x,
                            obj.reader.points[i-1].y,
                            obj.reader.points[i-1].z)
                glVertex3f(obj.reader.points[i].x,
                            obj.reader.points[i].y,
                            obj.reader.points[i].z)
                
            glEnd()

        

#main program loop
def main():
    #initalize pygame
    pygame.init()
    pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT), OPENGL|DOUBLEBUF)

    #setup the open gl scene
    scene=draw_scene()
    scene.resize(WINDOWWIDTH,WINDOWHEIGHT)

    machine = Machine()
    scene.addObject(machine)
    machine.origine = Point3D((0,0,0))

     
    frames = 0
    ticks = pygame.time.get_ticks()
    translateFrame = False
    rotateFrame = False
    prevLeftClick = 0
    prevRightClick = 0
    
    runTimeMchine = 0 #now = round(time.time()*1000)
    runTimeRender = 0
    runTimeEvent = 0


    while 1:
        prev = round(time.time()*1000)
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:            
                if((round(time.time()*1000) - prevLeftClick) < DOUBLE_CLICK_DELAY):
                    #print("double click left")
                    machine.center()
                else:
                    prevLeftClick = round(time.time()*1000)
                rotateFrame = True
                rotateStartX, rotateStartY = event.pos
                rotateAnchorX, rotateAnchorY = event.pos

            elif event.button == 3:
                if((round(time.time()*1000) - prevRightClick) < DOUBLE_CLICK_DELAY):
                    pass
                    #print("double click right")
                else:
                    prevRightClick = round(time.time()*1000)            
                translateFrame = True
                translateStartX, translateStartY = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:            
                rotateFrame = False
            elif event.button == 3:      
                translateFrame = False

        elif event.type == pygame.MOUSEMOTION:
            if rotateFrame:
                mouse_x, mouse_y = event.pos

                machine.rotate(rotationMatrix(Point3D((0,1,0)),
                                             machine.rotationAnchor,
                                             ROTATION_GAIN*(rotateStartX-mouse_x)))
 
                machine.rotate(rotationMatrix(Point3D((1,0,0)),
                                             machine.rotationAnchor,
                                             ROTATION_GAIN*(rotateStartY-mouse_y)))

                rotateStartX, rotateStartY = event.pos

            elif translateFrame:
                mouse_x, mouse_y = event.pos
                machine.offset(Point3D(((mouse_x - translateStartX)* SLIDING_GAIN,
                                        (translateStartY - mouse_y)* SLIDING_GAIN,
                                        0)))

                translateStartX, translateStartY = event.pos


        elif event.type == pygame.MOUSEWHEEL:
            machine.offset(machine.unprojection.unitMul(Point3D((0,0,event.y*ZOOM_GAIN))))

      
        #draw the scene
        #cinetest(machine)
        runTimeEvent += round(time.time()*1000) - prev
        prev = round(time.time()*1000)
        if(machine.state == state.READY):
            machine.reader.doLine()
            pass
            
        machine.run()
        runTimeMchine += round(time.time()*1000) - prev

        prev = round(time.time()*1000)
        scene.draw()
        pygame.display.flip()
        runTimeRender += round(time.time()*1000) - prev

        frames = frames+1

    print ("fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    print ("Event time:  %d ms" % (runTimeEvent/frames))
    print ("Machine run time:  %d ms" % (runTimeMchine/frames))
    print ("Render time:  %d ms" % (runTimeRender/frames))

    


if __name__ == '__main__':
    main()

