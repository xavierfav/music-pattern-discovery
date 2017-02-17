import numpy as np
import json
import pickle
from operator import itemgetter
from sequenceParser import sum_length_sequence
from parameters_global import length_sequence, tolerance_length

def matrixLoad(filepath_dissimilarity_matrix_pkl):
    with open(filepath_dissimilarity_matrix_pkl, 'rb') as openfile:
        dissimilarity_matrix_pairwise_fusion = pickle.load(openfile)
    return dissimilarity_matrix_pairwise_fusion


def index2PatternLoad(filepath_index_2_pattern_candidates_json):
    with open(filepath_index_2_pattern_candidates_json, 'r') as openfile:
        dict_index_2_pattern_candidates = json.load(openfile)
    return dict_index_2_pattern_candidates


def overlapping(ii_start_end, jj_start_end):
    return max(ii_start_end[0],jj_start_end[0]) <= min(ii_start_end[1],jj_start_end[1])


def getListMatrix(dict_index_2_pattern_candidates,
                  dissimilarity_matrix_pairwise_fusion,
                  K=100):
    """
    remove overlapping pairs, sort pair according to dissimilarity
    :param dict_index_2_pattern_candidates:
    :param dissimilarity_matrix_pairwise_fusion:
    :return:
    """
    N = dissimilarity_matrix_pairwise_fusion.shape[0]
    listMatrix = []
    for ii_pcf in range(1, N):
        for jj_pcf in range(ii_pcf):
            # dissimilarity_matrix_pairwise_fusion[jj_pcf, ii_pcf]

            pcf_jj = dict_index_2_pattern_candidates[str(jj_pcf)]
            pcf_ii = dict_index_2_pattern_candidates[str(ii_pcf)]

            if pcf_ii[-1][0] == pcf_jj[-1][0]:
                end_pcf_ii = pcf_ii[-1][1] + sum_length_sequence(pcf_ii[:-1], length_sequence+tolerance_length, truncate=False)
                end_pcf_jj = pcf_jj[-1][1] + sum_length_sequence(pcf_jj[:-1], length_sequence+tolerance_length, truncate=False)
                # print(pcf_ii[-1][1], end_pcf_ii, pcf_ii[-1][0], pcf_jj[-1][1], end_pcf_jj, pcf_jj[-1][0])

                if not overlapping([pcf_ii[-1][1],end_pcf_ii],[pcf_jj[-1][1],end_pcf_jj]):
                    listMatrix.append([jj_pcf,ii_pcf,dissimilarity_matrix_pairwise_fusion[jj_pcf,ii_pcf]])
            else:
                listMatrix.append([jj_pcf,ii_pcf,dissimilarity_matrix_pairwise_fusion[jj_pcf,ii_pcf]])

    listMatrix = sorted(listMatrix, key=itemgetter(2))
    listMatrix = listMatrix[:K]
    return listMatrix


def runProcess(filepath_dissimilarity_matrix_pkl,
               filepath_index_2_pattern_candidates_json):
    dissimilarity_matrix_pairwise_fusion = matrixLoad(filepath_dissimilarity_matrix_pkl)
    dict_index_2_pattern_candidates = index2PatternLoad(filepath_index_2_pattern_candidates_json)


    listMatrix = getListMatrix(dict_index_2_pattern_candidates,
                               dissimilarity_matrix_pairwise_fusion,
                               K=100)

    # print(listMatrix)
    # resort the pattern index
    dict_new_index = {}
    l1 = [l[0] for l in listMatrix]
    l2 = [l[1] for l in listMatrix]
    for ii, l in enumerate(sorted(list(set(l1+l2)))):
        dict_new_index[l] = ii

    dissimilarity_matrix_pairwise_fusion_new = np.ones((len(dict_new_index),len(dict_new_index)))
    for l in listMatrix:
        dissimilarity_matrix_pairwise_fusion_new[dict_new_index[l[0]],dict_new_index[l[1]]] = l[2]

    for ii in range(len(dict_new_index)):
        dissimilarity_matrix_pairwise_fusion_new[ii,ii] = 0.0

    # make the symmetry matrix
    for ii_pcf in range(1, len(dict_new_index)):
        for jj_pcf in range(ii_pcf):
            dissimilarity_matrix_pairwise_fusion_new[ii_pcf, jj_pcf] \
                = dissimilarity_matrix_pairwise_fusion_new[jj_pcf, ii_pcf]
    # dissimilarity_matrix_pairwise_fusion_new /= np.max(dissimilarity_matrix_pairwise_fusion_new)

    # print(dissimilarity_matrix_pairwise_fusion_new, np.max(dissimilarity_matrix_pairwise_fusion_new))

    dict_index_2_pattern_candidates_new = {}
    for key in dict_new_index:
        dict_index_2_pattern_candidates_new[dict_new_index[key]] = dict_index_2_pattern_candidates[str(key)]

    with open(filepath_index_2_pattern_candidates_json, 'w') as outfile:
        json.dump(dict_index_2_pattern_candidates_new, outfile)

    with open(filepath_dissimilarity_matrix_pkl, 'wb') as outfile:
        pickle.dump(dissimilarity_matrix_pairwise_fusion_new, outfile)

if __name__ == '__main__':
    from file_path_global import *
    runProcess(filepath_dissimlarity_matrix_replication_midinote_wo_ornament_normalized_pkl,
               filepath_pattern_index_2_pattern_candidates_wo_ornament_json)
