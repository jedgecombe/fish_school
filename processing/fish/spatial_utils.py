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
    
    @staticmethod
    def new_position_angle_length(angle, distance, starting_coordinates):
        """generate new position based on the angle, distance, and starting point"""
        # calc cosine of angle and multiply by the distance
        cosin_ang = math.cos(math.radians(angle)) * distance
        # calc sine of angle and multiply by the distance
        sin_ang = math.sin(math.radians(angle)) * distance
        # add cosine to x and sine to y to give new coord
        return starting_coordinates[0] + cosin_ang, starting_coordinates[1] + sin_ang
