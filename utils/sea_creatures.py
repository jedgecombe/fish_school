import logging
import math
import random

from utils.environ import OceanEnvironment
from utils.spatial_utils import SpatialUtils


logger = logging.getLogger(__name__)

FISH_NAMES = ['nemo', 'marvin', 'dyl', 'jal', 'ace', 'beatrix', 'cybil', 'lola', 'poppy',
              'zelda', 'ace', 'buster', 'dexter', 'finn', 'gunner', 'quinton', 'delilah', 'racer',
              'trixie', 'zeus', 'barnaby', 'tarquin']


class Fish:
    def __init__(self, environment: OceanEnvironment, initial_position: tuple=None, fish_name: str=None, place_attempts: int=3):
        self.environment = environment
        self.unique_id = self.generate_unique_id()
        self.name = fish_name
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





        # add fish to environment
        environment.population.append(self)

        logger.info('created fish: {}'.format(self.name))

    @staticmethod
    def choose_random_name():
        return random.choice(FISH_NAMES)

    def generate_unique_id(self):
        return len(self.environment.population) + 1

    #
    # # Move the fish within its environment
    # def calc_move(self):
    #
    #     # Pick a random number, up the max movement radius, for the fish to move on X & Y
    #     x_transform = random.randint(-self.max_movement_radius, self.max_movement_radius)
    #     y_transform = random.randint(-self.max_movement_radius, self.max_movement_radius)
    #
    #     # Default the description and new positions in the case that the movement is zero
    #     x_pos_new = self.current_pos.coordinates[0]
    #     y_pos_new = self.current_pos.coordinates[1]
    #
    #     # Limit the movement on the x-axis to between 0, environment max_x_pos
    #     if x_transform > 0:
    #         x_pos_new = min((self.current_pos.coordinates[0] + x_transform), self.environment.plane[0])
    #     if x_transform < 0:
    #         x_pos_new = max((self.current_pos.coordinates[0] + x_transform), 0)
    #
    #     # Limit the movement on the y-axis to between 0, environment max_y_pos
    #     if y_transform > 0:
    #         y_pos_new = min((self.current_pos.coordinates[1] + y_transform), self.environment.plane[1])
    #     if y_transform < 0:
    #         y_pos_new = max((self.current_pos.coordinates[1] + y_transform), 0);
    #
    #     # Record the proposed and the actual transformations
    #     proposed_transform = [x_transform, y_transform]
    #     actual_transform = [x_pos_new - self.current_pos.coordinates[0], y_pos_new - self.current_pos.coordinates[1]]
    #
    #     # Commit the actual transformation
    #     self.next_pos.coordinates[0] = x_pos_new
    #     self.next_pos.coordinates[1] = y_pos_new
    #
    #     return self.next_pos
    #
    # def move(self):
    #
    #     self.last_pos.coordinates = self.current_pos.coordinates
    #     self.current_pos.coordinates = self.next_pos.coordinates
    #     self.next_pos.coordinates = [None, None]
    #     self.to_direction = [None, None]


class Whale(Fish):
    def __init__(self, follow_zone_ratio, align_zone_ratio, repel_zone_ratio, max_movement_radius):
        self.follow_zone_ratio = follow_zone_ratio
        self.align_zone_ratio = align_zone_ratio
        self.repel_zone_ratio = repel_zone_ratio
        self.max_movement_radius = math.ceil(max_movement_radius)
        # Define the denominator for the fish movement radius as dictated by the three zones (follow, align, repel)
        # self.denominator = self.follow_zone_ratio + self.align_zone_ratio + self.repel_zone_ratio


class Position:
    def __init__(self, position: tuple, environment: OceanEnvironment, fish: Fish):
        self.coordinates = position
        self.environment = environment
        self.fish = fish

    # define the position of the fish in the environment
    def set_pos(self, place_attempts) -> tuple:
        bbox = SpatialUtils.extract_bounding_box(self.environment.boundary)
        for attempt in range(place_attempts):
            if self.coordinates is None:
                self.coordinates = self.generate_random_position(bounding_box=bbox,
                                                                 full_boundary=self.environment.boundary)
                logger.debug(
                    'position generated for {} ({}): {}'.format(self.fish.name, self.fish.unique_id, self.coordinates))
            if self.coordinates is not None:
                if self.detect_collision():
                    logger.debug('generating new starting location for: {} ({})'.format(self.fish.name,
                                                                                        self.fish.unique_id))
                    self.coordinates = None
                else:
                    logger.debug('successfully avoided collision for {} ({}) on attempt: {}'.format(self.fish.name,
                                                                                                    self.fish.unique_id,
                                                                                                    attempt))
                    break

        return self.coordinates

    def generate_random_position(self, bounding_box: tuple, full_boundary: tuple):
        """generate random starting position within bounding box of environment"""
        proposed_starting_pos = (
            random.randint(bounding_box[0], bounding_box[2]), random.randint(bounding_box[1], bounding_box[3]))
        if SpatialUtils.poly_contains_point(point=proposed_starting_pos, polygon=full_boundary,
                                            method='winding'):
            logger.info(
                'sploosh! {} ({}) landed in the water! {}'.format(self.fish.name, self.fish.unique_id, proposed_starting_pos))
            return proposed_starting_pos
        else:
            logger.info('flop! {} ({}) cannot swim outside of the ocean: {}'.format(self.fish.name, self.fish.unique_id, proposed_starting_pos))
            return None

    def detect_collision(self):
        other_fish = self.find_other_fish()
        for fish in other_fish:
            if self.coordinates == fish.position:
                logger.debug('collision between fish: {} ({}), and: {} ({})'.format(self.fish.name, self.fish.unique_id,
                                                                                    fish.name, fish.unique_id))
                return True

    def find_other_fish(self):
        """remove current fish and dead fish from list of fish being considered"""
        other_fish = []
        for fish in self.environment.population:
            if fish.welfare != 'dead' and fish.unique_id != self.fish.unique_id:
                other_fish.append(fish)
        return other_fish

    def calc_distance(self, comparison_position):
        squared_dist = (self.coordinates[0] - comparison_position.coordinates[0]) ** 2 + (self.coordinates[1] -
                                                                                          comparison_position.coordinates[
                                                                                              1]) ** 2
        dist = math.sqrt(squared_dist)
        return round(dist, 4)

    def calc_angle(self, that_position):
        """def angle_trunc(a):
                while a < 0.0:
                        a += pi * 2
                return a"""

        deltaY = that_position.coordinates[1] - self.coordinates[1]
        deltaX = that_position.coordinates[0] - self.coordinates[0]
        # return degrees(angle_trunc(atan2(deltaY, deltaX)))

        return math.degrees(math.atan2(deltaY, deltaX))