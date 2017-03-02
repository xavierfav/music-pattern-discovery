import pickle
import json

import numpy as np
from clustering_methods import *
import sequenceParser
import patternRepresentation
import similarityMatrix
import cluster_postprocessing
import similarityMatrixFiltering

from file_path_global import *


sequenceParser.runProcess(filepath_sequence_pkl_w_ornament, filepath_pattern_candidates_w_ornament_json)
sequenceParser.runProcess(filepath_sequence_pkl_wo_ornament, filepath_pattern_candidates_wo_ornament_json)

patternRepresentation.runProcess(filepath_pattern_candidates_w_ornament_json,
           filepath_pattern_candidates_replication_w_ornament_json,
           filepath_pattern_candidates_replication_midinote_w_ornament_json)

patternRepresentation.runProcess(filepath_pattern_candidates_wo_ornament_json,
           filepath_pattern_candidates_replication_wo_ornament_json,
           filepath_pattern_candidates_replication_midinote_wo_ornament_json)

similarityMatrix.runProcess(filepath_pattern_candidates_w_ornament_json,
                           filepath_pattern_candidates_replication_midinote_w_ornament_json,
                           filepath_pattern_index_2_line_index_w_ornament_json,
                           filepath_pattern_index_2_pattern_candidates_w_ornament_json,
                           filepath_dissimlarity_matrix_replication_midinote_w_ornament_normalized_pkl)

similarityMatrix.runProcess(filepath_pattern_candidates_wo_ornament_json,
                           filepath_pattern_candidates_replication_midinote_wo_ornament_json,
                           filepath_pattern_index_2_line_index_wo_ornament_json,
                           filepath_pattern_index_2_pattern_candidates_wo_ornament_json,
                           filepath_dissimlarity_matrix_replication_midinote_wo_ornament_normalized_pkl)

similarityMatrixFiltering.runProcess(filepath_dissimlarity_matrix_replication_midinote_w_ornament_normalized_pkl,
                                     filepath_pattern_index_2_pattern_candidates_w_ornament_json)

similarityMatrixFiltering.runProcess(filepath_dissimlarity_matrix_replication_midinote_wo_ornament_normalized_pkl,
                                     filepath_pattern_index_2_pattern_candidates_wo_ornament_json)

ind_2_pattern           = json.load(open('./dissimilarityMatrix/index2Pattern_wo_ornament.json', 'r'))
dissimilarity_matrix    = pickle.load(open('./dissimilarityMatrix/dissimilarityMatrixReplicationMidinote_wo_ornament_normalized.pkl','rb'))
similarity_matrix       = 1 - dissimilarity_matrix

# for k in range(0, 21):
#     g = knnGraph(similarity_matrix, k)
#     labels = g.get_labels()
#     # g.plot()
#     print k, g.get_modularity()


def generate_cluster(g):
    labels = g.get_labels()
    g.plot()

    cluster = []
    for kk in range(max(labels)+1):
        cluster.append([ind_2_pattern[str(ii)] for ii in range(len(labels)) if labels[ii] == kk])
    return cluster


# k = 0
# g = knnGraph(similarity_matrix, k)
# clusters = generate_cluster(g)
# clusters = cluster_postprocessing.runProcess(clusters)
#
# pickle.dump(clusters, open('clusters/clusters_knn0_wo_ornament_normalized.pkl', 'wb'))

k = 5
g = knnGraph(similarity_matrix, k)
clusters = generate_cluster(g)
clusters = cluster_postprocessing.runProcess(clusters)
pickle.dump(clusters, open('clusters/clusters_knn5_wo_ornament_normalized.pkl', 'wb'))

g = weightedGraph(similarity_matrix)
clusters = generate_cluster(g)
clusters = cluster_postprocessing.runProcess(clusters)
pickle.dump(clusters, open('clusters/clusters_weighted_wo_ornament_normalized.pkl', 'wb'))

