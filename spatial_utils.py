import logging


logger = logging.getLogger(__name__)


class SpatialUtils:
    @staticmethod
    def is_left(vertex1: tuple, vertex2: tuple, point: tuple):
        """
        tests if a point is left, on, or right on an infinite line
        :param vertex1: one point on line
        :param vertex2: other point on line
        :param point: point to compare to line
        :return: >0 for point left of the line through vertex1 and vertex2
                 =0 for point on the line
                 <0 for point right of the line
        """
        point_x = point[0]
        point_y = point[1]
        vertex1_x = vertex1[0]
        vertex1_y = vertex1[1]
        vertex2_x = vertex2[0]
        vertex2_y = vertex2[1]

        a = (vertex2_x - vertex1_x) * (point_y - vertex1_y)
        b = (vertex2_y - vertex1_y) * (point_x - vertex1_x)

        return a - b

    @staticmethod
    def _winding_number(point: tuple, polygon: tuple) -> int:
        """
        approach is correct for simple and non simple polygons
        :return: 0 if outside of polygon
                 else inside of polygon
        """
        winding_number_counter = 0  # the winding number counter
        vertices_num = len(polygon)

        for i in range(vertices_num - 1):
            vertex1 = polygon[i]
            vertex2 = polygon[i + 1]
            if vertex1[1] <= point[1]:  # point above start vertex
                if vertex2[1] > point[1]:  # point below next vertex
                    if SpatialUtils.is_left(vertex1, vertex2, point) > 0:  # point left of edge start vertex to end vertex
                        winding_number_counter += 1  # valid up intersect
            else:  # point below start vertex
                if vertex2[1] <= point[1]:  # point above next vertex
                    if SpatialUtils.is_left(vertex1, vertex2, point) < 0:  # point left of edge start vertex to end vertex
                        winding_number_counter -= 1  # a valid down intersect
        return winding_number_counter

    @staticmethod
    def _crossing_number(point: tuple, polygon: tuple) -> int:
        """
        approach only works for simple polygons (i.e. no self intersections)
        :return: 0 if even number of crosses - outside of polygon
                 1 if odd number of crosses - inside of polygon
        """
        crossing_number_counter = 0  # the crossing number counter

        vertices_num = len(polygon)

        for i in range(vertices_num - 1):
            vertex1 = polygon[i]
            vertex2 = polygon[i + 1]
            # if point above or level with start vertex and below next vertex
            # or below start vertex and above or level with next vertex
            if ((vertex1[1] <= point[1] and vertex2[1] > point[1])  # an upward crossing
                or (vertex1[1] > point[1] and vertex2[1] <= point[1])):  # a downward crossing
                # compute the actual edge-ray intersect x-coordinate
                vt = (point[1] - vertex1[1]) / float(vertex2[1] - vertex1[1])
                # if point left of intersect
                if point[0] < vertex1[0] + vt * (vertex2[0] - vertex1[0]):
                    crossing_number_counter += 1  # a valid crossing

        return crossing_number_counter % 2

    @staticmethod
    def poly_contains_point(point: tuple, polygon: tuple, method: str='winding') -> bool:
        assert polygon[0] == polygon[-1]

        if method == 'winding':
            number = SpatialUtils._winding_number(point=point, polygon=polygon)
        elif method == 'crossing':
            number = SpatialUtils._crossing_number(point=point, polygon=polygon)
        else:
            logger.warning('incorrect method selected, please choose from: [winding, crossing], exiting')
            exit()

        if number == 0:
            contains = False
        else:
            contains = True
        return contains

    @staticmethod
    def extract_bounding_box(bounding_coordinates):
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