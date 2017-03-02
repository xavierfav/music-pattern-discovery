import numpy as np
import json
import pickle
from operator import itemgetter
from sequenceParser import sum_length_sequence
from parameters_global import length_sequence, tolerance_length
from itertools import combinations
from patternRepresentation import replication_representation, solmization_2_midinote
from similarityMatrix import distance_dtw, distance_starting_ending_notes


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

            # examine if two sequences are overlapping, firstly, they should be at the same sentence
            # pcf_ii[-1][0] is the sentence number
            if pcf_ii[-1][0] == pcf_jj[-1][0]:
                end_pcf_ii = pcf_ii[-1][1] + len(pcf_ii[:-1]) - 1
                end_pcf_jj = pcf_jj[-1][1] + len(pcf_jj[:-1]) - 1
                # print(pcf_ii[-1][1], end_pcf_ii, pcf_ii[-1][0], pcf_jj[-1][1], end_pcf_jj, pcf_jj[-1][0])

                if not overlapping([pcf_ii[-1][1],end_pcf_ii],[pcf_jj[-1][1],end_pcf_jj]):
                    listMatrix.append([jj_pcf,ii_pcf,dissimilarity_matrix_pairwise_fusion[jj_pcf,ii_pcf]])
            else:
                listMatrix.append([jj_pcf,ii_pcf,dissimilarity_matrix_pairwise_fusion[jj_pcf,ii_pcf]])

    listMatrix = sorted(listMatrix, key=itemgetter(2))
    listMatrix = listMatrix[:K]
    return listMatrix


def mergeSequences(seq0, seq1):
    """
    merge two overlapped sequences
    :param seq0:
    :param seq1:
    :return:
    """
    if seq1[-1][1] < seq0[-1][1]:
        # swith to make sure seq1 comes after seq0
        temp_seq = seq0[:]
        seq0     = seq1
        seq1     = temp_seq

    merged = seq0[:seq1[-1][1]-seq0[-1][1]] + seq1[:-1] + seq0[-1:]

    # merged_first = [note[0] for note in merged[:-1]]
    # for ii in merged_first:
    #     if isinstance(ii, int):
    #         print(merged)
    return merged

