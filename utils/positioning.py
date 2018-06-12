import logging

import numpy as np

from utils.environ import OceanEnvironment
from utils.spatial_utils import SpatialUtils

logger = logging.getLogger(__name__)


class NearbyWaters:
    def __init__(self, fish, ocean: OceanEnvironment):
        """
        this class assesses the relevant environment around a fish i.e. the environment that will affect its movement
            this should be evaluated for each fish for each move
        :param fish:
        :param ocean:
        """
        self.fish = fish
        self.ocean = ocean

        self.repel_fish, self.align_fish, self.follow_fish = self.find_nearby_fish()
        self.all_nearby_fish = self.repel_fish + self.align_fish + self.follow_fish
        self.predator_count = self.count_predators()

        self.available_moves = self.update_available_moves()

    def count_predators(self):
        """return number of predators of that fish type within a fish's 'follow range'"""
        predator_count = 0
        for fsh in self.all_nearby_fish:
            if type(self.fish) in fsh.eats_fish:
                predator_count += 1
        self.predator_count = predator_count
        return predator_count

    def update_available_moves(self) -> list:
        """return the moves that are within fish's movement radius, not occupied by other fish, and within the
                boundary
        """
        # find coordinates within range of fish
        pos = self.fish.position
        coords_within_radius = self.find_moves_within_max_range()
        environ_coordinates = self.find_coordinates_within_sub_environment(coords_within_radius, self.ocean.boundary)
        empty_coordinates = self.find_empty_coordinates(all_coordinates=environ_coordinates,
                                                        nearby_fish=self.all_nearby_fish)
        return empty_coordinates

    def find_moves_within_max_range(self) -> list:
        """
        searches a rectangle of points within a fish's maximum movement radius (from point 0, 0)
          then adds them
        finds list of moves that are within a fish's maximum movement radius
        cycles through all coordinate pairs of inside bounding box of centre coords +- circle_radius
            then compares whether coordinate generated is within the circle_radius
        :return: list of coordinates within a circle within radius = circle_radius
        """
        coords_within_radius = []
        # create a range to search, normalised based on how far fish can move to stop range getting enormous
        search_range = np.arange(start=-self.fish.max_movement_radius, stop=self.fish.max_movement_radius + 0.001,
                                 step=1)
        for x_increment in search_range:
            for y_increment in search_range:
                test_coord = [x_increment, y_increment]
                dist_to_centre = SpatialUtils.calc_distance(test_coord, [0, 0])
                if dist_to_centre <= self.fish.max_movement_radius:
                    adj_coord = [test_coord[0] + self.fish.position[0], test_coord[1] + self.fish.position[1]]
                    coords_within_radius.append(adj_coord)
        return coords_within_radius

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
                    space_necessary = self.fish.size / 2
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
                    and type(self.fish) == type(other_fish):
                align_fish.append(other_fish)
            elif self.fish.follow_distance >= distance_between_fish > self.fish.align_distance \
                    and type(self.fish) == type(other_fish):
                follow_fish.append(other_fish)
        return repel_fish, align_fish, follow_fish

    def find_all_other_fish(self) -> list:
        """
        find other fish in their current positions
            remove current fish and dead fish from list of fish being considered
        """
        other_fish = []
        for fish in self.ocean.population:
            if fish.unique_id != self.fish.unique_id:
                other_fish.append(fish)
        return other_fish

    @staticmethod
    def extract_nearby_fish_names(fish_list: list) -> list:
        """cycles through fish list and extracts name and ID to make it easier to cross ref"""
        out_list = []
        for fsh in fish_list:
            out_list.append((fsh.name, fsh.unique_id))
        return out_list