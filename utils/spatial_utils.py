import logging
import math
import sys


logger = logging.getLogger(__name__)


class SpatialUtils:
    @staticmethod
    def is_left(coordinates: list, vertex1: list, vertex2: list) -> float:
        """
        tests if a point is left, on, or right on an infinite line
        :param coordinates: point to compare to line
        :param vertex1: one point on line
        :param vertex2: other point on line
        :return: >0 for point left of the line through vertex1 and vertex2
                 =0 for point on the line
                 <0 for point right of the line
        """
        point_x = coordinates[0]
        point_y = coordinates[1]
        vertex1_x = vertex1[0]
        vertex1_y = vertex1[1]
        vertex2_x = vertex2[0]
        vertex2_y = vertex2[1]

        a = (vertex2_x - vertex1_x) * (point_y - vertex1_y)
        b = (vertex2_y - vertex1_y) * (point_x - vertex1_x)

        return a - b

    @staticmethod
    def poly_contains_point(coordinates: list, polygon: tuple, method: str= 'winding') -> bool:
        def winding_number(coords: list, poly: tuple) -> int:
            """
            approach is correct for simple and non simple polygons
            :return: 0 if outside of polygon
                     else inside of polygon
            """
            winding_number_counter = 0  # the winding number counter
            vertices_num = len(poly)

            for i in range(vertices_num - 1):
                vertex1 = poly[i]
                vertex2 = poly[i + 1]
                if vertex1[1] <= coords[1]:  # coordinates above start vertex
                    if vertex2[1] > coords[1]:  # coordinates below next vertex
                        if SpatialUtils.is_left(vertex1, vertex2,
                                                coords) > 0:  # coordinates left of edge start vertex to end vertex
                            winding_number_counter += 1  # valid up intersect
                else:  # coordinates below start vertex
                    if vertex2[1] <= coords[1]:  # coordinates above next vertex
                        if SpatialUtils.is_left(vertex1, vertex2,
                                                coords) < 0:  # coordinates right of edge start vertex to end vertex
                            winding_number_counter -= 1  # a valid down intersect
            return winding_number_counter

        def crossing_number(coords: list, poly: tuple) -> int:
            """
            approach only works for simple polygons (i.e. no self intersections)
            :return: 0 if even number of crosses - outside of polygon
                     1 if odd number of crosses - inside of polygon
            """
            crossing_number_counter = 0  # the crossing number counter

            vertices_num = len(poly)

            for i in range(vertices_num - 1):
                vertex1 = poly[i]
                vertex2 = poly[i + 1]
                # if coordinates above or level with start vertex and below next vertex
                # or below start vertex and above or level with next vertex
                if ((vertex1[1] <= coords[1] and vertex2[1] > coords[1])  # an upward crossing
                        or (vertex1[1] > coords[1] and vertex2[1] <= coords[1])):  # a downward crossing
                    # compute the actual edge-ray intersect x-coordinate
                    vt = (coords[1] - vertex1[1]) / float(vertex2[1] - vertex1[1])
                    # if coordinates left of intersect
                    if coords[0] < vertex1[0] + vt * (vertex2[0] - vertex1[0]):
                        crossing_number_counter += 1  # a valid crossing

            return crossing_number_counter % 2

        assert polygon[0] == polygon[-1]

        if method == 'winding':
            number = winding_number(coords=coordinates, poly=polygon)
        elif method == 'crossing':
            number = crossing_number(coords=coordinates, poly=polygon)
        else:
            logger.warning('incorrect method selected, please choose from: [winding, crossing], exiting')
            sys.exit(1)

        return False if number == 0 else True

    @staticmethod
    def extract_bounding_box(bounding_coordinates) -> tuple:
        # create initial values to be overwritten
        min_long = 100000000
        max_long = -100000000
        min_lat = 100000000
        max_lat = -100000000

        for coord in bounding_coordinates:
            long = coord[0]
            lat = coord[1]
            if long < min_long:
                min_long = long
            if long > max_long:
                max_long = long
            if lat < min_lat:
                min_lat = lat
            if lat > max_lat:
                max_lat = lat

        bbox = (min_long, min_lat, max_long, max_lat)
        return bbox

    @staticmethod
    def distance_to_boundary(coordinates: list, polygon: tuple) -> float:
        """
        cycles through each line of polygon finding distance to line then returns minimum
            proof here: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
        :return: minimum distance from point to boundary
        """
        vertices_num = len(polygon)
        distances_to_edge = []
        for i in range(vertices_num - 1):
            vertex1 = polygon[i]
            vertex2 = polygon[i + 1]

            vertices_x_diff = vertex2[0] - vertex1[0]
            vertices_y_diff = vertex2[1] - vertex1[1]
            numerator = abs(vertices_y_diff*coordinates[0] - vertices_x_diff*coordinates[1] + vertex2[0]*vertex1[1] - vertex2[1]*vertex1[0])
            denominator = math.sqrt((vertex2[1] - vertex1[1])**2 + (vertex2[0] - vertex1[0])**2)
            distances_to_edge.append(numerator / denominator)
        return round(min(distances_to_edge), 3)

    @staticmethod
    def calc_distance(coordinates1: list, coordinates2: list) -> float:
        """
        calc distance between two points (units in same units as coordinates)
        :param coordinates1: coordinates of point 1
        :param coordinates2: coordinates of point 2
        :return: distance, rounded to 4 d.p.
        """
        squared_dist = (coordinates1[0] - coordinates2[0]) ** 2 + (coordinates1[1] - coordinates2[1]) ** 2
        dist = math.sqrt(squared_dist)
        return round(dist, 4)

    @staticmethod
    def calc_angle(coordinates1, coordinates2):
        delta_y = coordinates2[1] - coordinates1[1]
        delta_x = coordinates2[0] - coordinates1[0]
        return math.degrees(math.atan2(delta_y, delta_x))

    @staticmethod
    def new_position_angle_length(angle: float, distance: int, starting_coordinates: list):
        """generate new position based on the angle, distance, and starting point"""
        # calc cosine of angle and multiply by the distance
        cosin_ang = math.cos(math.radians(angle)) * distance
        # calc sine of angle and multiply by the distance
        sin_ang = math.sin(math.radians(angle)) * distance
        # add cosine to x and sine to y to give new coord
        return starting_coordinates[0] + cosin_ang, starting_coordinates[1] + sin_ang

    # @staticmethod
    # def generate_circle_boundary(starting_coords: tuple, radius: int, increments: int=360) -> tuple:
    #     """
    #     creates a tuple of tuples with coordinates of a 'circle' (is actually a series of straight lines
    #     :param starting_coords: coordinate points to draw circle around
    #     :param radius: radius of circle
    #     :param increments: number of lines to draw (i.e. precision), increase to increase precision
    #     :return: coordinates of circle
    #     """
    #     out_list = []
    #
    #     for incr in range(increments):
    #         pass
    #
    #     return tuple(out_list)