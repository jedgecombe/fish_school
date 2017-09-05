import logging
import math
import random

from utils.spatial_utils import SpatialUtils
from utils.environ import OceanEnvironment
from utils.fishies import Snapper, Whale
from utils.tools import delete_and_rebuild_directory

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s:%(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


REBUILD_DIRECTORIES = ('output',)
FISH_TO_SPAWN = 50


poly = ((0, 30), (20, 10), (40, 10), (100, 0), (100, 30), (110, 50), (60, 80), (40, 70), (0, 30))

# create directories
for dir in REBUILD_DIRECTORIES:
    delete_and_rebuild_directory(directory_path=dir)

the_sea = OceanEnvironment(bounding_coordinates=poly)
fishes = 0
while len(the_sea.population) < FISH_TO_SPAWN:
    fsh = Snapper(environment=the_sea)

wh = Whale(environment=the_sea)
the_sea.get_fish()

the_sea.save_snapshot(output_name='output/initial_config.png')
