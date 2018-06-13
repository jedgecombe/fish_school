import logging

import numpy as np

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
   * maybe make the graveyard and ocean subclass of something like 'world' - would then be easier to save a snaps short of each
   * think there are unused attributes - find and remove
   * fix shoal clustering - probably do this within animate function as should happen for every time period
   * NEXT - when fish have fish to follow, they just chill if their range is too far - this indicates something wrong with the random.choice of moves
   * NEXT UPDATE - finish on creating fish memory. Maybe add previous_rotation for consistency with previous_position
   * DBSCAN should happen according to follow distance - for this to work the clustering needs to happen for each species separately
   * Enter fish brains into postgres database
   * update DBSCAN to be class with .fit() a la sklearn. THINK border points should only be used to connect to other points if they have len(neighbours) > min_points. https://github.com/rugbyprof/4553-Spatial-DS/wiki/Dbscan
   * sure there is something up with the available options generated
   * the fish don't really need to know what moves are available - instead choose a move and check whether it available
   * add __repr__ to fish and ocean classes
   * would be cool to add some kind of decorators
"""


REBUILD_DIRECTORIES = ['output']
#%%
# FISH_NAMES = ['nemo', 'marvin', 'dyl', 'jal', 'ace', 'beatrix', 'cybil', 'lola', 'poppy',
#               'zelda', 'ace', 'buster', 'dexter', 'finn', 'gunner', 'quinton', 'delilah', 'racer',
#               'trixie', 'zeus', 'barnaby', 'tarquin', 'moby', 'free willy', 'jaws', 'bernie', 'suzanne',
#               'chomper', 'antonella', 'auntie jane']
FISH_NAMES = ['Alex', 'Andy', 'Ben', 'Clemente', 'Desi', 'Ela', 'Eleanor', 'James', 'Jamie', 'Jared',
             'Jeffrey', 'Jonathan', 'Khurom', 'Mahana', 'Mike', 'Oli', 'Orhan', 'Pete', 'Roland', 'Wing Lon',
             'Alessio', 'Bastien', 'David', 'Giacomo', 'Gilad', 'Harry', 'Hugo', 'Johnny', 'Jonny',
             'Kavya', 'Lampros', 'Lois', 'Will']
# print(len(FISH_NAMES))
#%%

FISH_TO_SPAWN = 31
SHARKS_TO_SPAWN = 2
OCEAN_SCALE = 7  # to make ocean larger or smaller - integer
MOVES_PER_PERIOD = 1
PERIODS = 250

# unscaled coordinate bounds of ocean edge
OCEAN_BOUNDS = ((0, 10), (20, -10), (35, -15), (40, -5), (50, 5), (60, 10), (80, 0), (90, 30), (70, 60),
                (35, 70), (25, 70), (5, 60), (-10, 30), (0, 10))


def main():
    bounds_scaled = tuple((x[0] * OCEAN_SCALE, x[1] * OCEAN_SCALE) for x in OCEAN_BOUNDS)  # scale ocean

    # create directories
    delete_and_rebuild_directory(directory_paths=REBUILD_DIRECTORIES)

    # create ocean
    the_sea = OceanEnvironment(bounding_coordinates=bounds_scaled, minimum_shoal_size=3)
    old_johns_fish_mongers = FishMongers()

    fish_names = FISH_NAMES
    for i in range(SHARKS_TO_SPAWN):
        name = np.random.choice(fish_names)
        fish_names.remove(name)
        moby = Shark([name])
        moby.make_it_rain(the_sea, old_johns_fish_mongers, place_attempts=10)

    for i in range(FISH_TO_SPAWN):
        name = np.random.choice(fish_names)
        fish_names.remove(name)
        fsh = Snapper([name])
        fsh.make_it_rain(the_sea, old_johns_fish_mongers, place_attempts=10)

    the_sea.passage_of_time(PERIODS, save_filename='output/movements.mp4')


if __name__ == '__main__':
    main()
