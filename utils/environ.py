import json
import logging
import math
import os
import pprint
import random

import numpy as np

from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox
from scipy import ndimage

from utils.spatial_utils import SpatialUtils

logger = logging.getLogger(__name__)


FISH_NAMES = ['nemo', 'marvin', 'dyl', 'jal', 'ace', 'beatrix', 'cybil', 'lola', 'poppy',
              'zelda', 'ace', 'buster', 'dexter', 'finn', 'gunner', 'quinton', 'delilah', 'racer',
              'trixie', 'zeus', 'barnaby', 'tarquin', 'moby', 'free willy', 'jaws', 'bernie', 'suzanne',
              'chomper']


class OceanEnvironment:
    def __init__(self, bounding_coordinates: tuple):
        """
        :param bounding_coordinates: should be tuple of tuples (x, y) listed in counterclockwise direction
            ending with the first coordinate to close path
        """
        self.boundary = bounding_coordinates
        self.population = []
        self.populated_sorted = self._sort_population_according_to_incentive()

        # self.background_colour = '#f6e5ae'
        self.sea_colour = '#006994'

    def get_fish_metadata(self):
        """
        log fish, grouped according to whether they are dead or alive
        :return: nothing
        """
        alive_fish = []
        dead_fish = []
        for fish in self.population:
            if fish.welfare != 'dead':
                fish_data = self._extract_fish_brains(fish)
                alive_fish.append(fish_data)
            else:
                fish_data = self._extract_fish_brains(fish)
                dead_fish.append(fish_data)
            logger.debug('fish: {}'.format(fish_data))
        logger.info('number of alive fish: {}'.format(len(alive_fish)))
        logger.info('number of dead fish: {}'.format(len(dead_fish)))

    def let_time_pass(self, moves_in_time_period):
        """
        first recalculate all fish's incentives to move
        find fish who want to move most
        :param moves_in_time_period: number of fish to move
        :return: nothing, just output logs
        """
        for fsh_num in range(len(self.population)):
            agitated_fish = self.population[fsh_num]
            initial_position = agitated_fish.position
            initial_rotation = agitated_fish.rotation
            next_pos = agitated_fish.choose_next_move()
            next_rotation = agitated_fish.rotation
            agitated_fish.position = next_pos
            dist = SpatialUtils.calc_distance(initial_position, next_pos)
            logger.debug('{} ({}) moved from {} to {}, distance: {}, rotation from {} to {}'.format(agitated_fish.name,
                                                                                                    agitated_fish.species,
                                                                                                    initial_position,
                                                                                                    next_pos, dist,
                                                                                                    initial_rotation,
                                                                                                    next_rotation))
        # self.assess_desire_to_move()
        ## following is for when using predator count to determine whether or not they move
        # for fsh_num in range(moves_in_time_period):
        #     self.assess_desire_to_move()
        #     agitated_fish = self.populated_sorted[0]  # select fish with highest incentive to move
        #     initial_position = agitated_fish.position
        #     initial_rotation = agitated_fish.rotation
        #     next_pos = agitated_fish.choose_next_move()
        #     next_rotation = agitated_fish.rotation
        #     agitated_fish.position = next_pos
        #     dist = SpatialUtils.calc_distance(initial_position, next_pos)
        #     logger.debug('{} ({}) moved from {} to {}, distance: {}, rotation from {} to {}'.format(agitated_fish.name,
        #                                                                                             agitated_fish.species,
        #                                                                                             initial_position,
        #                                                                                             next_pos, dist,
        #                                                                                             initial_rotation,
        #                                                                                             next_rotation))

    def assess_desire_to_move(self):
        """
        cycle through population and see whether there is a predator in each fish's
            sub env - if there is they have an incentive to move update that fish's attribute
            then update self.populated_sorted
        """
        for fsh in self.population:
            fsh.incentive_to_move = 1
            # refresh sub environ
            # sub_env = NearbyWaters(fish=fsh, ocean=self)
            # if it fish has available moves, incentive to move = number of predators in area
            # if len(fsh.possible_moves) > 0:
            #     fsh.incentive_to_move = sub_env.predator_count
        self.populated_sorted = self._sort_population_according_to_incentive()

    def _sort_population_according_to_incentive(self):
        return sorted(self.population, key=lambda x: x.incentive_to_move, reverse=True)

    def _extract_fish_brains(self, fish) -> dict:
        repel_fish = extract_nearby_fish_names(fish.sub_env.repel_fish)
        align_fish = extract_nearby_fish_names(fish.sub_env.align_fish)
        follow_fish = extract_nearby_fish_names(fish.sub_env.follow_fish)
        return {'name': fish.name, 'species': fish.species, 'welfare': fish.welfare, 'position': fish.position,
                'rotation': fish.rotation, 'age': fish.age,
                'distance_to_closest_edge': fish.dist_to_closest_edge, 'repel_fish': repel_fish,
                'align_fish': align_fish, 'follow_fish': follow_fish}

    def get_ocean_metadata(self):
        pass
    #### JE something to describe ocean - particularly size

    def save_snapshot(self, output_name: str):
        """
        save png with ocean perimeter and positions of fish at time of calling
        :param output_name: filename to use
        :return: nothing
        """

        save_path = os.path.join(output_name)
        fig, ax = plt.subplots()
        # ax.set_facecolor(self.background_colour)
        self._add_ocean(ax)
        self._add_fishes(ax)

        plt.savefig(save_path)

    def _add_ocean(self, axis):
        """
        add ocean perimeter as patch
        :param axis: chart axis to add to
        :return: nothing
        """

        patches = []
        poly = Polygon(self.boundary, closed=True)
        patches.append(poly)
        p = PatchCollection(patches, alpha=0.3, facecolors=self.sea_colour)
        axis.add_collection(p)

        x_limit, y_limit = self._get_axes_limits()

        plt.xlim(x_limit)
        plt.ylim(y_limit)

    def _add_fishes(self, axis):
        """
        add fish to the chart as markers from png
        :param axis: chart axis to add to
        :return: nothing
        """
        for fish in self.population:
            if fish.welfare != 'dead':
                # fits image to be within certain bounding box on page
                x = (fish.position[0]-fish.size/2)
                y = (fish.position[1]-fish.size/2)
                bb = Bbox.from_bounds(x0=x, y0=y,
                                      width=fish.size, height=fish.size)
                # bb.rotate(fish.rotation)
                bb2 = TransformedBbox(bb, axis.transData)

                bbox_image = BboxImage(bb2, norm=None, origin=None, clip_on=False)
                bbox_image.set_data(fish.graph_marker)
                axis.add_artist(bbox_image)
                axis.annotate((fish.name, fish.unique_id), (x, y))

    def _get_axes_limits(self, buffer: float=0.1):
        """
        calculate appropriate axes limits for chart
        :param buffer: increase to add more white space around edge of ocean
        :return: lists: x axis limit, y axis limit
        """
        bbox = SpatialUtils.extract_bounding_box(self.boundary)
        min_x = bbox[0]
        max_x = bbox[2]
        min_y = bbox[1]
        max_y = bbox[3]
        x_diff = max_x - min_x
        x_buffer = x_diff*buffer
        y_diff = max_y - min_y
        y_buffer = y_diff * buffer
        x_limit = [min_x-x_buffer, max_x+x_buffer]
        y_limit = [min_y-y_buffer, max_y+y_buffer]
        return x_limit, y_limit


