import logging

from utils.environ import OceanEnvironment, NearbyWaters, Snapper, Whale
# from utils.fishies import
from utils.tools import delete_and_rebuild_directory

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s:%(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


REBUILD_DIRECTORIES = ('output', )
FISH_TO_SPAWN = 15
SHARKS_TO_SPAWN = 1
OCEAN_SCALE = 1  # to make ocean larger or smaller - integer
MOVES_PER_PERIOD = 20

poly = ((0, 10), (20, -10), (35, -15), (40, -5), (50, 5), (60, 10), (80, 0), (90, 30), (70, 60), (35, 70), (25, 70), (5, 60), (-10, 30), (0, 10))

poly = tuple((x[0] * OCEAN_SCALE, x[1] * OCEAN_SCALE) for x in poly)  # scale ocean

# create directories
for dir in REBUILD_DIRECTORIES:
    delete_and_rebuild_directory(directory_path=dir)

the_sea = OceanEnvironment(bounding_coordinates=poly)

while len(the_sea.population) < SHARKS_TO_SPAWN:
    moby = Whale(environment=the_sea)
# nw = NearbyWaters(fish=jaws, ocean=the_sea)
while len(the_sea.population) < FISH_TO_SPAWN:
    fsh = Snapper(environment=the_sea)

the_sea.save_snapshot(output_name='output/initial_config.png')
the_sea.get_fish_metadata()

the_sea.let_time_pass(MOVES_PER_PERIOD)
the_sea.save_snapshot(output_name='output/time_1.png')

the_sea.let_time_pass(MOVES_PER_PERIOD)
the_sea.save_snapshot(output_name='output/time_2.png')

the_sea.let_time_pass(MOVES_PER_PERIOD)
the_sea.save_snapshot(output_name='output/time_3.png')

the_sea.let_time_pass(MOVES_PER_PERIOD)
the_sea.save_snapshot(output_name='output/time_4.png')


