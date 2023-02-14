### Guilherme de Oliveira Cherobim
### 8531139

from cmath import cos
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
window = glfw.create_window(720, 600, "Puzzle", None, None)
glfw.make_context_current(window)

vertex_code = """
        attribute vec2 position;
        uniform mat4 mat_transformation;
        void main(){
            gl_Position = mat_transformation * vec4(position,0.0,1.0);
        }
        """

fragment_code = """
        uniform vec4 color;
        void main(){
            gl_FragColor = color;
        }
        """

# Request a program and shader slots from GPU
program  = glCreateProgram()
vertex   = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

# Set shaders source
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

# Compile shaders
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")
    
glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")
    
# Attach shader objects to the program
glAttachShader(program, vertex)
glAttachShader(program, fragment)

# Build program
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')
    
# Make program the default program
glUseProgram(program)

# Definindo os vértices de cada objeto
estrela = [
    (0.0, 0.0),
    (0.0, 0.5),
    (0.125, 0.125),
    (0.5, 0.0),
    (0.125, -0.125),
    (0.0, -0.5),
    (-0.125, -0.125),
    (-0.5, 0.0),
    (-0.125, 0.125),
    (0.0, 0.5)
]

diamante = [
    (0.0, -0.5),
    (-0.5, 0.25),
    (-0.25, 0.55),
    (0.25, 0.55),
    (0.5, 0.25)
]

balao = [
    (0.0, -0.5),
    (-0.3, 0.25),
    (-0.25, 0.5),
    (0.0, 0.6),
    (0.25, 0.5),
    (0.3, 0.25),
    (0.0, -0.5),
    (-0.25, -1)
]

pilar = [
    (-0.25, 0.5),
    (-0.25, 0.55),
    (0.25, 0.5),
    (0.25, 0.55),
    (0.1, 0.5),
    (0.1, -0.5),
    (-0.1, 0.5),
    (-0.1, -0.5),
    (-0.25, -0.5),
    (-0.25, -0.55),
    (0.25, -0.5),
    (0.25, -0.55)
]

xis = [
    (0, 0),
    (0.5, 0.45),
    (0.5, 0.5),
    (0.45, 0.5),
    (0, 0.05),
    (-0.45, 0.5),
    (-0.5, 0.5),
    (-0.5, 0.45),
    (-0.05, 0),
    (-0.5, -0.45),
    (-0.5, -0.5),
    (-0.45, -0.5),
    (0, -0.05),
    (0.45, -0.5),
    (0.5, -0.5),
    (0.5, -0.45),
    (0.05, 0),
    (0.5, 0.45)
]

total = np.concatenate((estrela, xis, balao, diamante, pilar))

# preparando espaço para os vértices usando 2 coordenadas (x,y)
vertices = np.zeros(len(total), [("position", np.float32, 2)])

# preenchendo as coordenadas de cada vértice
vertices['position'] = total

# Request a buffer slot from GPU
buffer = glGenBuffers(1)
# Make this buffer the default one
glBindBuffer(GL_ARRAY_BUFFER, buffer)

# Upload data
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)

# Bind the position attribute
# --------------------------------------
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)

loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)

glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)

loc_color = glGetUniformLocation(program, "color")
R = 1.0
G = 0.0
B = 0.0


def key_event(window,key,scancode,action,mods):
    global t_x, t_y, tr, s_x, s_y, r_x, r_y

    if key == 258:
        tr += 1 # incremento na variável de operações
    if   tr%3 == 0:
            if key == 265: t_y += 0.01 #cima
            if key == 264: t_y -= 0.01 #baixo
            if key == 263: t_x -= 0.01 #esquerda
            if key == 262: t_x += 0.01 #direita
    elif tr%3 == 1:
            if key == 265: s_y += 0.01 #cima
            if key == 264: s_y -= 0.01 #baixo
            if key == 263: s_x -= 0.01 #esquerda
            if key == 262: s_x += 0.01 #direita
    else:
            if key == 265: r_x += 0.01 #cima
            if key == 264: r_x -= 0.01 #baixo
            if key == 263: r_x += 0.01 #esquerda
            if key == 262: r_x -= 0.01 #direita

    
glfw.set_key_callback(window,key_event)

# Define as funções que realizam as transformações
def scale(s_x, s_y):
    return np.array([   [s_x, 0.0, 0.0, 0.0], 
                        [0.0, s_y, 0.0, 0.0], 
                        [0.0, 0.0, 1.0, 0.0], 
                        [0.0, 0.0, 0.0, 1.0]], np.float32)

def rotation(r_x):
    return np.array([   [np.cos(r_x), -np.sin(r_x), 0.0, 0.0], 
                        [np.sin(r_x),  np.cos(r_x), 0.0, 0.0], 
                        [        0.0,          0.0, 1.0, 0.0], 
                        [        0.0,          0.0, 0.0, 1.0]], np.float32)

def translation(t_x, t_y):
    return np.array([   [1.0, 0.0, 0.0, t_x], 
                        [0.0, 1.0, 0.0, t_y], 
                        [0.0, 0.0, 1.0, 0.0], 
                        [0.0, 0.0, 0.0, 1.0]], np.float32)

def composta1(s_x, s_y, t_x, t_y, r):
    return np.matmul(scale(s_x, s_y), np.matmul(translation(t_x, t_y), rotation(r)))

