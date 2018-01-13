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
              'chomper', 'antonella', 'auntie jane']


class OceanEnvironment:
    def __init__(self, bounding_coordinates: tuple):
        """
        :param bounding_coordinates: should be tuple of tuples (x, y) listed in counterclockwise direction
            ending with the first coordinate to close path
        """
        self.boundary = bounding_coordinates
        self.population = []
        self.populated_sorted = self._sort_population_according_to_incentive()
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

    def let_time_pass(self, moves_in_time_period: int):
        """
        first recalculate all fish's incentives to move
        find fish who want to move most
        :param moves_in_time_period: number of moves for each fish
        :return: nothing, just output logs
        """
        for move in range(moves_in_time_period):
            logger.info('\n move: {}'.format(move))
            for fsh_num in range(len(self.population)):
                agitated_fish = self.population[fsh_num]
                initial_position = agitated_fish.position
                initial_rotation = agitated_fish.rotation
                next_pos = agitated_fish.choose_next_move()
                next_rotation = agitated_fish.rotation
                agitated_fish.position = next_pos
                dist = SpatialUtils.calc_distance(initial_position, next_pos)
                logger.debug(
                    '{} ({}) moved from {} to {}, distance: {}, rotation from {} to {}'.format(agitated_fish.name,
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
        # TODO something to describe ocean - particularly size
        pass

    def save_snapshot(self, output_name: str):
        """
        save png with ocean perimeter and positions of fish at time of calling
        :param output_name: filename to use
        :return: nothing
        """

        save_path = os.path.join(output_name)
        fig, ax = plt.subplots()
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
    def __init__(self, environment: OceanEnvironment, species: str, eats_fish: tuple=(), fish_name: str=None,
                 initial_position: tuple=None, size=1, max_movement_radius=0,
                 repel_dist=0, align_dist=0, follow_dist=0,
                 place_attempts: int=3, fish_image_filepath: str = 'input/fish.png'):
        """
        :param environment: the ocean that the fish lives in
        :param species: the type of fish
        :param eats_fish: the type of fish that this fish can eat
        :param fish_name: this fish's name e.g. Joe
        :param initial_position: the coordinates where this fish will be spawned
        :param size: the size of this fish
        :param max_movement_radius: how far this fish can move in a single turn
        :param repel_dist: the max distance which the focal fish believes is too close to other fish
        :param align_dist: within this distance (and greater than repel distance), the focal fish will want to
            align with other fish of the same species
        :param follow_dist: within this distance (and greater than the align distance), the focal fish will want to
            get closer to other fish of the same species
        :param place_attempts: the number of times that will try to spawn the fish before the fish dies
        :param fish_image_filepath: the path to the image of the file
        """

        # ocean data
        self.environment = environment

        # fish characteristics
        self.image = plt.imread(fish_image_filepath)
        self.unique_id = self.generate_unique_id()
        self.species = species
        self.eats_fish = eats_fish  # preys on these fish species
        self.size = size
        self.repel_distance = repel_dist  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = align_dist  # focal fish will seek to align direction with neighbours
        self.follow_distance = follow_dist  # focal fish will move towards a neighbour
        self.max_movement_radius = max_movement_radius
        self.age = 0
        self.name = self.choose_random_name() if fish_name is None else fish_name

        # fish positional information
        self.possible_moves = self.find_possible_moves_relative()
        self.position = self.set_pos(place_attempts) if initial_position is None else initial_position
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
        return random.choice(available_rotations)

    def generate_unique_id(self):
        return len(self.environment.population) + 1

    def distance_to_boundary(self):
        self.dist_to_closest_edge = SpatialUtils.distance_to_boundary(self.position, self.environment.boundary)
        return self.dist_to_closest_edge

    def choose_next_move(self):
        """"""
        def create_move_options(central_coordinate: tuple, shift_num: int) -> list:
            """creates four coordinates around a central coordinate - above, below, left, right"""
            return [(central_coordinate[0], central_coordinate[1] + shift_num),
                    (central_coordinate[0], central_coordinate[1] - shift_num),
                    (central_coordinate[0] + shift_num, central_coordinate[1]),
                    (central_coordinate[0] - shift_num, central_coordinate[1])]

        self.update_nearby_waters()
        # only move if it has somewhere it can go else stay in the same location
        if len(self.sub_env.available_moves) > 0:
            if len(self.sub_env.repel_fish) > 0:
                repel_fish = extract_nearby_fish_names(self.sub_env.repel_fish)
                move_to_try, self.rotation = self._move_repel()
                logger.debug('{} ({}) panicked and tried to swim away from: {}'.format(self.name, self.unique_id,
                                                                                       repel_fish))
            elif len(self.sub_env.align_fish) > 0:
                align_fish = extract_nearby_fish_names(self.sub_env.align_fish)
                move_to_try, self.rotation = self._move_align()
                self.graph_marker = ndimage.rotate(self.image, self.rotation)  # update graph marker with new rotation
                logger.debug('{} ({}) wants to align with: {}'.format(self.name, self.unique_id, align_fish))
            elif len(self.sub_env.follow_fish) > 0:
                follow_fish = extract_nearby_fish_names(self.sub_env.follow_fish)
                move_to_try, self.rotation = self._move_follow()
                logger.debug('{} ({}) wants to follow: {}'.format(self.name, self.unique_id, follow_fish))
            else:
                move_to_try, self.rotation = self._move_random()
                logger.debug('{} ({}) could not see other fish so moved randomly'.format(self.name, self.unique_id))

            # round to integer coordinate
            rounded_move_to_try = (int(move_to_try[0]), int(move_to_try[1]))

            # try a maximum of n shift attempts
            shift_attempts = 10
            for shift_attempt in range(shift_attempts):
                shifted_moves = create_move_options(rounded_move_to_try, shift_attempt)
                # loop through move options randomly choosing each time (thereby keeping element of randomness)
                shift_direction = 0
                while shift_direction < 4 and move_to_try not in self.sub_env.available_moves:
                    move_to_try = random.choice(shifted_moves)
                    shift_direction += 1
                    shifted_moves.remove(move_to_try)
                if len(shifted_moves) > 0:  # if there are moves left it implies one was available so break loop
                    self.position = move_to_try
                    break
            if shift_attempt == shift_attempts - 1:
                logger.debug('{} ({}) could not find anywhere to move so chilled out'.format(self.name,
                                                                                             self.unique_id))
        return self.position

    def _move_repel(self) -> tuple:
        """
        find average direction to repel fish, move in opposite direction to average repel fish direction,
            calculate the ideal location for the fish to move based on the above angle and max travel distance
        :return: the optimal location to move to, note that this location may not be available (e.g. occupied)
        """
        dir_to_fish = np.mean([SpatialUtils.calc_angle(self.position, other_fish.position) for other_fish in
                               self.sub_env.repel_fish])
        opposite_dir = dir_to_fish - 180  # move away from close fish
        optimal_move = SpatialUtils.new_position_angle_length(starting_coordinates=self.position, angle=opposite_dir,
                                                              distance=self.max_movement_radius)
        return optimal_move, self.rotation

    def _move_align(self) -> tuple:
        # if want to align, stay in same location, just change rotation to match that of average rotation of group
        new_rotation = np.mean([x.rotation for x in self.sub_env.align_fish])

        dist_to_closest = np.min([SpatialUtils.calc_distance(self.position, other_fish.position) for other_fish in
                                  self.sub_env.align_fish])
        # aim to move some distance between the repel and align distance from the nearest fish
        # use random choice from 4 intervals in this range
        move_dist = random.choice(
            [x for x in np.arange(dist_to_closest - self.size - self.align_distance,
                                  dist_to_closest - self.size - self.repel_distance + 1, step=4)])
        optimal_move = SpatialUtils.new_position_angle_length(starting_coordinates=self.position, angle=new_rotation,
                                                              distance=move_dist)
        return optimal_move, int(new_rotation)

    def _move_follow(self) -> tuple:
        """
        find average direction to follow fish, move in that direction so that align distance away from closest
            follow fish
        :return: the optimal location to move to, note that this location may not be available (e.g. occupied)
        """
        dir_to_fish = np.mean([SpatialUtils.calc_angle(self.position, other_fish.position) for other_fish in
                               self.sub_env.follow_fish])
        dist_to_closest = np.min([SpatialUtils.calc_distance(self.position, other_fish.position) for other_fish in
                                  self.sub_env.follow_fish])
        # aim to move some distance between the repel and align distance from the nearest fish
        # use random choice from 4 intervals in this range
        move_dist = random.choice(
            [x for x in np.arange(dist_to_closest - self.size - self.align_distance,
                                  dist_to_closest - self.size - self.repel_distance + 1, step=4)])
        optimal_move = SpatialUtils.new_position_angle_length(starting_coordinates=self.position, angle=dir_to_fish,
                                                              distance=move_dist)
        return optimal_move, self.rotation

    def _move_random(self) -> tuple:
        random_position = random.choice(self.sub_env.available_moves)

        return random_position, self.rotation

    def set_pos(self, place_attempts) -> tuple:
        """set the position of the fish in the environment, try n times before giving up"""
        bbox = SpatialUtils.extract_bounding_box(self.environment.boundary)
        for attempt in range(place_attempts):
            # generate random coordinate within bounding box
            proposed_postion = (random.randint(bbox[0], bbox[2]), random.randint(bbox[1], bbox[3]))
            # check if it is within the polygon (i.e. the ocean)
            if SpatialUtils.poly_contains_point(coordinates=proposed_postion, polygon=self.environment.boundary,
                                                method='winding'):
                logger.info('sploosh! {} ({}) landed in the water! {}'.format(self.name, self.unique_id,
                                                                              proposed_postion))
                return proposed_postion
            else:
                logger.info('flop! {} ({}) cannot swim outside of the ocean: {}'.format(self.name, self.unique_id,
                                                                                        proposed_postion))


class Snapper(Fish):
    def __init__(self, environment: OceanEnvironment, fish_name: str=None, initial_position: tuple=None):
        super().__init__(environment=environment, species='snapper', initial_position=initial_position,
                         fish_name=fish_name, size=5, max_movement_radius=10, repel_dist=2,
                         align_dist=5, follow_dist=10, eats_fish=())


class Whale(Fish):
    def __init__(self, environment: OceanEnvironment, fish_name: str=None, initial_position: tuple=None):
        super().__init__(environment=environment, species='whale', initial_position=initial_position,
                         fish_name=fish_name, size=15, max_movement_radius=10, repel_dist=1,
                         align_dist=3, follow_dist=15, eats_fish=('Snapper', ))


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

        self.repel_fish, self.align_fish, self.follow_fish = self.find_nearby_fish()
        self.all_nearby_fish = self.repel_fish + self.align_fish + self.follow_fish
        self.predator_count = self.count_predators()

        self.available_moves = self.update_available_moves()

    def count_predators(self):
        """return number of predators of that fish type within a fish's 'follow range'"""
        predator_count = 0
        for fsh in self.all_nearby_fish:
            if self.fish.species in fsh.eats_fish:
                predator_count += 1
        self.predator_count = predator_count
        return predator_count

    def update_available_moves(self) -> list:
        """return the moves that are within fish's movement radius, not occupied by other fish, and within the
                boundary
                """
        if self.fish.welfare == 'dead':
            empty_coordinates = [(666, 666)]
        else:
            coords_within_radius = [(i[0] + self.fish.position[0], i[1] + self.fish.position[1]) for i in
                                    self.fish.possible_moves]
            environ_coordinates = self.find_coordinates_within_sub_environment(coords_within_radius,
                                                                               self.ocean.boundary)
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
        if len(nearby_fish) == 0:  # if no fish nearby
            updated_coordinate_list = all_coordinates
        else:
            updated_coordinate_list = []
            for coord in all_coordinates:
                for fsh in nearby_fish:
                    space_necessary = self.fish.size
                    if SpatialUtils.calc_distance(coord, fsh.position) >= space_necessary:
                        updated_coordinate_list.append(coord)
        return updated_coordinate_list

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
            distance_between_fish = SpatialUtils.calc_distance(self.fish.position, other_fish.position)
            distance_between_fish = distance_between_fish - self.fish.size
            if distance_between_fish <= self.fish.repel_distance:
                repel_fish.append(other_fish)
            elif self.fish.align_distance >= distance_between_fish > self.fish.repel_distance \
                    and self.fish.species == other_fish.species:
                align_fish.append(other_fish)
            elif self.fish.follow_distance >= distance_between_fish > self.fish.align_distance \
                    and self.fish.species == other_fish.species:
                follow_fish.append(other_fish)
        return repel_fish, align_fish, follow_fish

    def find_all_other_fish(self) -> list:
        """find other fish in their current positions
            remove current fish and dead fish from list of fish being considered
        """
        other_fish = []
        for fish in self.ocean.population:
            if fish.unique_id != self.fish.unique_id and fish.welfare != 'dead':
                other_fish.append(fish)
        return other_fish


def extract_nearby_fish_names(fish_list: list) -> list:
    """cycles through fish list and extracts name and ID to make it easier to cross ref"""
    out_list = []
    for fsh in fish_list:
        out_list.append((fsh.name, fsh.unique_id))
    return out_list




