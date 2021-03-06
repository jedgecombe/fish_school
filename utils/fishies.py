import logging
import math
import random

import matplotlib as mpl
from matplotlib.path import Path
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

from utils.environ import OceanEnvironment, FishMongers
from utils.positioning import NearbyWaters
from utils.spatial_utils import SpatialUtils

logger = logging.getLogger(__name__)


class Fish:
    def __init__(self, name_options: list, eats_fish: tuple=(), size=1, colour='white', cluster_colour='black',
                 max_movement_radius=0,
                 repel_dist=0, align_dist=0, follow_dist=0):
        """
        :param eats_fish: the type of fish that this fish can eat
        :param size: the size of this fish
        :param colour: colour of fish when not in shoal
        :param cluster_colour: colour of fish when in shoal
        :param max_movement_radius: how far this fish can move in a single turn
        :param repel_dist: the max distance which the focal fish believes is too close to other fish
        :param align_dist: within this distance (and greater than repel distance), the focal fish will want to
            align with other fish of the same species
        :param follow_dist: within this distance (and greater than the align distance), the focal fish will want to
            get closer to other fish of the same species
        """

        # ocean data
        self.environment = OceanEnvironment(bounding_coordinates=(), minimum_shoal_size=2)

        # fish characteristics
        self.unique_id = None
        self.colour = colour
        self.cluster_colour = cluster_colour
        self.current_colour = self.colour
        self.eats_fish = eats_fish  # preys on these fish species
        self.size = size
        self.repel_distance = repel_dist  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = align_dist  # focal fish will seek to align direction with neighbours
        self.follow_distance = follow_dist  # focal fish will move towards a neighbour
        self.max_movement_radius = max_movement_radius
        self.age = 0
        self.name = random.choice(name_options)
        self.shoal_id = None

        # fish positional information
        self.position = []
        self.previous_position = []
        self.rotation = 0
        self.dist_to_closest_edge = 9999999

        # generate fish's local environment
        self.sub_env = None

        # next move information
        self.incentive_to_move = 0

        # memory of what has gone before
        self.memory = []

    def make_it_rain(self, ocean: OceanEnvironment, graveyard: FishMongers, initial_position: tuple=None,
                     place_attempts: int=3):
        """aim to add to ocean"""
        self.unique_id = len(ocean.population) + len(graveyard.population)
        self.position = self.set_pos(place_attempts, ocean) if initial_position is None else initial_position
        # previous_position = position initially as there is no previous position
        self.previous_position = self.position

        # if positioning is unsuccessful, add to graveyard
        if self.position is None:
            graveyard.population.append(self)
            self.environment = graveyard
        # else add to ocean and update fish metadata
        else:
            ocean.population.append(self)
            self.environment = ocean
            # random starting location
            self.rotation = self._update_rotation(random.choice(tuple(range(0, 360, 45))))
            self.dist_to_closest_edge = self.distance_to_boundary()
            self.sub_env = NearbyWaters(fish=self, ocean=self.environment)

    def set_pos(self, place_attempts, target_ocean: OceanEnvironment) -> tuple:
        """set the position of the fish in the environment, try n times before giving up"""
        bbox = SpatialUtils.extract_bounding_box(target_ocean.boundary)
        for attempt in range(place_attempts):
            # generate random coordinate within bounding box
            proposed_position = [random.randint(bbox[0], bbox[2]), random.randint(bbox[1], bbox[3])]
            # check if it is within the polygon (i.e. the ocean)
            if SpatialUtils.poly_contains_point(coordinates=proposed_position, polygon=target_ocean.boundary,
                                                method='winding'):
                logger.info(f'sploosh! {self.name} ({self.unique_id}) landed in the water! {proposed_position}. '
                            f'Place attempt: {attempt + 1}')
                return proposed_position
            else:
                logger.info(f'flop! {self.name} ({self.unique_id}) cannot swim outside of the ocean: '
                            f'{proposed_position}. Place attempt: {attempt + 1}')

    def update_nearby_waters(self):
        """update knowledge of surroundings including other fish and available moves"""
        self.sub_env = NearbyWaters(fish=self, ocean=self.environment)

    def distance_to_boundary(self):
        return SpatialUtils.distance_to_boundary(self.position, self.environment.boundary)

    def swim(self, max_move_attempts: int=30) -> None:
        def create_move_options(central_coordinate: list, shift_num: int) -> list:
            """creates four coordinates around a central coordinate - above, below, left, right"""
            return [[central_coordinate[0], central_coordinate[1] + shift_num],
                    [central_coordinate[0], central_coordinate[1] - shift_num],
                    [central_coordinate[0] + shift_num, central_coordinate[1]],
                    [central_coordinate[0] - shift_num, central_coordinate[1]]]

        # becomes aware of environment
        self.update_nearby_waters()
        preferred_alignment = None  # unless overwritten alignment to be decided based on movement direction
        # only move if it has somewhere it can go else stay in the same location
        if len(self.sub_env.available_moves) == 0:
            logger.debug(f'{self.name} ({self.unique_id}) could not move so just chilled at: {self.position}')
            move_description = 'stuck'
            preferred_move = self.position
        # if it can move, find it's preferred move
        elif len(self.sub_env.repel_fish) > 0:
            repel_fish = self.sub_env.extract_nearby_fish_names(self.sub_env.repel_fish)
            preferred_move = self._move_repel()
            move_description = 'repel'
            logger.debug(f'{self.name} ({self.unique_id}) panicked and tried to swim away from: {repel_fish}')
        elif len(self.sub_env.align_fish) > 0:
            align_fish = self.sub_env.extract_nearby_fish_names(self.sub_env.align_fish)
            preferred_move, preferred_alignment = self._move_align()
            move_description = 'align'
            logger.debug(f'{self.name} ({self.unique_id}) wants to align with: {align_fish}')
        elif len(self.sub_env.follow_fish) > 0:
            follow_fish = self.sub_env.extract_nearby_fish_names(self.sub_env.follow_fish)
            preferred_move = self._move_follow()
            move_description = 'follow'
            logger.debug(f'{self.name} ({self.unique_id}) wants to follow: {follow_fish}')
        else:
            preferred_move = self._move_random()
            move_description = 'random'
            logger.debug(f'{self.name} ({self.unique_id}) could not see other fish so moved randomly')

        # round to integer coordinate
        preferred_move_rounded = [int(preferred_move[0]), int(preferred_move[1])]

        # try a maximum of n shift attempts
        # can fish move where it wants to? If it can't try a move nearby
        for shift_attempt in range(max_move_attempts):
            move_options = create_move_options(preferred_move_rounded, shift_attempt)
            # loop through move options randomly choosing each time (thereby keeping element of randomness)
            move_to_try = random.choice(move_options)
            move_options.remove(move_to_try)
            # choose if this move is available
            avail = self.sub_env.available_moves
            if move_to_try in self.sub_env.available_moves:
                movement_direction = SpatialUtils.calc_angle(self.position, move_to_try)
                rotation = movement_direction if preferred_alignment is None else preferred_alignment
                self.previous_position = self.position
                self.position = move_to_try
                self.age += 1
                break
        else:
            logger.debug(f'{self.name} ({self.unique_id}) could not find anywhere to move so chilled out')
            rotation = self.rotation
            self.previous_position = self.position
            move_description = 'moves available but stuck'
            logger.debug('available moves: ')

        dist = SpatialUtils.calc_distance(self.position, self.previous_position)

        logger.debug(f'{self.name} ({self.unique_id}) move description: \n'
                     f' primary motivation: {move_description} \n'
                     f' move choice: ({shift_attempt + 1} / {max_move_attempts}) \n'
                     f' moved from: {self.previous_position} to {self.position} (distance = {dist}) \n'
                     f' rotation from: {round(self.rotation, 0)} to {round(rotation, 0)} \n'
                     f' new shoal id: {self.shoal_id}')
        self.create_memory(move_description=move_description, new_rotation=rotation,
                           move_distance=dist)
        self.rotation = self._update_rotation(rotation)

    def create_memory(self, move_description, new_rotation, move_distance):
        memory = {
            'move_descr': move_description,
            'position_pre': self.previous_position,
            'position_post': self.position,
            'move_distance': move_distance,
            'rotation_pre': self.rotation,
            'rotation_post': new_rotation,
            'shoal_id': self.shoal_id,
            'age': self.age,
            'follow_fish': self.sub_env.follow_fish,
            'align_fish': self.sub_env.align_fish,
            'repel_fish': self.sub_env.repel_fish,
        }
        self.memory.append(memory)

    def _update_rotation(self, target_degrees: float):
        # """update degrees so that 0 degrees is facing upwards"""
        self.custom_marker = self.custom_marker.transformed(mpl.transforms.Affine2D().rotate_deg(target_degrees))
        return target_degrees

    def _move_repel(self) -> float:
        """
        find average direction to repel fish, move in opposite direction to average repel fish direction,
            calculate the ideal location for the fish to move based on the above angle and max travel distance
        :return: the optimal location to move to, note that this location may not be available (e.g. occupied)
        """
        dir_to_fish = np.mean([SpatialUtils.calc_angle(self.position, other_fish.position) for other_fish in
                               self.sub_env.repel_fish]).item()
        opposite_dir = dir_to_fish - 180  # move away from close fish
        optimal_move = SpatialUtils.new_position_angle_length(starting_coordinates=self.position, angle=opposite_dir,
                                                              distance=self.max_movement_radius)
        return optimal_move

    def _move_align(self) -> tuple:
        # if want to align, stay in same location, just change rotation to match that of average rotation of group
        new_rotation = np.mean([x.rotation for x in self.sub_env.align_fish]).item()

        dist_to_closest = np.min([SpatialUtils.calc_distance(self.position, other_fish.position) for other_fish in
                                  self.sub_env.align_fish])
        # aim to move some distance between the repel and align distance from the nearest fish
        # use random choice from 4 intervals in this range
        move_dist = random.choice(
            [x for x in np.arange(dist_to_closest - self.align_distance,
                                  dist_to_closest - self.repel_distance + 1, step=4)])
        optimal_move = SpatialUtils.new_position_angle_length(starting_coordinates=self.position, angle=new_rotation,
                                                              distance=move_dist)
        return optimal_move, None

    def _move_follow(self) -> float:
        """
        find average direction to follow fish, move in that direction so that align distance away from closest
            follow fish
        :return: the optimal location to move to, note that this location may not be available (e.g. occupied)
        """
        dir_to_fish = np.mean([SpatialUtils.calc_angle(self.position, other_fish.position) for other_fish in
                               self.sub_env.follow_fish]).item()
        dist_to_closest = np.min([SpatialUtils.calc_distance(self.position, other_fish.position) for other_fish in
                                  self.sub_env.follow_fish]).item()
        # aim to move some distance between the repel and align distance from the nearest fish
        # use random choice from 4 intervals in this range
        move_dist = random.choice(
            [x for x in np.arange(dist_to_closest - self.align_distance,
                                  dist_to_closest - self.repel_distance + 0.0001, step=4)])
        optimal_move = SpatialUtils.new_position_angle_length(starting_coordinates=self.position, angle=dir_to_fish,
                                                              distance=move_dist)
        return optimal_move

    def _move_random(self) -> float:
        """
        aim to move randomly among the moves within the range of the fish
        :return: the optimal location to move to, note that this location may not be available (e.g. occupied)
        """
        random_position = random.choice(self.sub_env.available_moves)

        return random_position


