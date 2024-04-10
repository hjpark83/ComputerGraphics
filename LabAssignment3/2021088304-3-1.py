import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

global gComposedM

gComposedM = np.array([[1., .0, .0],
                       [.0, 1., .0],
                       [.0, .0, 1.]])

def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw coordinates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv((T @ np.array([.0, .5, 1.]))[:-1])
    glVertex2fv((T @ np.array([.0, .0, 1.]))[:-1])
    glVertex2fv((T @ np.array([.5, .0, 1.]))[:-1])
    glEnd()

def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 1., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0]))
    glVertex3fv(np.array([0., 0., 1.]))
    glEnd()

def key_callback(window, key, scancode, action, mods):
    global gComposedM
    if key == glfw.KEY_Q and action == glfw.PRESS:
        # Translate by -0.1 in x direction w.r.t global coordinate
        newM = np.array([[1., 0., -0.1],
                         [0., 1., 0.],
                         [0., 0., 1.]])
        gComposedM = newM @ gComposedM
        
    elif key == glfw.KEY_E and action == glfw.PRESS:
        # Translate by 0.1 in x direction w.r.t global coordinate
        newM = np.array([[1., 0., 0.1],
                         [0., 1., 0.],
                         [0., 0., 1.]])
        gComposedM = newM @ gComposedM
        
    elif key == glfw.KEY_A and action == glfw.PRESS:
        # Rotate by 10 degrees C.C.W w.r.t local coordinate
        newM = np.array([[np.cos(np.radians(10)), -np.sin(np.radians(10)), .0],
                         [np.sin(np.radians(10)), np.cos(np.radians(10)), .0],
                         [.0, .0, 1.]])
        gComposedM = gComposedM @ newM
        
    elif key == glfw.KEY_D and action == glfw.PRESS:
        # Rotate by 10 degrees C.W w.r.t local coordinate
        newM = np.array([[np.cos(-np.radians(10)), -np.sin(-np.radians(10)), .0],
                         [np.sin(-np.radians(10)), np.cos(-np.radians(10)), .0],
                         [.0, .0, 1.]])
        gComposedM = gComposedM @ newM
        
    elif key == glfw.KEY_1 and action == glfw.PRESS:
        # Reset the tringle with identity matrix
        newM = np.array([[1., 0., 0.],
                         [0., 1., 0.],
                         [0., 0., 1.]])
        gComposedM = newM


def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, '2021088304-3-1', None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(gComposedM)
        drawFrame()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == '__main__':
    main()