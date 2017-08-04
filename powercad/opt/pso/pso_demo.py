'''
Created on Sep 5, 2012

@author: bxs003
'''

from math import fabs, sin, pow

import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.extensions import *

ESCAPE = '\x1b'

window = 0

iter_count = 0
frame = 0
rotate_val = 0.0
tex_id = 0

# up, down, right, left
arrow_keys_state = [False, False, False, False]
rotx = 0.0
roty = 0.0

particle_hist = None

def InitGL(Width, Height):
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glPointSize(4.0)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    
    if hasGLExtension("MULTISAMPLE_ARB"):
        print "True"
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 1000.0)

    glMatrixMode(GL_MODELVIEW)

def ReSizeGLScene(Width, Height):
    if Height == 0:
        Height = 1

    glViewport(0, 0, Width, Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)

def DrawGLScene():
    global rotate_val, iter_count, frame
    global arrow_keys_state, rotx, roty
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if arrow_keys_state[0]:
        rotx += 2.0
    if arrow_keys_state[1]:
        rotx -= 2.0
    if arrow_keys_state[2]:
        roty += 2.0
    if arrow_keys_state[3]:
        roty -= 2.0
    
    glPushMatrix()
    glTranslate(-10.0, 0, -80.0)
    glRotate(roty, 0, 1, 0)
    glRotate(rotx, 1, 0, 0)
    
    render_grid()
    
    glBegin(GL_POINTS)
    for part in particle_hist[iter_count]:
        pos = part[0]
        fit = part[2]
        glColor3f(1.0, fit/10.0, 0.0)
        glVertex3f(pos[0], fit, pos[1])
    glEnd()
    glPopMatrix()
    
    glutSwapBuffers()
    
    frame += 1
    if frame >= 5:
        iter_count += 1
        frame = 0
        if iter_count >= len(particle_hist):
            iter_count = 0
    
    rotate_val += 0.1
    if rotate_val > 360:
        rotate_val = 0
        
def render_grid():
    xv = numpy.linspace(0.0, 20.0, 50)
    yv = numpy.linspace(0.0, 20.0, 50)
    
    glBegin(GL_LINES)
    
    for xi in xrange(len(xv)):
        for yi in xrange(len(yv)):
            x1 = xv[xi]
            y1 = yv[yi]
            # Draw Y lines
            if yi+1 < len(yv):
                z1 = func(x1, y1)
                
                glColor3f(0.0, z1/10.0, 0.5)
                glVertex3f(x1, z1, y1)
            
                y2 = yv[yi+1]
                z2 = func(x1, y2)
                glColor3f(0.0, z2/10.0, 0.5)
                glVertex3f(x1, z2, y2)
            
            # Draw X lines
            if xi+1 < len(xv):
                x2 = xv[xi+1]
                z3 = func(x2, y1)
                glColor3f(0.0, z1/10.0, 0.5)
                #glVertex3f(x1, z1, y1)
                glColor3f(0.0, z3/10.0, 0.5)
                #glVertex3f(x2, z3, y1)
                
    glEnd()
    
def func(x, y):
    return ((fabs(sin(x))+1.0)*pow((x-10),2) + (fabs(sin(y))+1.0)*pow(y-10,2))/35.0

def keyPressed(code, x, y):
    if code == ESCAPE:
        sys.exit()
        
def special_key_pressed(key, x, y):
    global arrow_keys_state
    if key == GLUT_KEY_UP:
        arrow_keys_state[0] = True
    elif key == GLUT_KEY_DOWN:
        arrow_keys_state[1] = True
    elif key == GLUT_KEY_RIGHT:
        arrow_keys_state[2] = True
    elif key == GLUT_KEY_LEFT:
        arrow_keys_state[3] = True
    
def special_key_released(key, x, y):
    global arrow_keys_state
    if key == GLUT_KEY_UP:
        arrow_keys_state[0] = False
    elif key == GLUT_KEY_DOWN:
        arrow_keys_state[1] = False
    elif key == GLUT_KEY_RIGHT:
        arrow_keys_state[2] = False
    elif key == GLUT_KEY_LEFT:
        arrow_keys_state[3] = False

def main():
    global particle_hist
    
    from powercad.opt.pso.pso import ParticleSwarm
    from powercad.opt.pso import Design2DConfig, Design2D
    import powercad.opt.pso.pso_config as pso_config
    
    config = Design2DConfig()
    opt = ParticleSwarm(Design2D, config, pso_config)
    opt.setup()
    opt.run()
    particle_hist = opt.particle_hist
    
    global window
    glutInit(sys.argv)

    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1024, 768)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("GLwindow")
    glutDisplayFunc(DrawGLScene)
    #glutFullScreen()
    glutIdleFunc(DrawGLScene)   
    glutReshapeFunc(ReSizeGLScene)
    glutKeyboardFunc(keyPressed)
    glutSpecialFunc(special_key_pressed)
    glutSpecialUpFunc(special_key_released)
    InitGL(1024, 768)

    # Begin Main Loop
    glutMainLoop()

if __name__ == '__main__':
    print "Hit ESC key to quit."
    main()
