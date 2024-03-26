import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

x = GL_LINE_STRIP

def render(x):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    
    glBegin(x)
    glColor3ub(255, 255, 255) # 흰색
    
    for i in range(13):
        rad = np.radians(i*30) # 360 / 12 = 30 (12-sided polygon)
        R = np.array([[np.cos(rad), -np.sin(rad)],
                      [np.sin(rad), np.cos(rad)]])
        glVertex2fv(R@np.array([1., 0.]))
    glEnd()


def keyCallback(window, key, scancode, action, mods):
    global x
    if action == glfw.PRESS:
        if key == glfw.KEY_1:
            x = GL_POINTS
        elif key == glfw.KEY_2:
            x = GL_LINES
        elif key == glfw.KEY_3:
            x = GL_LINE_STRIP
        elif key == glfw.KEY_4:
            x = GL_LINE_LOOP
        elif key == glfw.KEY_5:
            x = GL_TRIANGLES
        elif key == glfw.KEY_6:
            x = GL_TRIANGLE_STRIP
        elif key == glfw.KEY_7:
            x = GL_TRIANGLE_FAN
        elif key == glfw.KEY_8:
            x = GL_QUADS
        elif key == glfw.KEY_9:
            x = GL_QUAD_STRIP
        elif key == glfw.KEY_0:
            x = GL_POLYGON


def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, '2021088304-2-1', None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    glfw.set_key_callback(window, keyCallback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render(x)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == '__main__':
    main()