# class Predator(Fish):
#     def __init__(self, environment: OceanEnvironment):
#         super().__init__(environment=environment)


class Snapper(Fish):
    def __init__(self, name_options: list):
        super().__init__(size=10, max_movement_radius=10, repel_dist=2, colour='#fcba76', cluster_colour='#FF8100',
                         align_dist=5, follow_dist=30, eats_fish=(), name_options=name_options)
        verts = [
            (-5., -4.),  # left, bottom of tail
            (-2., -1.),  # left, top of tail
            (-4., 3.),  # leftmost part of head
            (0., 7.),  # top of head
            (4., 3.),  # rightmost part of head
            (2., -1.),  # right, top of tail
            (5., -4.),  # right, bottom of tail
            (0., 0.),  # ignored - incl. for close poly arg
        ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.CLOSEPOLY]
        self.custom_marker = Path(verts, codes)


class Shark(Fish):
    def __init__(self, name_options: list):
        super().__init__(size=30, max_movement_radius=20, repel_dist=1, colour='#D1D7D7', cluster_colour='#8C9B9B',
                         align_dist=3, follow_dist=15, eats_fish=(Snapper, ), name_options=name_options)
        verts = [
            (-4., -7.),  # left, bottom of tail
            (-1., -1.),  # left, top of tail
            (-3., 3.),  # leftmost part of head
            (0., 7.),  # top of head
            (3., 3.),  # rightmost part of head
            (1., -1.),  # right, top of tail
            (4., -7.),  # right, bottom of tail
            (0., 0.),  # ignored - incl. for close poly arg
        ]

        codes = [Path.MOVETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.LINETO,
                 Path.CLOSEPOLY]
        self.custom_marker = Path(verts, codes)
