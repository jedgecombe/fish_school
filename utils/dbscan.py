# import numpy
#
#
# def DBSCAN(vectors, eps, min_points):
#     """
#     cluster dataset of vectors according to DBSCAN methodology
#     :param vectors: the list of vectors to cluster
#     :param eps: threshold distance
#     :param min_points: minimum number of points required in the cluster for it to be considered non-noise
#     :return: a list of labels. -1 for noise, other labels begin from one
#     """
#     # initialise all labels as 0, before subsequently overwriting
#     labels = [0] * len(vectors)
#
#     # C is the ID of the current cluster.
#     C = 0
#
#     # This outer loop is just responsible for picking new seed points--a point
#     # from which to grow a new cluster.
#     # Once a valid seed point is found, a new cluster is created, and the
#     # cluster growth is all handled by the 'expandCluster' routine.
#
#     # For each point P in the Dataset D...
#     # ('P' is the index of the datapoint, rather than the datapoint itself.)
#     for P in range(0, len(vectors)):
#
#         # Only points that have not already been claimed can be picked as new
#         # seed points.
#         # If the point's label is not 0, continue to the next point.
#         if not (labels[P] == 0):
#             continue
#
#         # Find all of P's neighboring points.
#         NeighborPts = regionQuery(vectors, P, eps)
#
#         # If the number is below MinPts, this point is noise.
#         # This is the only condition under which a point is labeled
#         # NOISE--when it's not a valid seed point. A NOISE point may later
#         # be picked up by another cluster as a boundary point (this is the only
#         # condition under which a cluster label can change--from NOISE to
#         # something else).
#         if len(NeighborPts) < min_points:
#             labels[P] = -1
#         # Otherwise, if there are at least MinPts nearby, use this point as the
#         # seed for a new cluster.
#         else:
#             C += 1
#             growCluster(vectors, labels, P, NeighborPts, C, eps, min_points)
#
#     # All data has been clustered!
#     return labels
#
#
# def growCluster(D, labels, P, NeighborPts, C, eps, MinPts):
#     """
#     Grow a new cluster with label `C` from the seed point `P`.
#
#     This function searches through the dataset to find all points that belong
#     to this new cluster. When this function returns, cluster `C` is complete.
#
#     Parameters:
#       `D`      - The dataset (a list of vectors)
#       `labels` - List storing the cluster labels for all dataset points
#       `P`      - Index of the seed point for this new cluster
#       `NeighborPts` - All of the neighbors of `P`
#       `C`      - The label for this new cluster.
#       `eps`    - Threshold distance
#       `MinPts` - Minimum required number of neighbors
#     """
#
#     # Assign the cluster label to the seed point.
#     labels[P] = C
#
#     # Look at each neighbor of P (neighbors are referred to as Pn).
#     # NeighborPts will be used as a FIFO queue of points to search--that is, it
#     # will grow as we discover new branch points for the cluster. The FIFO
#     # behavior is accomplished by using a while-loop rather than a for-loop.
#     # In NeighborPts, the points are represented by their index in the original
#     # dataset.
#     i = 0
#     while i < len(NeighborPts):
#
#         # Get the next point from the queue.
#         Pn = NeighborPts[i]
#
#         # If Pn was labelled NOISE during the seed search, then we
#         # know it's not a branch point (it doesn't have enough neighbors), so
#         # make it a leaf point of cluster C and move on.
#         if labels[Pn] == -1:
#             labels[Pn] = C
#
#         # Otherwise, if Pn isn't already claimed, claim it as part of C.
#         elif labels[Pn] == 0:
#             # Add Pn to cluster C (Assign cluster label C).
#             labels[Pn] = C
#
#             # Find all the neighbors of Pn
#             PnNeighborPts = regionQuery(D, Pn, eps)
#
#             # If Pn has at least MinPts neighbors, it's a branch point!
#             # Add all of its neighbors to the FIFO queue to be searched.
#             if len(PnNeighborPts) >= MinPts:
#                 NeighborPts = NeighborPts + PnNeighborPts
#             # If Pn *doesn't* have enough neighbors, then it's a leaf point.
#             # Don't queue up it's neighbors as expansion points.
#             # else:
#             # Do nothing
#             # NeighborPts = NeighborPts
#
#         # Advance to the next point in the FIFO queue.
#         i += 1
#
#         # We've finished growing cluster C!
#
#
# def regionQuery(D, P, eps):
#     """
#     Find all points in dataset `D` within distance `eps` of point `P`.
#
#     This function calculates the distance between a point P and every other
#     point in the dataset, and then returns only those points which are within a
#     threshold distance `eps`.
#     """
#     neighbors = []
#
#     # For each point in the dataset...
#     for Pn in range(0, len(D)):
#
#         # If the distance is below the threshold, add it to the neighbors list.
#         if numpy.linalg.norm(D[P] - D[Pn]) < eps:
#             neighbors.append(Pn)
#
#     return neighbors

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

    # C is the ID of the current cluster.
    cluster_num = 0

    # This outer loop is just responsible for picking new seed points--a point
    # from which to grow a new cluster.
    # Once a valid seed point is found, a new cluster is created, and the
    # cluster growth is all handled by the 'expandCluster' routine.
    #
    # For each point P in the Dataset D...
    # ('P' is the index of the datapoint, rather than the datapoint itself.)

    # JE create a seed for each point
    for seed in range(len(points)):
        # JE if the point has already been assigned to a cluster, skip
        if labels[seed] != 0:
            continue
        # JE find all points withn eps of points[seed]
        seed_point = points[seed]
        neighbours = nearby_points(points=points, ref_point=seed_point, eps=eps)

        # If the number is below MinPts, this point is noise.
        # This is the only condition under which a point is labeled
        # NOISE--when it's not a valid seed point. A NOISE point may later
        # be picked up by another cluster as a boundary point (this is the only
        # condition under which a cluster label can change--from NOISE to
        # something else).
        if len(neighbours) < min_points:
            labels[seed] = -1
        # Otherwise, if there are at least MinPts nearby, use this point as the
        # seed for a new cluster.
        else:
            cluster_num += 1
            grow_cluster(points=points, labels=labels, seed_num=seed,
                         neighbours=neighbours, cluster_label=cluster_num,
                         eps=eps, min_points=min_points)

    # All data has been clustered!
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

    # Assign the cluster label to the seed point.
    labels[seed_num] = cluster_label

    # Look at each neighbor of P (neighbors are referred to as Pn).
    # NeighborPts will be used as a FIFO queue of points to search--that is, it
    # will grow as we discover new branch points for the cluster. The FIFO
    # behavior is accomplished by using a while-loop rather than a for-loop.
    # In NeighborPts, the points are represented by their index in the original
    # dataset.
    i = 0

    # JE loop through each neighbour. Use while loop because neighbours is added to if branch is found
    while i < len(neighbours):
        ref_point = neighbours[i]
        # NEXT - don't think this is correct. Think  it is good up to hear but from here but need to update the label of the specific ref_point in entire label list. Maybe use index like so
        # https://stackoverflow.com/questions/6294179/how-to-find-all-occurrences-of-an-element-in-a-list

        # if ref_point was classed as NOISE we know it is not a branch point (noise has no point within eps)
        # but it is a leaf point of this cluster, so add
        indices = [i for i, x in enumerate(points) if x == ref_point]
        for ind in indices:
            if labels[ind] == -1:
                labels[ind] = cluster_label
        # # ind for ind in indices
        # if labels[i] == -1:
        #     labels[i] = cluster_label

        # if ref_point isn't already claimed, add to this cluster
            elif labels[ind] == 0:
                labels[ind] = cluster_label
                # find all neighbours of the neighbour
                neighbour_neighbours = nearby_points(points=points, ref_point=ref_point, eps=eps)
                # if ref_point has min required neighbouring points, it is a branch point
                # add all of its neighbors to the FIFO queue to be searched.
                if len(neighbour_neighbours) >= min_points:
                    neighbours = neighbours + neighbour_neighbours
        i += 1

    #
    # while i < len(neighbours):
    #
    #     # Get the next point from the queue.
    #     Pn = neighbours[i]
    #
    #     # If Pn was labelled NOISE during the seed search, then we
    #     # know it's not a branch point (it doesn't have enough neighbors), so
    #     # make it a leaf point of cluster C and move on.
    #     if labels[Pn] == -1:
    #         labels[Pn] = cluster_label
    #
    #     # Otherwise, if Pn isn't already claimed, claim it as part of C.
    #     elif labels[Pn] == 0:
    #         # Add Pn to cluster C (Assign cluster label C).
    #         labels[Pn] = cluster_label
    #
    #         # Find all the neighbors of Pn
    #         PnNeighborPts = nearby_points(points, Pn, eps)
    #
    #         # If Pn has at least MinPts neighbors, it's a branch point!
    #         # Add all of its neighbors to the FIFO queue to be searched.
    #         if len(PnNeighborPts) >= min_points:
    #             neighbours = neighbours + PnNeighborPts
    #         # If Pn *doesn't* have enough neighbors, then it's a leaf point.
    #         # Don't queue up it's neighbors as expansion points.
    #         # else:
    #         # Do nothing
    #         # NeighborPts = NeighborPts
    #
    #     # Advance to the next point in the FIFO queue.
    #     i += 1
    #
    #     # We've finished growing cluster C!


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
