from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import spectral_clustering
#from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn import metrics
import networkx as nx
import community.community_louvain as com
import numpy as np
import operator
from sklearn.datasets.samples_generator import make_blobs
from sklearn.metrics.pairwise import euclidean_distances
import matplotlib.pyplot as plt
import json


def kmeans(data, n_clusters=5):
    km = KMeans(n_cluster=n_clusters, init='k-means++', max_iter=200, n_init=1)
    km.fit(data)
    return km.labels_

def affinityPropagation(data, preference=-50):
    af = AffinityPropagation(preference=preference)
    af.fit(data)
    return af.labels_

def meanShift(data):
    bandwidth = estimate_bandwidth(data, quantile=0.2)
    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(data)
    return ms.labels_

def spectral(similarity_matrix):
    labels = spectral_clustering(similarity_matrix)
    return labels

def dbscan(data):
    db = DBSCAN(eps=0.3, min_samples=10)
    db.fit(data)
    return db.labels_

def agglomerative(data):
    # check here how to return the labels
    Z = linkage(data, 'Ward')
    return Z

class Graph():
    def __init__(self):
        pass
        
    def get_labels(self):
        return [self.classes[k] for k in range(len(self.classes.keys()))]
    
    def plot(self):
        nx.draw(self.graph)
        plt.show()
    
    def get_clusters(self):
        id_to_seq = json.load(open('dissimilarityMatrix/index2Pattern_w_ornament.json', 'rb'))
        labels = self.get_labels()
        clusters = []
        for k in range(max(labels)):
            clusters.append([id_to_seq[str(s)] for s in range(2022) if labels[s]==k])  
        return clusters

class weightedGraph(Graph):
    """
    Graph based clustering using Louvain aglorithm.
    
    Dependencies
    ----------
    networkx, community, matplotlib
    
    Parameters
    ----------
    similarity_matrix : 2D array
    """
    
    def __init__(self, similarity_matrix):
        self.graph = self.create_weighted_graph(similarity_matrix)
        self.classes = com.best_partition(self.graph)
        
    def create_weighted_graph(self, similarity_matrix):
        """ Returns a weighted from a similarity matrix - NetworkX module """
        np.fill_diagonal(similarity_matrix, 0) # for removing the 1 from diagonal
        g = nx.Graph()
        g.add_nodes_from(range(len(similarity_matrix)))
        for idx in range(len(similarity_matrix)):
            g.add_weighted_edges_from([(idx, i[0], i[1]) for i in zip(range(len(similarity_matrix)), similarity_matrix[idx]) if i[0]!=idx and i[1]!=0])
        return g     

class knnGraph(Graph):
    """
    Knn-graph based clustering using Louvain aglorithm.
    
    Dependencies
    ----------
    networkx, community, matplotlib
    
    Parameters
    ----------
    similarity_matrix : 2D array
    
    k_nn : int
        the parameter of the k nearest neighbour for graph generation. Default to 20
        
    Examples
    --------
    import pickle
    import numpy as np
    from clustering_methods import *
    dissimilarity_matrix = pickle.load(open('outputData/dissimilarityMatrixReplicationMidinote_w_ornament_normalized.pkl','rb'))
    similarity_matrix = 1 - dissimilarity_matrix
    g = knnGraph(similarity_matrix)
    labels = g.get_labels()
    g.plot()  
    """
    
    def __init__(self, similarity_matrix, k=20):
        self.graph = self.create_knn_graph(similarity_matrix, k)
        self.classes = com.best_partition(self.graph)
        
    def create_knn_graph(self, similarity_matrix, k):
        """ Returns a knn graph from a similarity matrix - NetworkX module """
        np.fill_diagonal(similarity_matrix, 0) # for removing the 1 from diagonal
        g = nx.Graph()
        g.add_nodes_from(range(len(similarity_matrix)))
        for idx in range(len(similarity_matrix)):
            g.add_edges_from([(idx, i) for i in self.k_nearest_neighbors(similarity_matrix, idx, k)])
        return g  
    
    @staticmethod
    def k_nearest_neighbors(similarity_matrix, idx, k):
        distances = []
        for x in range(len(similarity_matrix)):
            distances.append((x, similarity_matrix[idx][x]))
        distances.sort(key=operator.itemgetter(1), reverse=True)
        if k>0:
            return [d[0] for d in distances[0:k]]
        if k==0:
            # extract the more similar one with the highest similarity
            r = []
            i = distances[0][1]
            idx = 0
            while (i==distances[0][1]):
                r.append(distances[idx][0])
                idx += 1
                i = distances[idx][1]
            return r

#X, y = make_blobs(n_samples=10, centers=10, n_features=2, random_state=0)
#similarity = euclidean_distances(X)

def evaluate(labels_true, labels):
    homogeneity = metrics.homogeneity_score(labels_true, labels)
    completeness = metrics.completeness_score(labels_true, labels)
    v_measure = metrics.v_measure_score(labels_true, labels)
    adjusted_rand = metrics.adjusted_rand_score(labels_true, labels)
    adjusted_mutual_info = metrics.adjusted_mutual_info_score(labels_true, labels)
    #silhouette = metrics.silhouette_score(data, labels, metric='sqeuclidean')
    return homogeneity, completeness, v_measure, adjusted_rand, adjusted_mutual_info#, silhouette

