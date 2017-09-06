import logging
import math
import random

import matplotlib.pyplot as plt
from scipy import ndimage

from utils.environ import OceanEnvironment
from utils.spatial_utils import SpatialUtils

logger = logging.getLogger(__name__)

FISH_NAMES = ['nemo', 'marvin', 'dyl', 'jal', 'ace', 'beatrix', 'cybil', 'lola', 'poppy',
              'zelda', 'ace', 'buster', 'dexter', 'finn', 'gunner', 'quinton', 'delilah', 'racer',
              'trixie', 'zeus', 'barnaby', 'tarquin']


class Fish:
    def __init__(self, environment: OceanEnvironment, species: str, fish_name: str=None,
                 initial_position: tuple=None, place_attempts: int=3):
        self.environment = environment
        self.unique_id = self.generate_unique_id()
        self.name = fish_name
        self.species = species
        self.size = 1  # give default size - overwritten when creating species
        self.rotation = self.choose_random_rotation()
        self.position = initial_position
        self.dist_to_closest_edge = self.distance_to_boundary()
        if fish_name is None:
            self.name = self.choose_random_name()
        else:
            self.name = fish_name
        self.welfare = 'dead'  # start off dead and become alive when find valid position
        environment.population.append(self)

        logger.info('created {}: {}'.format(self.species, self.name))

    @staticmethod
    def choose_random_name():
        return random.choice(FISH_NAMES)

    @staticmethod
    def choose_random_rotation():
        available_rotations = (0, 90, 180, 270)
        return random.choice(available_rotations)

    def generate_unique_id(self):
        return len(self.environment.population) + 1

    def distance_to_boundary(self):
        if self.position is not None:
            self.dist_to_closest_edge = SpatialUtils.distance_to_boundary(self.position, self.environment.boundary)
            return self.dist_to_closest_edge


class Snapper(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None,
                 initial_position: tuple=None, place_attempts: int=3):
        Fish.__init__(self, environment=environment, species='whale', initial_position=initial_position,
                      fish_name=fish_name, place_attempts=place_attempts)
        self.size = 5
        self.repel_distance = 1  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = 3  # focal fish will seek to align direction with neighbours
        self.follow_distance = 10  # focal fish will move towards a neighbour
        self.max_movement_radius = 2  # max distance fish can move in a single turn
        im = plt.imread('input/fish.png')
        self.graph_marker = ndimage.rotate(im, self.rotation)

        self.fish_pos = FishPosition(environment=self.environment, fish=self)
        self.position = self.fish_pos.set_pos(place_attempts)

        if self.position is not None:
            self.welfare = 'alive'

        self.dist_to_closest_edge = self.distance_to_boundary()


class Whale(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None,
                 initial_position: tuple=None, place_attempts: int=3
                 ):
        Fish.__init__(self, environment=environment, species='whale', initial_position=initial_position,
                      fish_name=fish_name, place_attempts=place_attempts)
        self.size = 15
        self.repel_distance = 1  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = 3  # focal fish will seek to align direction with neighbours
        self.follow_distance = 10  # focal fish will move towards a neighbour
        self.max_movement_radius = 2  # max distance fish can move in a single turn
        im = plt.imread('input/fish.png')
        self.graph_marker = ndimage.rotate(im, self.rotation)

        self.fish_pos = FishPosition(environment=self.environment, fish=self)
        self.position = self.fish_pos.set_pos(place_attempts)

        if self.position is not None:
            self.welfare = 'alive'

        self.dist_to_closest_edge = self.distance_to_boundary()


class FishPosition:
    def __init__(self, environment: OceanEnvironment, fish: Fish):
        self.environment = environment
        self.fish = fish
        if self.fish.position is not None:
            SpatialUtils.distance_to_boundary(self.fish.position, self.environment.boundary)

    # define the position of the fish in the environment
    def set_pos(self, place_attempts) -> tuple:
        bbox = SpatialUtils.extract_bounding_box(self.environment.boundary)
        for attempt in range(place_attempts):
            if self.fish.position is None:
                self.fish.position = self.generate_random_position(bounding_box=bbox,
                                                                 full_boundary=self.environment.boundary)
                logger.debug(
                    'position generated for {} ({}): {}'.format(self.fish.name, self.fish.unique_id, self.fish.position))
            if self.fish.position is not None:
                other_fish = self.find_other_fish()
                if self.detect_fish_collision(self.fish.position, other_fish):
                    logger.debug('generating new starting location for: {} ({})'.format(self.fish.name,
                                                                                        self.fish.unique_id))
                    self.fish.position = None
                else:
                    logger.debug('successfully avoided collision for {} ({}) on attempt: {}'.format(self.fish.name,
                                                                                                    self.fish.unique_id,
                                                                                                    attempt))
                    break

        return self.fish.position

    def generate_random_position(self, bounding_box: tuple, full_boundary: tuple):
        """generate random starting position within bounding box of environment"""
        proposed_starting_pos = (
            random.randint(bounding_box[0], bounding_box[2]), random.randint(bounding_box[1], bounding_box[3]))
        if SpatialUtils.poly_contains_point(coordinates=proposed_starting_pos, polygon=full_boundary,
                                            method='winding'):
            logger.info(
                'sploosh! {} ({}) landed in the water! {}'.format(self.fish.name, self.fish.unique_id, proposed_starting_pos))
            return proposed_starting_pos
        else:
            logger.info('flop! {} ({}) cannot swim outside of the ocean: {}'.format(self.fish.name, self.fish.unique_id, proposed_starting_pos))
            return None

    def detect_fish_collision(self, coordinates: tuple, comparison_group: list) -> bool:
        for other in comparison_group:
            distance_between = SpatialUtils.calc_distance(coordinates, other.position)
            if distance_between < max([self.fish.size, other.size]):
                logger.debug('collision between fish: {} ({}), and: {} ({})'.format(self.fish.name, self.fish.unique_id,
                                                                                    other.name, other.unique_id))
                return True

    def detect_edge_collision(self):
        pass

    def find_other_fish(self) -> list:
        """find other fish in their current positions
            remove current fish and dead fish from list of fish being considered
        """
        other_fish = []
        for fish in self.environment.population:
            if fish.unique_id != self.fish.unique_id and fish.welfare != 'dead':
                other_fish.append(fish)
        return other_fish


