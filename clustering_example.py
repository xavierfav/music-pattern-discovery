import pickle
import json
import numpy as np
from clustering_methods import *


ind_2_pattern = json.load(open('/home/gong/PycharmProjects/music-pattern-discovery/dissimilarityMatrix/index2Pattern_wo_ornament.json', 'rb'))
dissimilarity_matrix = pickle.load(open('dissimilarityMatrix/dissimilarityMatrixReplicationMidinote_wo_ornament_normalized.pkl','rb'))
similarity_matrix = 1 - dissimilarity_matrix

# for k in range(0, 21):
#     g = knnGraph(similarity_matrix, k)
#     labels = g.get_labels()
#     # g.plot()
#     print k, g.get_modularity()


def generate_cluster(g):
    labels = g.get_labels()
    g.plot()

    cluster = []
    for kk in xrange(max(labels)+1):
        cluster.append([ind_2_pattern[str(ii)] for ii in xrange(len(labels)) if labels[ii] == kk])
    return cluster


k = 0
g = knnGraph(similarity_matrix, k)
cluster = generate_cluster(g)
pickle.dump(cluster, open('clusters/clusters_knn0_wo_ornament_normalized.pkl', 'wb'))

k = 5
g = knnGraph(similarity_matrix, k)
cluster = generate_cluster(g)
pickle.dump(cluster, open('clusters/clusters_knn5_wo_ornament_normalized.pkl', 'wb'))

g = weightedGraph(similarity_matrix)
cluster = generate_cluster(g)
pickle.dump(cluster, open('clusters/clusters_weighted_wo_ornament_normalized.pkl', 'wb'))