def composta2(s_x, s_y, t_x, t_y, r):
    return np.matmul(rotation(r), np.matmul(translation(t_x, t_y), scale(s_x, s_y)))

glfw.show_window(window)

t_y = t_x = r_y = r_x = tr = 0
s_y = s_x = 1

round = 0
while not glfw.window_should_close(window):

    glfw.poll_events() 

    
    glClear(GL_COLOR_BUFFER_BIT) 
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    
    # Definindo as operações a ser passadas nas respostas
    mat_translation = translation(t_x, t_y)

    mat_scale       = scale(s_x, s_y)

    mat_rotation    = rotation(r_x)

    mat_comp1 = composta1(s_x, s_y, t_x, t_y, r_x)
    mat_comp2 = composta2(s_x, s_y, t_x, t_y, r_x)

    loc = glGetUniformLocation(program, "mat_transformation")

    # Respostas de cada operação por round
    respostas_per_round =   [
                                (2, 2, 0, 0, 0),
                                (1, 1, 0, 0, 2),
                                (1, 1, 0.5, 0.2, 0),
                                (1, 2, 0.2, 0.1, 2),
                                (1, 1.5, 0.2, 0.1, 1)
                            ]

    # Transformações realizadas em cada round
    transformacoes_per_round =  [   
                                    scale(2, 2), 
                                    rotation(2), 
                                    translation(0.5, 0.2), 
                                    composta1(1, 2, 0.2, 0.1, 2), 
                                    composta2(1, 1.5, 0.2, 0.1, 1)
                                ]

    # Operações que o usuário executa por round
    usuario_per_round = [
                            mat_comp1,
                            mat_comp1,
                            mat_comp1,
                            mat_comp1,
                            mat_comp2
                        ]

    # Exibindo cada round
    if round == 0:

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) ### modificando a cor do objeto
        glDrawArrays(GL_TRIANGLE_FAN, 0, 10)
            
        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 0, 10)

        if abs(respostas_per_round[round][0] - s_x) <= 0.01 and abs(respostas_per_round[round][1] - s_y) <= 0.01 and abs(respostas_per_round[round][2] - t_x) <= 0.01 and abs(respostas_per_round[round][3] - t_y) <= 0.01 and abs(respostas_per_round[round][4] - r_x) <= 0.01:
            round += 1
            tr = 0
            t_x = t_y = r_x = 0
            s_x = s_y = 1

    elif round == 1:

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 10, 18)
            
        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 10, 18)

        if abs(respostas_per_round[round][0] - s_x) <= 0.01 and abs(respostas_per_round[round][1] - s_y) <= 0.01 and abs(respostas_per_round[round][2] - t_x) <= 0.01 and abs(respostas_per_round[round][3] - t_y) <= 0.01 and abs(respostas_per_round[round][4] - r_x) <= 0.01:
            round += 1
            tr = 0
            t_x = t_y = r_x = 0
            s_x = s_y = 1

    elif round == 2:

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 28, 6)

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_LINES, 34, 2)
            
        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 28, 6)

        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_LINES, 34, 2)

        if abs(respostas_per_round[round][0] - s_x) <= 0.01 and abs(respostas_per_round[round][1] - s_y) <= 0.01 and abs(respostas_per_round[round][2] - t_x) <= 0.01 and abs(respostas_per_round[round][3] - t_y) <= 0.01 and abs(respostas_per_round[round][4] - r_x) <= 0.01:
            round += 1
            tr = 0
            t_x = t_y = r_x = 0
            s_x = s_y = 1

    elif round == 3:

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 36, 5)
            
        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_FAN, 36, 5)

        if abs(respostas_per_round[round][0] - s_x) <= 0.01 and abs(respostas_per_round[round][1] - s_y) <= 0.01 and abs(respostas_per_round[round][2] - t_x) <= 0.01 and abs(respostas_per_round[round][3] - t_y) <= 0.01 and abs(respostas_per_round[round][4] - r_x) <= 0.01:
            round += 1
            tr = 0
            t_x = t_y = r_x = 0
            s_x = s_y = 1

    elif round == 4:

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_TRIANGLE_STRIP, 41, 4)

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_TRIANGLE_STRIP, 45, 4)

        glUniformMatrix4fv(loc, 1, GL_TRUE, *transformacoes_per_round[round])
        glUniform4f(loc_color, 0, 0, 1, 1.0) 
        glDrawArrays(GL_TRIANGLE_STRIP, 49, 4)
            
        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_STRIP, 41, 4)

        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_STRIP, 45, 4)

        glUniformMatrix4fv(loc, 1, GL_TRUE, usuario_per_round[round])
        glUniform4f(loc_color, R, G, B, 1.0) 
        glDrawArrays(GL_TRIANGLE_STRIP, 49, 4)

        if abs(respostas_per_round[round][0] - s_x) <= 0.01 and abs(respostas_per_round[round][1] - s_y) <= 0.01 and abs(respostas_per_round[round][2] - t_x) <= 0.01 and abs(respostas_per_round[round][3] - t_y) <= 0.01 and abs(respostas_per_round[round][4] - r_x) <= 0.01:
            round += 1
            tr = 0
            t_x = t_y = r_x = 0
            s_x = s_y = 1

    else:

        # encerra o programa depois dos cinco rounds
        glfw.set_window_should_close(window)

    glfw.swap_buffers(window)

glfw.terminate()