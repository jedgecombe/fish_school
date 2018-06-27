from ocean import Ocean
from creatures import Fish
from spatial_utils import SpatialUtils

fish_num = 10
sea = Ocean()

def setup():
  size(640, 360)

def draw():
    background(255)
    sea.swim()
  
def mousePressed():
    Fish(0, sea, repel_distance=20, x=mouseX, y=mouseY)

        
    
