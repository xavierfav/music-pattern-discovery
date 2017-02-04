"""
Functions parsing the sequences of Rafa to pattern candidates.
"""

import pickle
import json
from parameters_global import length_sequence_minimum


def sequence_pkl_reader(filename_sequence_pkl):
    """
    Read sequence pkl
    :param filename_sequence_pkl
    :return: [line1,line2,...], line1 = [(u'E4', 8.0), (u'A4', 2.0), ...]
    """
    with open(filename_sequence_pkl, 'rb') as f:
        sequences = pickle.load(f)
    return sequences


def sum_length_pattern(pattern):
    """
    Summation length of a pattern
    :param pattern:
    :return:
    """
    sum_len_pattern = 0
    for note in pattern:
        sum_len_pattern += int(note[1])
    return sum_len_pattern


def sequence_collector_all_possible(sequence):
    """
    collect all possible pattern candidate if its length >= length_pattern_minimum
    :param sequence: a line, NOT a list of lines
    :return:
    """
    pattern_candidates = []
    for ii_start in xrange(0, len(sequence)-1):
        for ii_end in xrange(ii_start+1, len(sequence)):
            pattern_candidate = sequence[ii_start:ii_end+1]
            if sum_length_pattern(pattern_candidate) >= length_sequence_minimum:
                pattern_candidates.append(tuple(pattern_candidate))
    return pattern_candidates


def sequence_collector_filtered(sequence, length_sequence, tolerance_length, note_number_minimum):
    """
    collect sequence candidate if its absolute length <= length_pattern + tolerance_length
    :param sequence: a line, NOT a list of lines
    :param length_sequence:
    :param tolerance_length:
    :param note_number_minimum: sequence note number <= this number will be filtered out
    :return:
    """
    sequence_candidates = []
    for ii_start in xrange(0, len(sequence)-1):
        sequence_candidates_ii_start_intolerance = []
        for ii_end in xrange(ii_start+1, len(sequence)):
            sequence_candidate = sequence[ii_start:ii_end+1]

            # remove restsequence_collector_limit_length
            # print('normal')
            # print sequence_candidate
            if sequence_candidate[0][0] == 'rest':
                # print('with rest ')
                # print(sequence_candidate)
                sequence_candidate = sequence_candidate[1:]
                # print('without rest')
                # print(sequence_candidate)
            if sequence_candidate[-1][0] == 'rest':
                sequence_candidate = sequence_candidate[:-1]

            if (length_sequence - tolerance_length <= sum_length_pattern(sequence_candidate) <= length_sequence + tolerance_length) and \
                            len(sequence_candidate) > note_number_minimum:
                sequence_candidates_ii_start_intolerance.append(tuple(sequence_candidate))

        # filter the sequence_candidates_ii_start_intolerance
        # we just want one pattern candidate with the same ii_start
        # find the pattern whose length is nearest to length_pattern
        min_diff = length_sequence + 2 * tolerance_length
        sequence_candidate_selected = []
        if len(sequence_candidates_ii_start_intolerance) > 0:
            if len(sequence_candidates_ii_start_intolerance) > 1:
                for pcit in sequence_candidates_ii_start_intolerance:
                    if abs(sum_length_pattern(pcit) - length_sequence) < min_diff:
                        min_diff = abs(sum_length_pattern(pcit) - length_sequence)
                        sequence_candidate_selected = pcit
            elif len(sequence_candidates_ii_start_intolerance) == 1:
                sequence_candidate_selected = sequence_candidates_ii_start_intolerance[0]
            sequence_candidates.append(sequence_candidate_selected)

    return sequence_candidates


def runProcess(filepath_sequence_pkl, filepath_pattern_candidates_json):
    """
    run the process of parsing sequence from Rafa to patter dictionary
    :param filepath_sequence_pkl:
    :param filepath_pattern_candidates_json:
    :return:
    """

    from parameters_global import length_sequence, tolerance_length, note_number_minimum

    sequences = sequence_pkl_reader(filepath_sequence_pkl)

    # collect pattern candidates in each line (sequence)
    dict_pattern_candidates = {}
    for ii_sequence, sequence in enumerate(sequences):
        pattern_candidates = sequence_collector_filtered(sequence, length_sequence, tolerance_length, note_number_minimum)
        if len(pattern_candidates):
            dict_pattern_candidates[ii_sequence] = tuple(pattern_candidates)

    # print sum([len(ii) for ii in dict_pattern_candidates.values()])

    with open(filepath_pattern_candidates_json, 'wb') as outfile:
        json.dump(dict_pattern_candidates, outfile)

if __name__ == '__main__':

    from file_path_global import *

    runProcess(filepath_sequence_pkl_w_ornament, filepath_pattern_candidates_w_ornament_json)
    runProcess(filepath_sequence_pkl_wo_ornament, filepath_pattern_candidates_wo_ornament_json)