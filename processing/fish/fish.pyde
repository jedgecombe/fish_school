from ocean import Ocean
from creatures import Fish
from spatial_utils import SpatialUtils

fish_num = 10
sea = Ocean()

def setup():
  size(640, 360)
  sea.create_ocean()

def draw():
    sea.create_ocean()
    # rect(0, 0, 150, 150)
    sea.swim()
  
def mousePressed():
    Fish(0, sea, separation_distance=30, x=mouseX, y=mouseY)

        
    
