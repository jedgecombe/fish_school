import logging

from utils.environ import OceanEnvironment, FishMongers
from utils.fishies import Snapper, Shark
from utils.tools import delete_and_rebuild_directory

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d - %(name)s:%(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

"""
TODO
   * update fish names to those in data science off-site
   * remove species reference as text argument - can probably just achieve the same using the type - THINK I've done this but not checked it works
   * maybe make the graveyard and ocean subclass of something like 'world' - would then be easier to save a snaps short of each
   * think there are unused attributes - find and remove
   * fix shoal clustering - probably do this within animate function as should happen for every time period
   * NEXT - when fish have fish to follow, they just chill if their range is too far - this indicates something wrong with the random.choice of moves
   * NEXT UPDATE - finish on creating fish memory. Maybe add previous_rotation for consistency with previous_position
   * DBSCAN should happen according to follow distance - for this to work the clustering needs to happen for each species separately
   * Enter fish brains into postgres database
"""


REBUILD_DIRECTORIES = ['output']

FISH_NAMES = ['nemo', 'marvin', 'dyl', 'jal', 'ace', 'beatrix', 'cybil', 'lola', 'poppy',
              'zelda', 'ace', 'buster', 'dexter', 'finn', 'gunner', 'quinton', 'delilah', 'racer',
              'trixie', 'zeus', 'barnaby', 'tarquin', 'moby', 'free willy', 'jaws', 'bernie', 'suzanne',
              'chomper', 'antonella', 'auntie jane']

FISH_TO_SPAWN = 15
SHARKS_TO_SPAWN = 1
OCEAN_SCALE = 5  # to make ocean larger or smaller - integer
MOVES_PER_PERIOD = 1
PERIODS = 50

# unscaled coordinate bounds of ocean edge
OCEAN_BOUNDS = ((0, 10), (20, -10), (35, -15), (40, -5), (50, 5), (60, 10), (80, 0), (90, 30), (70, 60),
                (35, 70), (25, 70), (5, 60), (-10, 30), (0, 10))


def main():
    bounds_scaled = tuple((x[0] * OCEAN_SCALE, x[1] * OCEAN_SCALE) for x in OCEAN_BOUNDS)  # scale ocean

    # create directories
    delete_and_rebuild_directory(directory_paths=REBUILD_DIRECTORIES)

    # create ocean
    the_sea = OceanEnvironment(bounding_coordinates=bounds_scaled)
    old_johns_fish_mongers = FishMongers()

    for i in range(SHARKS_TO_SPAWN):
        moby = Shark(FISH_NAMES)
        moby.make_it_rain(the_sea, old_johns_fish_mongers, place_attempts=3)

    for i in range(FISH_TO_SPAWN):
        fsh = Snapper(FISH_NAMES)
        fsh.make_it_rain(the_sea, old_johns_fish_mongers, place_attempts=3)

    the_sea.passage_of_time(PERIODS, save_filename='output/movements.mp4')


if __name__ == '__main__':
    main()