def mergeSequencePairBatch(listMatrix, dict_index_2_pattern_candidates):
    """
    Merge sequence pair if they both overlap
    :param listMatrix: sorted filtered similar sequence pairs
    :param dict_index_2_pattern_candidates:
    :return:
    """
    idx_dict_biggest = max([int(key) for key in dict_index_2_pattern_candidates])

    for comb_3 in combinations(listMatrix, 2):
        pair_0 = comb_3[0]
        pair_1 = comb_3[1]
        idx_0_pair_0 = pair_0[0]
        idx_1_pair_0 = pair_0[1]
        idx_0_pair_1 = pair_1[0]
        idx_1_pair_1 = pair_1[1]
        seq_0_0 = dict_index_2_pattern_candidates[str(idx_0_pair_0)]
        seq_0_1 = dict_index_2_pattern_candidates[str(idx_1_pair_0)]
        seq_1_0 = dict_index_2_pattern_candidates[str(idx_0_pair_1)]
        seq_1_1 = dict_index_2_pattern_candidates[str(idx_1_pair_1)]

        # first, let's test if the sequences are in the same phrase

        if len(list({seq_0_0[-1][0], seq_1_0[-1][0], seq_0_1[-1][0], seq_1_1[-1][0]})) <= 2:
            # the case if the phrase space fo all four sequences are <= 2
            end_seq_0_0 = seq_0_0[-1][1] + len(seq_0_0[:-1]) - 1
            end_seq_1_0 = seq_1_0[-1][1] + len(seq_1_0[:-1]) - 1
            end_seq_0_1 = seq_0_1[-1][1] + len(seq_0_1[:-1]) - 1
            end_seq_1_1 = seq_1_1[-1][1] + len(seq_1_1[:-1]) - 1

            # if seq_0_0 == [['F#4', 8.0, False], ['F#4', 8.0, False], ['G#4', 16.0, False], [32, 8]] or \
            #     seq_0_1 == [['F#4', 8.0, False], ['F#4', 8.0, False], ['G#4', 16.0, False], [32, 8]] or \
            #     seq_0_1 == [['F#4', 8.0, False], ['F#4', 8.0, False], ['G#4', 16.0, False], [32, 8]] or \
            #     seq_1_0 == [['F#4', 8.0, False], ['F#4', 8.0, False], ['G#4', 16.0, False], [32, 8]]:
            #     print(seq_0_0)
            #     print(seq_0_1)
            #     print(seq_1_0)
            #     print(seq_1_1)

            if seq_0_0[-1][0] == seq_1_0[-1][0] and seq_0_1[-1][0] == seq_1_1[-1][0]:
                if overlapping([seq_0_0[-1][1],end_seq_0_0],[seq_1_0[-1][1],end_seq_1_0]) and \
                        overlapping([seq_0_1[-1][1],end_seq_0_1],[seq_1_1[-1][1],end_seq_1_1]):
                    # seq_0_0 overlap with seq_1_0 and seq_0_1 with seq_1_1

                    # delete overlapped sequences in listMatrix
                    if pair_0 in listMatrix:
                        listMatrix.remove(pair_0)
                    if pair_1 in listMatrix:
                        listMatrix.remove(pair_1)

                    seq_merged_0 = mergeSequences(seq_0_0, seq_1_0)
                    seq_merged_1 = mergeSequences(seq_0_1, seq_1_1)
                    # add merged sequences into dict
                    idx_merged_0 = idx_dict_biggest + 1
                    idx_dict_biggest += 1
                    dict_index_2_pattern_candidates[str(idx_merged_0)] = seq_merged_0
                    idx_merged_1 = idx_dict_biggest + 1
                    idx_dict_biggest += 1
                    dict_index_2_pattern_candidates[str(idx_merged_1)] = seq_merged_1

                    listMatrix.append((idx_merged_0, idx_merged_1, None))

            if seq_0_0[-1][0] == seq_1_1[-1][0] and seq_0_1[-1][0] == seq_1_0[-1][0]:
                if overlapping([seq_0_0[-1][1], end_seq_0_0], [seq_1_1[-1][1], end_seq_1_1]) and \
                        overlapping([seq_0_1[-1][1], end_seq_0_1], [seq_1_0[-1][1], end_seq_1_0]):
                    # delete overlapped sequences in listMatrix
                    if pair_0 in listMatrix:
                        listMatrix.remove(pair_0)
                    if pair_1 in listMatrix:
                        listMatrix.remove(pair_1)

                    seq_merged_0 = mergeSequences(seq_0_0, seq_1_1)
                    seq_merged_1 = mergeSequences(seq_0_1, seq_1_0)
                    # add merged sequences into dict
                    idx_merged_0 = idx_dict_biggest + 1
                    idx_dict_biggest += 1
                    dict_index_2_pattern_candidates[str(idx_merged_0)] = seq_merged_0
                    idx_merged_1 = idx_dict_biggest + 1
                    idx_dict_biggest += 1
                    dict_index_2_pattern_candidates[str(idx_merged_1)] = seq_merged_1

                    listMatrix.append((idx_merged_0, idx_merged_1, None))
    return listMatrix, dict_index_2_pattern_candidates