class Fish:
    def __init__(self, environment: OceanEnvironment, species: str, fish_type: str, fish_name: str=None,
                 initial_position: tuple=None, size=1, max_movement_radius=0,
                 repel_dist=0, align_dist=0, follow_dist=0,
                 place_attempts: int=3, fish_image_filepath: str='input/fish.png'):
        # ocean data
        self.environment = environment

        # fish characteristics
        self.image = plt.imread(fish_image_filepath)
        self.unique_id = self.generate_unique_id()
        self.species = species
        self.fish_type = fish_type
        self.size = size
        self.repel_distance = repel_dist  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = align_dist  # focal fish will seek to align direction with neighbours
        self.follow_distance = follow_dist  # focal fish will move towards a neighbour
        self.max_movement_radius = max_movement_radius
        self.age = 0
        self.name = self.choose_random_name() if fish_name is None else fish_name

        # fish positional information
        self.possible_moves = self.find_possible_moves_relative()
        # self.fish_pos = FishPosition(environment=self.environment, focal_fish=self)
        self.position = FishPosition(environment=self.environment, focal_fish=self).set_pos(place_attempts) if initial_position is None else initial_position
        self.position = (666, 666) if self.position is None else self.position  # give random position if not place
        self.rotation = self.choose_random_rotation()
        self.dist_to_closest_edge = self.distance_to_boundary()

        # fish characteristics that depend on positional information
        self.welfare = 'alive' if self.position != (666, 666) else 'dead'
        self.graph_marker = ndimage.rotate(self.image, self.rotation)

        # generate fish's local environment
        self.sub_env = NearbyWaters(fish=self, ocean=self.environment)

        # next move information
        self.incentive_to_move = 0
        self.next_move = None

        self.environment.population.append(self)

        logger.info('created {}: {}'.format(self.species, self.name))

    @staticmethod
    def choose_random_name():
        return random.choice(FISH_NAMES)

    def update_nearby_waters(self):
        self.sub_env = NearbyWaters(fish=self, ocean=self.environment)

    def find_possible_moves_relative(self):
        """
        finds list of moves that are within a fish's maximum movement radius
        cycles through all coordinate pairs of inside bounding box of centre coords +- circle_radius
            then compares whether coordinate generated is within the circle_radius
        :param circle_radius: circle_radius of circle to be considered
        :return: list of coordinates within a circle within radius = circle_radius
        """
        coords_within_radius = []
        test_list = []
        search_range = range(-self.max_movement_radius, self.max_movement_radius + 1)
        for num, x_increment in enumerate(search_range):
            for num2, y_increment in enumerate(search_range):
                test_coord = (x_increment, y_increment)
                dist_to_centre = SpatialUtils.calc_distance(test_coord, (0, 0))
                if dist_to_centre <= self.max_movement_radius:
                    test_list.append((num, num2))
                    coords_within_radius.append(test_coord)
        return coords_within_radius

    @staticmethod
    def choose_random_rotation():
        available_rotations = tuple(range(0, 360, 45))
        print(available_rotations)
        return random.choice(available_rotations)

    def generate_unique_id(self):
        return len(self.environment.population) + 1

    def distance_to_boundary(self):
        self.dist_to_closest_edge = SpatialUtils.distance_to_boundary(self.position, self.environment.boundary)
        return self.dist_to_closest_edge

    def choose_next_move(self):
        """choose next move at random from available moves"""
        self.update_nearby_waters()
        repel_fish = extract_nearby_fish_names(self.sub_env.repel_fish)
        align_fish = extract_nearby_fish_names(self.sub_env.align_fish)
        follow_fish = extract_nearby_fish_names(self.sub_env.follow_fish)
        if len(repel_fish) > 0:
            # update this with a more intelligent route to take - perhaps just away from the repel fish
            chosen_move = random.choice(self.sub_env.available_moves)
            logger.debug('{} ({}) panicked and tried to swim away from: {}'.format(self.name, self.unique_id,
                                                                                   repel_fish))
        elif len(align_fish) > 0:
            # if want to align, stay in same location, just change rotation to match that of average rotation of group
            chosen_move = self.position
            new_rotation = np.mean([x.rotation for x in self.sub_env.align_fish])
            logger.debug('{} ({}) wants to align with: {}'.format(self.name, self.unique_id, align_fish))
            self.rotation = new_rotation
            self.graph_marker = ndimage.rotate(self.image, self.rotation)
        elif len(follow_fish) > 0:
            chosen_move = self.position
        # self.incentive_to_move = self.incentive_to_move - 1
        else:
            chosen_move = self.position
        return chosen_move


