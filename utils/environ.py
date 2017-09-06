import logging
import os

from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
from matplotlib.image import BboxImage
from matplotlib.transforms import Bbox, TransformedBbox

from utils.spatial_utils import SpatialUtils

logger = logging.getLogger(__name__)


class OceanEnvironment:
    def __init__(self, bounding_coordinates: tuple):
        """
        :param bounding_coordinates: should be tuple of tuples (x, y) listed in counterclockwise direction
            ending with the first coordinate to close path
        """
        self.boundary = bounding_coordinates
        self.population = []
        self.subenvironment = None

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
        logger.info('number of alive fish: {} \n alive fish: {}'.format(len(alive_fish), alive_fish))
        logger.info('number of dead fish: {} \n dead fish: {}'.format(len(dead_fish), dead_fish))

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
        p = PatchCollection(patches, alpha=0.4)
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


class NearbyWaters(OceanEnvironment):
    def __init__(self, fish, ocean: OceanEnvironment):
        OceanEnvironment.__init__()
        pass