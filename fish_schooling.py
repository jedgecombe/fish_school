import logging
import math
import random

from spatial_utils import SpatialUtils
from environ import OceanEnvironment
from sea_creatures import Fish
from tools import delete_and_rebuild_directory

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s:%(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


DIRECTORIES = ('INPUT', 'OUTPUT')
FISH_TO_SPAWN = 5


# i = 0
# while (i <= 4):
#     print(nemo.current_pos.coordinates)
#     nemo.calc_move()
#     nemo.move()
#     print(nemo.current_pos.coordinates)
#     print(nemo.current_pos.calc_angle(nemo.last_pos))
#     i = i + 1

# JE write something to clear and create input / output
poly = ((0, 3), (2, 1), (4, 1), (10, 0), (10, 3), (11, 5), (6, 8), (4, 7), (0, 3))

# create directories
for dir in DIRECTORIES:
    delete_and_rebuild_directory(directory_path=dir)

the_sea = OceanEnvironment(bounding_coordinates=poly)
fishes = 0
while len(the_sea.population) <= FISH_TO_SPAWN:
    fsh = Fish(environment=the_sea, initial_position=None, place_attempts=3)
the_sea.get_fish()

the_sea.save_snapshot(output_name='output/initial_config.png')