class Snapper(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None,
                 initial_position: tuple=None):
        super().__init__(environment=environment, species='snapper', fish_type='prey',
                         initial_position=initial_position,
                         fish_name=fish_name, size=5, max_movement_radius=10, repel_dist=1,
                         align_dist=3, follow_dist=10)


class Whale(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None, initial_position: tuple=None):
        super().__init__(environment=environment, species='whale', fish_type='predator',
                         initial_position=initial_position,
                         fish_name=fish_name, size=15, max_movement_radius=10, repel_dist=1,
                         align_dist=3, follow_dist=15)


class NearbyWaters:
    def __init__(self, fish: Fish, ocean: OceanEnvironment):
        """
        this class assesses the relevant environment around a fish i.e. the environment that will affect its movement
            this should be evaluated for each fish for each move
        :param fish:
        :param ocean:
        """
        self.fish = fish
        self.ocean = ocean
        self.centre_coordinates = self.fish.position
        self.environ_radius = self.fish.follow_distance

        self.repel_fish, self.align_fish, self.follow_fish = FishPosition(self.ocean, self.fish).find_nearby_fish()
        self.all_nearby_fish = self.repel_fish + self.align_fish + self.follow_fish
        self.predator_count = 0 if self.fish.fish_type == 'predator' else self.count_predators()

        self.available_moves = self.update_available_moves()

    def count_predators(self):
        predator_count = 0
        for fsh in self.all_nearby_fish:
            if fsh.fish_type == 'predator':
                predator_count += 1
        self.predator_count = predator_count
        return predator_count

    def update_available_moves(self) -> list:
        if self.fish.welfare == 'dead':
            empty_coordinates = [(666, 666)]
        else:
            coords_within_radius = [(i[0] + self.fish.position[0], i[1] + self.fish.position[1]) for i in
                                    self.fish.possible_moves]
            environ_coordinates = self.find_coordinates_within_sub_environment(coords_within_radius, self.ocean.boundary)
            empty_coordinates = self.find_empty_coordinates(all_coordinates=environ_coordinates,
                                                            nearby_fish=self.all_nearby_fish)
        return empty_coordinates

    @staticmethod
    def find_coordinates_within_sub_environment(coordinate_list: list, environment_boundary: tuple) -> list:
        """
        fish which of a list of coordinates are inside the polygon
        :param coordinate_list: coordinates to be assessed
        :param environment_boundary: polygon boundary which the coordinates are to be compared to
        :return: list of coordinates within the environment
        """
        coords_within_env = []
        for coord in coordinate_list:
            if SpatialUtils.poly_contains_point(coordinates=coord, polygon=environment_boundary, method='winding'):
                coords_within_env.append(coord)
        return coords_within_env

    def find_empty_coordinates(self, all_coordinates: list, nearby_fish: list) -> list:
        """
        finds which coordinates are not occupied, also considering focal and neighbouring fish size
        :param all_coordinates: all coordinates to be considered
        :param nearby_fish: list of fish within sub-environment
        :return: list with all empty coordinates within sub-environment
        """
        updated_coordinate_list = all_coordinates
        for coord in all_coordinates:
            for fsh in nearby_fish:
                space_necessary = self.fish.size + fsh.size
                if SpatialUtils.calc_distance(coord, fsh.position) < space_necessary:
                    updated_coordinate_list.remove(coord)
                break
        return updated_coordinate_list


