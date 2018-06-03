# from utils.spatial_utils import SpatialUtils
#
# import numpy as np
#
#
# def find_coordinates_within_radius(centre_coords: tuple, circle_radius: int) -> list:
#     """
#     cycles through all coordinate pairs of inside bounding box of centre coords +- circle_radius
#         then compares whether coordinate generated is within the circle_radius
#     :param centre_coords: central coordinates of bounding box
#     :param circle_radius: circle_radius of circle to be considered
#     :return: list of coordinates within a circle within radius = circle_radius
#     """
#     test_list = []
#     centre_x = centre_coords[0]
#     centre_y = centre_coords[1]
#     search_range = np.arange(-circle_radius, 0 + STEP, STEP)
#     for num, x_increment in enumerate(search_range):
#         for num2, y_increment in enumerate(search_range):
#             test_coord = (centre_x + x_increment, centre_y + y_increment)
#             dist_to_centre = SpatialUtils.calc_distance(test_coord, centre_coords)
#             if dist_to_centre > circle_radius:
#                 continue
#             else:
#                 test_list.append((num, num2))
#                 break
#         print('radius: {}'.format(circle_radius))
#         print('coordinate numbers: {}'.format((num, abs(num2))))
#         dct = {'radius': circle_radius, 'x_incremement_num': num}
#
#
#
# STEP = 0.1
#
# for i in range(1, 30, 1):
#     find_coordinates_within_radius((0, 0), circle_radius=i)