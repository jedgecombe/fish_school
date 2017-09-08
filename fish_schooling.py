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


REBUILD_DIRECTORIES = ('output',)
FISH_TO_SPAWN = 50

# poly = ((0, 30), (20, 10), (40, 10), (100, 0), (100, 30), (110, 50), (60, 20), (80, 40), (80, 20), (120, 20), (120, 50), (60, 80),
#         (40, 70), (0, 30))

poly = ((0, 10), (20, -10), (35, -15), (40, -5), (50, 5), (60, 10), (80, 0), (90, 30), (70, 60), (35, 70), (25, 70), (5, 60), (-10, 30), (0, 10))

# create directories
for dir in REBUILD_DIRECTORIES:
    delete_and_rebuild_directory(directory_path=dir)

the_sea = OceanEnvironment(bounding_coordinates=poly)
wh = Whale(environment=the_sea)
nw = NearbyWaters(fish=wh, ocean=the_sea)
wh.distance_to_boundary()
while len(the_sea.population) < FISH_TO_SPAWN:
    fsh = Snapper(environment=the_sea)
    fh = NearbyWaters(fish=fsh, ocean=the_sea)

the_sea.get_fish_metadata()

the_sea.save_snapshot(output_name='output/initial_config.png')
