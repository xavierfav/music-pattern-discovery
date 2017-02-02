"""
Calculate similarity matrix by different distances
"""

import json
import pickle
import numpy as np
# from editDistance import levenshtein
import editdistance
from dtwSankalp import dtw1d_std


def flat_pattern_candidates(dict_pattern_candidates):

    index_pattern_flat = 0
    dict_pattern_index_2_line_index = {}
    pattern_candidates_flat = []

    # sort convert keys into int and sort
    keys_int_sorted = sorted([int(ii) for ii in dict_pattern_candidates.keys()])

    for ii in keys_int_sorted:
        key = str(ii)
        try:
            pattern_candidates = dict_pattern_candidates[key]
            pattern_candidates_flat += pattern_candidates

            # arrange pattern index to line index mapping
            for ii in xrange(index_pattern_flat, len(pattern_candidates)+index_pattern_flat):
                dict_pattern_index_2_line_index[ii] = key
            index_pattern_flat += len(pattern_candidates)
        except KeyError:
            print('Key doesn''t exist '+key)

    return pattern_candidates_flat, dict_pattern_index_2_line_index


def interp_fix_length(pattern):
    """
    interpolation of pattern to fixed length
    :param pattern:
    :return:
    """
    from parameters_global import length_pattern

    x = np.linspace(0, len(pattern) - 1, len(pattern))
    xvals = np.linspace(0, len(pattern) - 1, length_pattern)
    yinterp = np.interp(xvals, x, pattern)

    return yinterp


def distance_dtw(pattern0, pattern1):
    """
    dtw distance of two patterns
    :param pattern0:
    :param pattern1:
    :return:
    """
    pattern0_interp = interp_fix_length(pattern0)
    pattern1_interp = interp_fix_length(pattern1)
    dist_dtw, path_align = dtw1d_std(pattern0_interp, pattern1_interp)

    dist_dtw_normalized = dist_dtw/len(path_align[0])
    return dist_dtw, dist_dtw_normalized


def distance_starting_ending_notes(pattern0, pattern1):
    """
    distance comparing the starting and the ending notes of two patterns
    :param pattern0: midinote replication pattern
    :param pattern1: same as above
    :return:
    """
    if not all([isinstance(note_replication, int) for note_replication in pattern0]):
        raise TypeError("All element of pattern should be integer.")
    if not all([isinstance(note_replication, int) for note_replication in pattern1]):
        raise TypeError("All element of pattern should be integer.")

    # 1.1 avoid 0 dissimilarity
    distance_pattern0 = 1 - 1.0/(abs(pattern0[0] - pattern1[0]) + 1.1)
    distance_pattern1 = 1 - 1.0/(abs(pattern0[-1] - pattern1[-1]) + 1.1)

    distance = (distance_pattern0 + distance_pattern1) / 2.0

    return distance


