from utils.spatial_utils import SpatialUtils


def DBSCAN(points, eps, min_points):
    """
    cluster dataset of points according to DBSCAN methodology
    :param points: the list of vectors to cluster
    :param eps: threshold distance
    :param min_points: minimum number of points required in the cluster for it to be considered non-noise
    :return: a list of labels. -1 for noise, other labels begin from one
    """
    # initialise all labels as 0, before subsequently overwriting
    labels = [0] * len(points)

    # ID of current cluster
    cluster_num = 0

    # create a seed for each point (points from which to try to grow new cluster)
    for seed_num, seed in enumerate(points):
        # if the point has already been assigned to a cluster, skip
        if labels[seed_num] != 0:
            continue
        # find all points within eps of point
        neighbours = nearby_points(points=points, ref_point=seed, eps=eps)

        # if has few that min_points as neighbours it is noise. Note it may later be classed as a boundary point
        # of other cluster and have label updated
        if len(neighbours) < min_points:
            labels[seed_num] = -1
        # else grow cluster around this seed
        else:
            cluster_num += 1
            grow_cluster(points=points, labels=labels, seed_num=seed_num,
                         neighbours=neighbours, cluster_label=cluster_num,
                         eps=eps, min_points=min_points)
    return labels


def grow_cluster(points, labels, seed_num, neighbours, cluster_label, eps, min_points):
    """
    Grow a new cluster with label `C` from the seed point `P`.

    This function searches through the dataset to find all points that belong
    to this new cluster. When this function returns, cluster `C` is complete.

    Parameters:
      `D`      - The dataset (a list of vectors)
      `labels` - List storing the cluster labels for all dataset points
      `P`      - Index of the seed point for this new cluster
      `NeighborPts` - All of the neighbors of `P`
      `C`      - The label for this new cluster.
      `eps`    - Threshold distance
      `MinPts` - Minimum required number of neighbors
    """

    # assign the cluster label to the seed point
    labels[seed_num] = cluster_label

    # Look at each neighbor of P (neighbors are referred to as Pn).
    # NeighborPts will be used as a FIFO queue of points to search--that is, it
    # will grow as we discover new branch points for the cluster. The FIFO
    # behavior is accomplished by using a while-loop rather than a for-loop.
    # In NeighborPts, the points are represented by their index in the original
    # dataset.
    i = 0

    # try branching from each point within neighbours
    # use while loop because neighbours is added to if branch is found
    while i < len(neighbours):
        ref_point = neighbours[i]
        # if ref_point was classed as noise we know it is not a branch point (noise has no point within eps)
        # but it is a leaf point of this cluster, so add to cluster of seed point
        indices = [i for i, x in enumerate(points) if x == ref_point]
        for ind in indices:
            if labels[ind] == -1:
                labels[ind] = cluster_label
            # if ref_point isn't already claimed, add to this cluster
            elif labels[ind] == 0:
                labels[ind] = cluster_label
                # find all neighbours of the neighbour
                neighbour_neighbours = nearby_points(points=points, ref_point=ref_point, eps=eps)
                # if ref_point has min required neighbouring points, it is a branch point
                # add all of its neighbors to the FIFO queue to be searched.
                neighbours = neighbours + neighbour_neighbours
        i += 1


def nearby_points(points, ref_point, eps):
    """
    Find all points in dataset `D` within distance `eps` of point `P`.

    This function calculates the distance between a point P and every other
    point in the dataset, and then returns only those points which are within a
    threshold distance `eps`.
    """
    neighbours = []
    # ref_point = points[point_seed]
    for point in points:
        # if point within eps of reference point, class as neighbour
        if SpatialUtils.calc_distance(ref_point, point) <= eps:
            neighbours.append(point)
    return neighbours
