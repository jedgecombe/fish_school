import logging
import math
import random

from utils.environ import OceanEnvironment
# from utils.fishies import Fish
from utils.spatial_utils import SpatialUtils

logger = logging.getLogger(__name__)


class Position:
    def __init__(self, position: tuple, environment: OceanEnvironment, fish):
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
                if self.detect_fish_collision():
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

    def detect_fish_collision(self):
        other_fish = self.find_other_fish()
        for fish in other_fish:
            if self.coordinates == fish.position:
                logger.debug('collision between fish: {} ({}), and: {} ({})'.format(self.fish.name, self.fish.unique_id,
                                                                                    fish.name, fish.unique_id))
                return True

    def detect_edge_collision(self):
        pass

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
