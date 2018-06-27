import math


class SpatialUtils:
    @staticmethod
    def calc_angle(coordinates1, coordinates2):
        delta_y = coordinates2[1] - coordinates1[1]
        delta_x = coordinates2[0] - coordinates1[0]
        return math.degrees(math.atan2(delta_y, delta_x))
    
    @staticmethod
    def calc_distance(coordinates1, coordinates2):
        """
        calc distance between two points (units in same units as coordinates)
        :param coordinates1: coordinates of point 1
        :param coordinates2: coordinates of point 2
        :return: distance, rounded to 4 d.p.
        """
        squared_dist = (coordinates1[0] - coordinates2[0]) ** 2 + (coordinates1[1] - coordinates2[1]) ** 2
        dist = math.sqrt(squared_dist)
        return round(dist, 4)
