from math import (pi, sin, cos, acos, sqrt, tan)
from itertools import chain, islice
from random import choice, randint
import pyglet
from pyglet.gl import *

#6 => [5, 10, 11, 7, 1]
#7 => [1, 6, 11, 8, 2]
#8 => [2, 7, 11, 9, 3]

C_WHITE = 0
C_BABY = 1
C_PURPLE = 2
C_GREEN = 3
C_HELIO = 4
C_BROWN = 5
C_ORANGE = 6
C_RED = 7
C_BLUE = 8
C_PINK = 9
C_LIME = 10
C_YELLOW = 11

dihedral = acos(-1/sqrt(5))
dodec_rad = 1.0
edge_dist = dodec_rad / tan(dihedral / 2.0)
face_rad = edge_dist / cos(pi / 5.0)
edge_len = face_rad * 2 * sin(pi / 5.0)
inner_face_rad = face_rad - (cos(3.0 / 10.0 * pi) * edge_len)

def draw_color(color):
  colors = [
    (1.0, 1.0, 1.0),
    (188.0/256.0, 212.0/256.0, 230.0/256.0),
    (0.5, 0.0, 0.5),
    (34.0/256.0, 139.0/256.0, 24.0/256.0),
    (223.0/256.0, 115.0/256.0, 1.0),
    (159.0/256.0, 139.0/256.0, 112.0/256.0),
    (1.0, 0.5, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0),
    (1.0, 192.0/256.0, 203.0/256.0),
    (0.0, 1.0, 0.0),
    (1.0, 1.0, 0.0)
  ]
  
  (r, g, b) = colors[color]
  glColor3f(r, g, b)

def draw_pentagon():
  theta = 0.0
  for side in range(5):
    delta = theta + (2.0 / 5.0 * pi)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(sin(theta) * face_rad, cos(theta) * face_rad, 0.0)
    glVertex3f(sin(delta) * face_rad, cos(delta) * face_rad, 0.0)
    glEnd(GL_TRIANGLES)
    theta = delta


class Face:
  def __init__(self, color, puzzle):
    self.color = color
    self.puzzle = puzzle
    self.generate_neighbors()
    self.generate_tiles()
    self.generate_labels()
    self.rotation = 0
    self.display = None
    self.generate_display()
  
  def face_cycle(self, min, max, start):
      return range(start, max + 1) + range(min, start)
  
  def generate_labels(self):
    self.labels = []
    for num in range(11):
      self.labels.append(pyglet.text.Label(str(num), font_size=72, color=(0, 0, 0, 255), width=1, height=1, anchor_x='center', anchor_y='baseline'))
  
  def generate_tiles(self):
    self.tiles = zip(range(11), [self.color] * 11)
  
  def generate_display(self):
    if self.display is not None:
      glDeleteLists(self.display, 1)
    
    self.display = glGenLists(1)
    glNewList(self.display, GL_COMPILE)
    
    glPushMatrix()
    
    self.rotate_display()
    glTranslatef(0, 0, dodec_rad)
    
    glColor3f(0.0, 0.0, 0.0)
    draw_pentagon()
    
    glTranslatef(0.0, 0.0, 0.01)
    for tile_idx, tile in enumerate(self.tiles):
      self.draw_tile(tile_idx)
    
    glPopMatrix()
    glEndList()
  
  def generate_neighbors(self):
    if self.color == 0:
      # the easiest side
      self.neighbors =  zip(self.face_cycle(1,5,1), [2,2,2,2,2])
    elif self.color < 6:
      self.neighbors = zip(list(zip(
        self.face_cycle(6, 10, 7),
        self.face_cycle(1, 5, 2),
        [0, 0, 0, 0, 0],
        self.face_cycle(1, 5, 5),
        self.face_cycle(6, 10, 6))[self.color - 1]), [0, 3, 0, 1, 4])
    elif self.color < 11:
      self.neighbors = zip(list(zip(
        self.face_cycle(1,5,5),
        self.face_cycle(6,10,6),
        [11,11,11,11,11],
        self.face_cycle(6,10,7),
        self.face_cycle(1,5,1)
      )[self.color - 6]), [0,3,2,1,4])
    else:
      self.neighbors = zip(self.face_cycle(6,10,8), [2,2,2,2,2])

  def rotate_display(self):
    if self.color == 0: # bottom
      glRotatef(90, 1.0, 0.0, 0.0)
      #glRotatef(180, 0.0, 0.0, 1)
    elif self.color == 11: # top
      glRotatef(-90, 1.0, 0.0, 0.0)
    elif self.color < 6: # first layer
      glRotatef(36 + (72 * (self.color - 1)), 0.0, 1.0, 0.0)
      glRotatef((-pi / 2.0 + dihedral)/ pi * 180, 1.0, 0.0, 0.0)
    else: # second layer
      glRotatef(72 * (self.color - 6), 0.0, 1.0, 0.0)
      glRotatef(-(-pi / 2.0 + dihedral) / pi * 180, 1.0, 0.0, 0.0)
      glRotatef(180, 0, 0, 1)
  
  def draw_label(self, label):
    glPushMatrix()
    glTranslatef(0.0, -0.3, 0.0)
    glScalef(0.01, 0.01, 0.0)
    label.draw()
    glPopMatrix()
  
  def draw_tile(self, idx):
    (tile_id, color) = self.tiles[idx]
    draw_color(color)
    label = self.labels[tile_id]
    scale = 0.8
    outer_inner_ratio = inner_face_rad / face_rad
    if idx == 10: # center
      glPushMatrix()
      inner_scale = (edge_dist + face_rad) * (1.0 + outer_inner_ratio) * 0.5 * outer_inner_ratio
      glScalef(inner_scale, inner_scale, inner_scale)
      draw_pentagon()
      glTranslatef(0.0, 0.0, 0.01)
      glRotatef(self.rotation * 72, 0.0, 0.0, 1.0)
      self.draw_label(label)
      glPopMatrix()
      return
    glPushMatrix()
    glScalef(scale, scale, 1.0)
    if idx % 2 == 1: # edge piece
      glRotatef(-idx * 36, 0.0, 0.0, 1.0)
      glTranslatef(0.0, face_rad  * (1 - scale) - ((face_rad - inner_face_rad) * (1 - scale) * 0.5), 0.0)
      theta = (pi / 5.0)
      glBegin(GL_TRIANGLES)
      glVertex3f(sin(-theta) * inner_face_rad, cos(-theta) * inner_face_rad, 0.0)
      glVertex3f(sin(theta) * inner_face_rad, cos(theta) * inner_face_rad, 0.0)
      glVertex3f(0.0, edge_dist, 0.0)
      glEnd()
      glTranslatef(0.0, face_rad / 2.5, 0.0)
      glScalef(0.2, 0.2, 1.0)
      glTranslatef(0.0, 0.0, 0.01)
      self.draw_label(label)
    elif idx % 2 == 0: # corners
      glRotatef(-idx * 36, 0.0, 0.0, 1.0)
      glTranslatef(0.0, 0.5/scale - 0.5, 0.0)
      theta = pi / 5.0
      glBegin(GL_TRIANGLES)
      glVertex3f(sin(-theta) * edge_dist, cos(-theta) * edge_dist, 0.0)
      glVertex3f(0.0, inner_face_rad, 0.0)
      glVertex3f(0.0, face_rad, 0.0)
  
      glVertex3f(sin(theta) * edge_dist, cos(theta) * edge_dist, 0.0)
      glVertex3f(0.0, inner_face_rad, 0.0)
      glVertex3f(0.0, face_rad, 0.0)
      glEnd()
  
      glTranslatef(0.0, (inner_face_rad + face_rad) / 2.0, 0.0)
      glScalef(0.4, 0.4, 1.0)
      glTranslatef(0.0, 0.0, 0.01)
      self.draw_label(label)
    glPopMatrix()
  
  def fetch_side(self, side_idx):
    if side_idx == 4:
      return (self.tiles[8], self.tiles[9], self.tiles[0])
    return (self.tiles[side_idx * 2], self.tiles[side_idx * 2 + 1], self.tiles[side_idx * 2 + 2])
  
  def set_side(self, side_idx, new):
    if side_idx == 4:
      self.tiles[8], self.tiles[9], self.tiles[0] = new
    else:
      self.tiles[side_idx * 2], self.tiles[side_idx * 2 + 1], self.tiles[side_idx * 2 + 2] = new
    self.generate_display()
  
  def rotate_side(self, num):
    num = num % 5
    if num == 0:
      return
    self.tiles = self.tiles[num * 2:10] + self.tiles[:num * 2] + [self.tiles[10]]
    self.rotation = (self.rotation + num) % 5
    
    #now the neighbors
    faces, sides = zip(*self.neighbors)
    faces = map(self.puzzle.get_face, faces)
    
    # pull out the edges
    edges = []
    for idx, face in enumerate(faces):
      edges.append(face.fetch_side(sides[idx]))
    edges = edges[num:] + edges[:num]
    for idx, face in enumerate(faces):
      face.set_side(sides[idx], edges[idx])
    # and that's it!
    self.generate_display()

  def draw(self):
    glCallList(self.display)
    

