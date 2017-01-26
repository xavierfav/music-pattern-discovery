"""
Calculate similarity matrix by different distances
"""

import json
import pickle
import numpy as np
# from editDistance import levenshtein
import editdistance


def flat_pattern_candidates(dict_pattern_candidates):

    index_pattern_flat = 0
    dict_pattern_index_2_line_index = {}
    pattern_candidates_flat = []
    for key in dict_pattern_candidates:
        pattern_candidates = dict_pattern_candidates[key]
        pattern_candidates_flat += pattern_candidates

        # arrange pattern index to line index mapping
        for ii in xrange(index_pattern_flat, len(pattern_candidates)+index_pattern_flat):
            dict_pattern_index_2_line_index[ii] = key
        index_pattern_flat += len(pattern_candidates)

    return pattern_candidates_flat, dict_pattern_index_2_line_index


def runProcess(filepath_pattern_candidates_replication_midinote_json,
               filepath_pattern_index_2_line_index_json,
               filepath_simlarity_matrix_replication_midinote_pkl,
               filepath_simlarity_matrix_replication_midinote_normalized_pkl):
    with open(filepath_pattern_candidates_replication_midinote_json, 'rb') as openfile:
        dict_pattern_candidates_replication_midinote = json.load(openfile)

    pattern_candidates_flat, dict_pattern_index_2_line_index = flat_pattern_candidates(dict_pattern_candidates_replication_midinote)

    similarity_matrix_pairwise_editdistance = np.zeros((len(pattern_candidates_flat), len(pattern_candidates_flat)))
    similarity_matrix_pairwise_editdistance_normalized = np.zeros((len(pattern_candidates_flat), len(pattern_candidates_flat)))

    for ii_pcf in xrange(len(pattern_candidates_flat)-1):
        print('calculating the '+str(ii_pcf)+'th pattern')
        for jj_pcf in xrange(ii_pcf+1, len(pattern_candidates_flat)):
            pcf_ii = pattern_candidates_flat[ii_pcf]
            pcf_jj = pattern_candidates_flat[jj_pcf]

            if pcf_ii == pcf_jj:
                similarity_matrix_pairwise_editdistance[ii_pcf, jj_pcf] = 0
            else:
                similarity_matrix_pairwise_editdistance[ii_pcf, jj_pcf] = editdistance.eval(pcf_ii, pcf_jj)
                similarity_matrix_pairwise_editdistance_normalized[ii_pcf, jj_pcf] = \
                    editdistance.eval(pcf_ii, pcf_jj)/float(max(len(pcf_ii),len(pcf_jj)))

    with open(filepath_pattern_index_2_line_index_json, 'wb') as outfile:
        json.dump(dict_pattern_index_2_line_index, outfile)

    with open(filepath_simlarity_matrix_replication_midinote_pkl, 'wb') as outfile:
        pickle.dump(similarity_matrix_pairwise_editdistance, outfile)

    with open(filepath_simlarity_matrix_replication_midinote_normalized_pkl, 'wb') as outfile:
        pickle.dump(similarity_matrix_pairwise_editdistance, outfile)

if __name__ == '__main__':

    from file_path_global import *
    runProcess(filepath_pattern_candidates_replication_midinote_w_ornament_json,
               filepath_pattern_index_2_line_index_w_ornament_json,
               filepath_simlarity_matrix_replication_midinote_w_ornament_pkl,
               filepath_simlarity_matrix_replication_midinote_w_ornament_normalized_pkl)

    runProcess(filepath_pattern_candidates_replication_midinote_wo_ornament_json,
               filepath_pattern_index_2_line_index_wo_ornament_json,
               filepath_simlarity_matrix_replication_midinote_wo_ornament_pkl,
               filepath_simlarity_matrix_replication_midinote_wo_ornament_normalized_pkl)