class FishPosition:
    def __init__(self, environment: OceanEnvironment, focal_fish: Fish):
        self.environment = environment
        self.fish = focal_fish

    def set_pos(self, place_attempts) -> tuple:
        """set the position of the fish in the environment, try n times before giving up"""
        bbox = SpatialUtils.extract_bounding_box(self.environment.boundary)
        for attempt in range(place_attempts):
            self.fish.position = self.generate_random_position(bounding_box=bbox, full_boundary=self.environment.boundary)
            logger.debug(
                'position generated for {} ({}): {}'.format(self.fish.name, self.fish.unique_id, self.fish.position))
            if self.fish.position is not None:
                other_fish = self.find_all_other_fish()
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

    def generate_random_position(self, bounding_box: tuple, full_boundary: tuple) -> tuple:
        """
        generate random starting position within bounding box of environment
        :param bounding_box: bounding box to generate within
        :param full_boundary: boundary coordinates of area
        :return: coordinates of position generated if within the area, else None
        """
        proposed_starting_pos = (random.randint(bounding_box[0], bounding_box[2]),
                                 random.randint(bounding_box[1], bounding_box[3]))
        if SpatialUtils.poly_contains_point(coordinates=proposed_starting_pos, polygon=full_boundary,
                                            method='winding'):
            logger.info('sploosh! {} ({}) landed in the water! {}'.format(self.fish.name, self.fish.unique_id,
                                                                          proposed_starting_pos))
            return proposed_starting_pos
        else:
            logger.info('flop! {} ({}) cannot swim outside of the ocean: {}'.format(self.fish.name, self.fish.unique_id, proposed_starting_pos))

    def find_nearby_fish(self) -> tuple:
        """
        find all fish within the follow distance of the focal fish (i.e. all fish the focal fish can see)
        find all fish within the repel distance of the focal fish (i.e. all fish the focal fish can see)
        find all fish within the align distance of the focal fish (i.e. all fish the focal fish can see)
            distance includes subtractions of the size of each fish to account for fish being visible not just on
            the single coordinate they occupy
        :return: fish that are within this zone
        """
        all_other_fish = self.find_all_other_fish()
        follow_fish = []
        align_fish = []
        repel_fish = []
        for other_fish in all_other_fish:
            ## exclude those that are out range without
            # if (abs(self.fish.position[0] - self.fish.position[0]) > self.fish.follow_distance) or (
            #     abs(self.fish.position[1] - self.fish.position[1]) > self.fish.follow_distance):
            #     continue
            distance_between_fish = SpatialUtils.calc_distance(self.fish.position, other_fish.position)
            # account for sizes of fish
            distance_between_fish = distance_between_fish - self.fish.size - other_fish.size
            if distance_between_fish <= self.fish.repel_distance:
                repel_fish.append(other_fish)
            elif distance_between_fish <= self.fish.align_distance:
                align_fish.append(other_fish)
            elif distance_between_fish <= self.fish.follow_distance:
                follow_fish.append(other_fish)
        return repel_fish, align_fish, follow_fish

    def detect_fish_collision(self, coordinates: tuple, comparison_group: list) -> bool:
        """
        cycles through and compares coordinates against other group of fish, assessing
            whether fish is closer than the maximum radius of the two fish
        :param coordinates: coordinates of focal fish
        :param comparison_group: group to compare against
        :return: true if there is a collision
        """
        for other in comparison_group:
            distance_between = SpatialUtils.calc_distance(coordinates, other.position)
            if distance_between < max([self.fish.size, other.size]):
                logger.debug('collision between fish: {} ({}), and: {} ({})'.format(self.fish.name, self.fish.unique_id,
                                                                                    other.name, other.unique_id))
                return True

    def detect_edge_collision(self):
        pass

    def find_all_other_fish(self) -> list:
        """find other fish in their current positions
            remove current fish and dead fish from list of fish being considered
        """
        other_fish = []
        for fish in self.environment.population:
            if fish.unique_id != self.fish.unique_id and fish.welfare != 'dead':
                other_fish.append(fish)
        return other_fish


def extract_nearby_fish_names(fish_list: list) -> list:
    """cycles through fish list and extracts name and ID to make it easier to cross ref"""
    out_list = []
    for fsh in fish_list:
        out_list.append((fsh.name, fsh.unique_id))
    return out_list




