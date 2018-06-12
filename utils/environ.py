import logging
import os

import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.animation as animation
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text

from utils.spatial_utils import SpatialUtils
from utils.dbscan import DBSCAN

logger = logging.getLogger(__name__)


class OceanEnvironment:
    def __init__(self, bounding_coordinates: tuple, minimum_shoal_size: int):
        """
        :param bounding_coordinates: should be tuple of tuples (x, y) listed in counterclockwise direction
            ending with the first coordinate to close path
        :param minimum_shoal_size: minimum number of fish required to be considered a shoal (used during clustering)
        """
        self.boundary = bounding_coordinates
        self.population = []
        self.populated_sorted = []
        self.min_shoal_size = minimum_shoal_size
        self.sea_colour = '#006994'
        self.move_metadata = []

    def get_fish_metadata(self):
        """
        log fish, grouped according to whether they are dead or alive
        :return: nothing
        """
        for fish in self.population:
            fish_data = self._extract_fish_brains(fish)
            logger.debug(f'fish: {fish_data}')
        logger.info(f'number of fish in the ocean: {len(self.population)}')

    def _assign_shoals(self, shoal_labels):
        for fsh, cluster in zip(self.population, shoal_labels):
            if cluster == -1:
                fsh.shoal_id = None
                fsh.current_colour = fsh.colour
            else:
                fsh.shoal_id = cluster
                fsh.current_colour = fsh.cluster_colour

            # fsh.shoal_id = None if cluster == -1 else cluster

    def _extract_fish_positions(self) -> list:
        """
        extract the coordinate points of each fish in the population
        :return: list of coordinates
        """
        coords = []
        for fsh in self.population:
            coords.append([fsh.position[0], fsh.position[1]])
        return coords

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

    @staticmethod
    def _extract_fish_brains(fish) -> dict:
        repel_fish = fish.sub_env.extract_nearby_fish_names(fish.sub_env.repel_fish)
        align_fish = fish.sub_env.extract_nearby_fish_names(fish.sub_env.align_fish)
        follow_fish = fish.sub_env.extract_nearby_fish_names(fish.sub_env.follow_fish)
        return {'name': fish.name, 'id': fish.unique_id, 'shoal_id': fish.shoal_id, 'species': type(fish),
                'welfare': fish.welfare, 'position': fish.position, 'rotation': fish.rotation, 'age': fish.age,
                'distance_to_closest_edge': fish.dist_to_closest_edge, 'repel_fish': repel_fish,
                'align_fish': align_fish, 'follow_fish': follow_fish}

    def get_ocean_metadata(self):
        # TODO something to describe ocean - particularly size
        pass

    def passage_of_time(self, time_periods: int, save_filename: str):
        def animate(i):
            logger.info(f'\n\n time: {i} \n\n')
            ax.set_title(f'time {i}')
            # remove previous fish - could change this by using set_colour argument
            for x in ax.get_children():
                if type(x) == Line2D or type(x) == Text:
                    # try and except is necessary to avoid removing crucial Text objects
                    try:
                        x.remove()
                    except NotImplementedError:
                        continue
            for fsh in self.population:
                fsh.swim()
                ln = Line2D([fsh.previous_position[0], fsh.position[0]], [fsh.previous_position[1], fsh.position[1]],
                            marker=fsh.custom_marker, markersize=fsh.size,  c=fsh.current_colour, linestyle='none',
                            markevery=[1])

                ax.text(fsh.position[0], fsh.position[1], f'{fsh.name}', fontsize=8)
                # ax.text(fsh.position[0], fsh.position[1], f'{fsh.name} ({fsh.unique_id})', fontsize=6)
                ax.add_line(ln)

            population_coords = self._extract_fish_positions()
            cluster_labels = DBSCAN(points=population_coords, eps=30, min_points=self.min_shoal_size) # TODO update eps to close to follow_distance
            self._assign_shoals(shoal_labels=cluster_labels)

        fig, ax = plt.subplots(figsize=(9, 7))
        self._add_ocean(ax)

        x_limit, y_limit = self._get_axes_limits()
        plt.xlim(x_limit)
        plt.ylim(y_limit)
        ax.set_yticks([])
        ax.set_xticks([])
        # to update speed on animation need to play with interval and fps
        ani = animation.FuncAnimation(fig, animate, frames=time_periods, interval=50)
        writer = animation.writers['ffmpeg']
        ff_writer = writer(fps=5, metadata=dict(artist='Jamie Edgecombe'))
        ani.save(os.path.join(save_filename), writer=ff_writer)

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


class FishMongers:
    def __init__(self):
        self.population = []
