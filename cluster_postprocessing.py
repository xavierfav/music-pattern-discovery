"""
Functions do the post processing
"""
from sequenceParser import sum_length_sequence
from parameters_global import length_sequence, tolerance_length


def cluster_cleaner(cluster):
    """
    if sequence is from the same line and with the same starting note, just keep the longest one
    :param cluster:
    :return:
    """

    # collect the unique indices
    cluster_cleaned = []
    indices = []
    for ind in [sequence[-1] for sequence in cluster]:
        if ind not in indices:
            indices.append(ind)

    # find the max length sequence for each index
    for index in indices:
        length_max = -1
        for seq in [sequence[:-1] for sequence in cluster if sequence[-1] == index]:
            len_seq = sum_length_sequence(seq, length_sequence + tolerance_length, truncate=False)
            if len_seq > length_max:
                seq_max_length = seq
                length_max = len_seq
        cluster_cleaned.append(seq_max_length)
    return cluster_cleaned


def runProcess(clusters):
    clusters_cleaned = []
    for cluster in clusters:
        cluster_cleaned = cluster_cleaner(cluster)
        clusters_cleaned.append(cluster_cleaned)
    return clusters_cleaned