class Puzzle:
  def __init__(self):
    self.theta = self.phi = 0
    self.init_faces()
  
  def init_faces(self):
    self.faces = []
    for color in range(12):
      self.faces.append(Face(color, self))

  def draw(self):
    glTranslatef(0.0, 0.0, -5.0)
    glRotatef(self.phi / pi * 180.0, 0.0, 1.0, 0.0)
    glRotatef(self.theta / pi * 180.0, 1.0, 0.0, 0.0)
    for face in self.faces:
      face.draw()
  
  def update_theta(self, d_theta): # change in theta
    theta = self.theta + d_theta
    if theta > pi / 2.0:
      self.theta = pi / 2.0
    elif theta < -pi / 2.0:
      self.theta = -pi / 2.0
    else:
      self.theta = theta
  
  def update_phi(self, d_phi):
    phi = self.phi + d_phi
    if phi > pi:
      self.phi = phi - 2.0 * pi
    elif phi < -pi:
      self.phi = phi + 2.0 * pi
    else:
      self.phi = phi
   
  def get_face(self, idx):
    return self.faces[idx]
  
  def shuffle(self, times):
    for time in range(times):
      choice(self.faces).rotate_side(randint(0,4))


window = pyglet.window.Window()
puzzle = Puzzle()
puzzle.shuffle(50)

@window.event
def on_draw():
  glClear(GL_COLOR_BUFFER_BIT)
  glClear(GL_DEPTH_BUFFER_BIT)
  glLoadIdentity()
  puzzle.draw()
  glFlush()
  

@window.event
def on_resize(width, height):
  glViewport(0, 0, width, height)
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  gluPerspective(65, width / float(height), .1, 1000)
  glMatrixMode(GL_MODELVIEW)
  glEnable(GL_DEPTH_TEST)
  glDepthFunc(GL_LEQUAL)
  return pyglet.event.EVENT_HANDLED


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
  # dx is scaled so dx=width => d_phi = 2pi
  # dy so that dy=height => d_theta = pi
  (w, h) = window.get_size()
  if buttons == pyglet.window.mouse.LEFT:
    puzzle.update_phi(float(dx) / w * pi * 2)
    puzzle.update_theta(-float(dy) / h * pi)

pyglet.app.run()



