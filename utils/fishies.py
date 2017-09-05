import logging
import random

import matplotlib.pyplot as plt
from scipy import ndimage

from utils.environ import OceanEnvironment
from utils.fish_positioning import Position


logger = logging.getLogger(__name__)

FISH_NAMES = ['nemo', 'marvin', 'dyl', 'jal', 'ace', 'beatrix', 'cybil', 'lola', 'poppy',
              'zelda', 'ace', 'buster', 'dexter', 'finn', 'gunner', 'quinton', 'delilah', 'racer',
              'trixie', 'zeus', 'barnaby', 'tarquin']


class Fish:
    def __init__(self, environment: OceanEnvironment, species: str, initial_position: tuple=None, fish_name: str=None,
                 place_attempts: int=3):
        self.environment = environment
        self.unique_id = self.generate_unique_id()
        self.name = fish_name
        self.species = species
        self.rotation = self.choose_random_rotation()
        if fish_name is None:
            self.name = self.choose_random_name()
        else:
            self.name = fish_name
        self.position = Position(position=initial_position, environment=self.environment, fish=self).set_pos(place_attempts)

        if self.position is None:
            # fish generated on the land
            self.welfare = 'dead'
        else:
            self.welfare = 'alive'

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


class Snapper(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None,
                 initial_position: tuple=None, place_attempts: int=3
                 ):
        Fish.__init__(self, environment=environment, species='whale', initial_position=initial_position,
                      fish_name=fish_name, place_attempts=place_attempts)
        self.size = 5
        # self.colour = '#1a1aff'  # dark blue
        self.repel_distance = 1  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = 3  # focal fish will seek to align direction with neighbours
        self.follow_distance = 10  # focal fish will move towards a neighbour
        self.max_movement_radius = 2  # max distance fish can move in a single turn
        im = plt.imread('input/fish.png')
        self.graph_marker = ndimage.rotate(im, self.rotation)


class Whale(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None,
                 initial_position: tuple=None, place_attempts: int=3
                 ):
        Fish.__init__(self, environment=environment, species='whale', initial_position=initial_position,
                      fish_name=fish_name, place_attempts=place_attempts)
        self.size = 15
        # self.colour = '#1a1aff'  # dark blue
        self.repel_distance = 1  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = 3  # focal fish will seek to align direction with neighbours
        self.follow_distance = 10  # focal fish will move towards a neighbour
        self.max_movement_radius = 2  # max distance fish can move in a single turn
        im = plt.imread('input/fish.png')
        self.graph_marker = ndimage.rotate(im, self.rotation)

