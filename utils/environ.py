import json
import logging
import math
import os
import pprint
import random

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
              'trixie', 'zeus', 'barnaby', 'tarquin']


class OceanEnvironment:
    def __init__(self, bounding_coordinates: tuple):
        """
        :param bounding_coordinates: should be tuple of tuples (x, y) listed in counterclockwise direction
            ending with the first coordinate to close path
        """
        self.boundary = bounding_coordinates
        self.population = []
        self.subenvironment = None

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
                fish_data = self._extract_fish_metadata(fish)
                alive_fish.append(fish_data)
            else:
                fish_data = self._extract_fish_metadata(fish)
                dead_fish.append(fish_data)
            logger.debug('fish: {}'.format(fish_data))
        logger.info('number of alive fish: {}'.format(len(alive_fish)))
        logger.info('number of dead fish: {}'.format(len(dead_fish)))

    @staticmethod
    def _extract_fish_metadata(fish) -> dict:
        name = fish.name
        species = fish.species
        welfare = fish.welfare
        position = fish.position
        edge_distance = fish.dist_to_closest_edge
        return {'name': name, 'species': species, 'welfare': welfare, 'position': position,
                'distance_to_closest_edge': edge_distance}

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
                bb = Bbox.from_bounds(x0=(fish.position[0]-fish.size/2), y0=(fish.position[1]-fish.size/2),
                                      width=fish.size, height=fish.size)
                bb2 = TransformedBbox(bb, axis.transData)
                bbox_image = BboxImage(bb2, norm=None, origin=None, clip_on=False)
                bbox_image.set_data(fish.graph_marker)
                axis.add_artist(bbox_image)

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
    def __init__(self, environment: OceanEnvironment, species: str, fish_name: str=None,
                 initial_position: tuple=None):
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
        # Fish.__init__(self, environment=environment, species='snapper', initial_position=initial_position,
        #               fish_name=fish_name, place_attempts=place_attempts)
        super().__init__(environment=environment, species='snapper', initial_position=initial_position,
                         fish_name=fish_name)
        self.size = 5
        self.repel_distance = 1  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = 3  # focal fish will seek to align direction with neighbours
        self.follow_distance = 10  # focal fish will move towards a neighbour
        self.max_movement_radius = 2  # max distance fish can move in a single turn
        im = plt.imread('input/fish.png')
        self.graph_marker = ndimage.rotate(im, self.rotation)

        self.fish_pos = FishPosition(environment=self.environment, focal_fish=self)
        self.position = self.fish_pos.set_pos(place_attempts)

        if self.position is not None:
            self.welfare = 'alive'

        self.dist_to_closest_edge = self.distance_to_boundary()


class Whale(Fish):
    def __init__(self, environment: OceanEnvironment,
                 fish_name: str=None,
                 initial_position: tuple=None, place_attempts: int=3
                 ):
        # super().__init__(self, species='whale')
        super().__init__(environment=environment, species='whale', initial_position=initial_position,
                         fish_name=fish_name)

        self.size = 15
        self.repel_distance = 1  # less than this distance focal fish will swim away to avoid collision
        self.align_distance = 3  # focal fish will seek to align direction with neighbours
        self.follow_distance = 10  # focal fish will move towards a neighbour
        self.max_movement_radius = 2  # max distance fish can move in a single turn
        im = plt.imread('input/fish.png')
        self.graph_marker = ndimage.rotate(im, self.rotation)

        self.fish_pos = FishPosition(environment=self.environment, focal_fish=self)

        if self.position is not None:
            self.position = self.fish_pos.set_pos(place_attempts)
            self.welfare = 'alive'
            self.dist_to_closest_edge = self.distance_to_boundary()


class NearbyWaters:
    def __init__(self, fish: Fish, ocean: OceanEnvironment):
        """
        this class assesses the relevant environment around a fish i.e. the environment that will affect its movement
            this should be evaluated for each fish for each move
        :param fish:
        :param ocean:
        """
        # super(OceanEnvironment, self).__init__()
        # OceanEnvironment.__init__()
        if fish.position is not None:
            self.fish = fish
            self.ocean = ocean
            self.centre_coordinates = self.fish.position
            self.environ_radius = self.fish.follow_distance


            self.nearby_fish = FishPosition(self.ocean, self.fish).find_nearby_fish()

            coords_within_radius = self.find_coordinates_within_radius(self.centre_coordinates, self.environ_radius)
            environ_coordinates = self.find_coordinates_within_sub_environment(coords_within_radius, self.ocean.boundary)
            empty_coordinates = self.find_empty_coordinates(all_coordinates=environ_coordinates, nearby_fish=self.nearby_fish)

            self.available_moves = self.find_available_moves(empty_coordinates=empty_coordinates)
            print(self.available_moves)


    @staticmethod
    def find_coordinates_within_radius(centre_coords: tuple, circle_radius: int) -> list:
        """
        cycles through all coordinate pairs of inside bounding box of centre coords +- circle_radius
            then compares whether coordinate generated is within the circle_radius
        :param centre_coords: central coordinates of bounding box
        :param circle_radius: circle_radius of circle to be considered
        :return: list of coordinates within a circle within radius = circle_radius
        """
        coords_within_radius = []
        centre_x = centre_coords[0]
        centre_y = centre_coords[1]
        search_range = range(-circle_radius, circle_radius + 1)
        for x_increment in search_range:
            for y_incremement in search_range:
                test_coord = (centre_x + x_increment, centre_y + y_incremement)
                dist_to_centre = SpatialUtils.calc_distance(test_coord, centre_coords)
                if dist_to_centre <= circle_radius:
                    coords_within_radius.append(test_coord)
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
        updated_coordinate_list = all_coordinates
        for coord in all_coordinates:
            for fsh in nearby_fish:
                space_necessary = self.fish.size + fsh.size
                if SpatialUtils.calc_distance(coord, fsh.position) < space_necessary:
                    updated_coordinate_list.remove(coord)
                break
        return updated_coordinate_list

    def find_available_moves(self, empty_coordinates: list) -> list:
        """
        finds which locations a fish could actually move to
        :param empty_coordinates: coordinates that are not currently occupied
        :return: list of moves that a fish could make in one turn
        """
        available_moves = []
        for coord in empty_coordinates:
            if SpatialUtils.calc_distance(coord, self.fish.position) <= self.fish.max_movement_radius:
                available_moves.append(coord)
        return available_moves


class FishPosition:
    def __init__(self, environment: OceanEnvironment, focal_fish: Fish):
        self.environment = environment
        self.fish = focal_fish

        if focal_fish.position is not None:
            self.distance_to_boundary = SpatialUtils.distance_to_boundary(self.fish.position, self.environment.boundary)
        # self.nearby_fish = self.find_nearby_fish()

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

    def find_nearby_fish(self) -> list:
        """
        find all fish within the follow distance of the focal fish (i.e. all fish the focal fish can see)
            follow distance is summed with sizes of both fish being considered to account for larger fish
            being visible not just on the single coordinate they occupy
        :return: fish that are within this zone
        """
        all_other_fish = self.find_all_other_fish()
        nearby_fish = []
        for other_fish in all_other_fish:
            distance_between_fish = SpatialUtils.calc_distance(self.fish.position, other_fish.position)
            total_distance_considered = self.fish.follow_distance + self.fish.size + other_fish.size
            if distance_between_fish <= total_distance_considered:
                nearby_fish.append(other_fish)
        return nearby_fish

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