def runProcess(filepath_dissimilarity_matrix_pkl,
               filepath_index_2_pattern_candidates_json):

    dissimilarity_matrix_pairwise_fusion = matrixLoad(filepath_dissimilarity_matrix_pkl)
    dict_index_2_pattern_candidates = index2PatternLoad(filepath_index_2_pattern_candidates_json)


    listMatrix = getListMatrix(dict_index_2_pattern_candidates,
                               dissimilarity_matrix_pairwise_fusion,
                               K=50)

    listMatrix, dict_index_2_pattern_candidates = mergeSequencePairBatch(listMatrix, dict_index_2_pattern_candidates)

    print(listMatrix)
    print(dict_index_2_pattern_candidates)

    # remove identical sequences
    flipped = {}
    for key, value in dict_index_2_pattern_candidates.items():
        value = tuple([tuple(note) for note in value])
        if value not in flipped:
            flipped[value] = [key]
        else:
            flipped[value].append(key)

    for key, value in flipped.items():
        if len(value) > 1:
            for v in value[1:]:
                substitued_v = int(value[0])
                to_substitued_v = int(v)
                for ii in range(len(listMatrix)):
                    if listMatrix[ii][0] == to_substitued_v:
                        listMatrix[ii] = [substitued_v, listMatrix[ii][1]]
                    elif listMatrix[ii][1] == to_substitued_v:
                        listMatrix[ii] = [listMatrix[ii][0], substitued_v]
                dict_index_2_pattern_candidates.pop(v, None)

    # print(listMatrix)
    # for v in dict_index_2_pattern_candidates.values():
    #     print(v)
    # resort the pattern index
    dict_new_index = {}
    l1 = [l[0] for l in listMatrix]
    l2 = [l[1] for l in listMatrix]
    for ii, l in enumerate(sorted(list(set(l1+l2)))):
        dict_new_index[l] = ii

    for ii in range(len(listMatrix)):
        listMatrix[ii] = (dict_new_index[listMatrix[ii][0]], dict_new_index[listMatrix[ii][1]])

    # reorganize the dictionary
    dict_index_2_pattern_candidates_new = {}
    dict_index_2_pattern_candidates_new_midinote = {}
    for key in dict_new_index:
        dict_index_2_pattern_candidates_new[dict_new_index[key]] = dict_index_2_pattern_candidates[str(key)]
        print(dict_index_2_pattern_candidates[str(key)][:-1])
        # for rr in replication_representation(dict_index_2_pattern_candidates[str(key)][:-1]):
            # print(rr)
            # print(solmization_2_midinote(rr))
        dict_index_2_pattern_candidates_new_midinote[dict_new_index[key]] = \
            [solmization_2_midinote(rr) for rr in replication_representation(dict_index_2_pattern_candidates[str(key)][:-1])]

    # recalculate the similarity matrix
    dissimilarity_matrix_pairwise_dtw_new               = np.zeros((len(dict_new_index),len(dict_new_index)))
    dissimilarity_matrix_pairwise_beginning_ending_new  = np.zeros((len(dict_new_index),len(dict_new_index)))
    for l in listMatrix:

        _,dissimilarity_matrix_pairwise_dtw_new[l[0],l[1]] = \
            distance_dtw(dict_index_2_pattern_candidates_new_midinote[l[0]],
                         dict_index_2_pattern_candidates_new_midinote[l[1]])
        dissimilarity_matrix_pairwise_beginning_ending_new[l[0], l[1]] = \
            distance_starting_ending_notes(dict_index_2_pattern_candidates_new_midinote[l[0]],
                                           dict_index_2_pattern_candidates_new_midinote[l[1]])

    # normalization
    dissimilarity_matrix_pairwise_dtw_new = np.log(dissimilarity_matrix_pairwise_dtw_new + 1)

    dissimilarity_matrix_pairwise_dtw_new /= np.max(dissimilarity_matrix_pairwise_dtw_new)

    dissimilarity_matrix_pairwise_beginning_ending_new /= np.max(
        dissimilarity_matrix_pairwise_beginning_ending_new)

    dissimilarity_matrix_pairwise_fusion_new = \
        dissimilarity_matrix_pairwise_dtw_new * \
        dissimilarity_matrix_pairwise_beginning_ending_new

    # make the symmetry matrix
    for ii_pcf in range(1, len(dict_new_index)):
        for jj_pcf in range(ii_pcf):
            dissimilarity_matrix_pairwise_fusion_new[ii_pcf, jj_pcf] \
                = dissimilarity_matrix_pairwise_fusion_new[jj_pcf, ii_pcf]

    for ii_pcf in range(0, len(dict_new_index)):
        for jj_pcf in range(0, len(dict_new_index)):
            if ii_pcf != jj_pcf and (ii_pcf, jj_pcf) not in listMatrix:
                dissimilarity_matrix_pairwise_fusion_new[ii_pcf, jj_pcf] = 1.0


    # dissimilarity_matrix_pairwise_fusion_new /= np.max(dissimilarity_matrix_pairwise_fusion_new)

    # print(dissimilarity_matrix_pairwise_fusion_new, np.max(dissimilarity_matrix_pairwise_fusion_new))


    with open(filepath_index_2_pattern_candidates_json, 'w') as outfile:
        json.dump(dict_index_2_pattern_candidates_new, outfile)

    with open(filepath_dissimilarity_matrix_pkl, 'wb') as outfile:
        pickle.dump(dissimilarity_matrix_pairwise_fusion_new, outfile)

if __name__ == '__main__':
    from file_path_global import *
    runProcess(filepath_dissimlarity_matrix_replication_midinote_wo_ornament_normalized_pkl,
               filepath_pattern_index_2_pattern_candidates_wo_ornament_json)