def runProcess(filepath_pattern_candidates_json,
               filepath_pattern_candidates_replication_midinote_json,
               filepath_pattern_index_2_line_index_json,
               filepath_index_2_pattern_candidates_json,
               filepath_dissimlarity_matrix_replication_midinote_normalized_pkl):

    # get similarity matrix index to pattern dictionary
    with open(filepath_pattern_candidates_json, 'rb') as openfile:
        dict_pattern_candidates = json.load(openfile)
    pattern_candidates_flat, _ = flat_pattern_candidates(dict_pattern_candidates)

    dict_index_2_pattern_candidates = {}
    for ii_pc, pattern_candidate in enumerate(pattern_candidates_flat):
        dict_index_2_pattern_candidates[ii_pc] = pattern_candidate

    with open(filepath_pattern_candidates_replication_midinote_json, 'rb') as openfile:
        dict_pattern_candidates_replication_midinote = json.load(openfile)

    pattern_candidates_replication_midinote_flat, dict_pattern_index_2_line_index = flat_pattern_candidates(dict_pattern_candidates_replication_midinote)

    dissimilarity_matrix_pairwise_editdistance_normalized = np.zeros((len(pattern_candidates_replication_midinote_flat), len(pattern_candidates_replication_midinote_flat)))
    dissimilarity_matrix_pairwise_dtwdistance_normalized = np.zeros((len(pattern_candidates_replication_midinote_flat), len(pattern_candidates_replication_midinote_flat)))
    dissimilarity_matrix_pairwise_beginning_ending_normalized = np.zeros((len(pattern_candidates_replication_midinote_flat), len(pattern_candidates_replication_midinote_flat)))

    for ii_pcf in xrange(len(pattern_candidates_replication_midinote_flat)-1):
        print('calculating the '+str(ii_pcf)+'th pattern')
        for jj_pcf in xrange(ii_pcf+1, len(pattern_candidates_replication_midinote_flat)):
            pcf_ii = pattern_candidates_replication_midinote_flat[ii_pcf]
            pcf_jj = pattern_candidates_replication_midinote_flat[jj_pcf]

            if pcf_ii == pcf_jj:
                dissimilarity_matrix_pairwise_editdistance_normalized[ii_pcf, jj_pcf] = 0
                dissimilarity_matrix_pairwise_dtwdistance_normalized[ii_pcf, jj_pcf] = 0
                dissimilarity_matrix_pairwise_beginning_ending_normalized[ii_pcf, jj_pcf] = 0
            else:
                # edit distance
                dissimilarity_matrix_pairwise_editdistance_normalized[ii_pcf, jj_pcf] = \
                    editdistance.eval(pcf_ii, pcf_jj)/float(max(len(pcf_ii), len(pcf_jj)))

                # dtw distance
                _, dissimilarity_matrix_pairwise_dtwdistance_normalized[ii_pcf, jj_pcf] = \
                    distance_dtw(pcf_ii, pcf_jj)

                # beginning and ending distance
                dissimilarity_matrix_pairwise_beginning_ending_normalized[ii_pcf, jj_pcf] = \
                    distance_starting_ending_notes(pcf_ii, pcf_jj)

    # normalize dissimilarity matrix
    dissimilarity_matrix_pairwise_dtwdistance_normalized /= np.max(dissimilarity_matrix_pairwise_dtwdistance_normalized)
    dissimilarity_matrix_pairwise_beginning_ending_normalized /= np.max(dissimilarity_matrix_pairwise_beginning_ending_normalized)

    dissimilarity_matrix_pairwise_fusion = \
        dissimilarity_matrix_pairwise_editdistance_normalized * \
        dissimilarity_matrix_pairwise_dtwdistance_normalized * \
        dissimilarity_matrix_pairwise_beginning_ending_normalized

    # normalize dissimilarity matrix fusion
    dissimilarity_matrix_pairwise_fusion /= np.max(dissimilarity_matrix_pairwise_fusion)

    # make the symmetry matrix
    for ii_pcf in xrange(1, len(pattern_candidates_replication_midinote_flat)):
        for jj_pcf in xrange(ii_pcf):
            dissimilarity_matrix_pairwise_fusion[ii_pcf, jj_pcf] \
                = dissimilarity_matrix_pairwise_fusion[jj_pcf, ii_pcf]

    with open(filepath_pattern_index_2_line_index_json, 'wb') as outfile:
        json.dump(dict_pattern_index_2_line_index, outfile)

    with open(filepath_index_2_pattern_candidates_json, 'wb') as outfile:
        json.dump(dict_index_2_pattern_candidates, outfile)

    with open(filepath_dissimlarity_matrix_replication_midinote_normalized_pkl, 'wb') as outfile:
        pickle.dump(dissimilarity_matrix_pairwise_fusion, outfile)

if __name__ == '__main__':

    from file_path_global import *
    runProcess(filepath_pattern_candidates_w_ornament_json,
               filepath_pattern_candidates_replication_midinote_w_ornament_json,
               filepath_pattern_index_2_line_index_w_ornament_json,
               filepath_pattern_index_2_pattern_candidates_w_ornament_json,
               filepath_dissimlarity_matrix_replication_midinote_w_ornament_normalized_pkl)

    runProcess(filepath_pattern_candidates_wo_ornament_json,
               filepath_pattern_candidates_replication_midinote_wo_ornament_json,
               filepath_pattern_index_2_line_index_wo_ornament_json,
               filepath_pattern_index_2_pattern_candidates_wo_ornament_json,
               filepath_dissimlarity_matrix_replication_midinote_wo_ornament_normalized_pkl)

