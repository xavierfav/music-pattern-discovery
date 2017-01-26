"""
Functions parsing the sequences of Rafa to pattern candidates.
"""

import pickle
import json
from parameters_global import length_pattern_minimum


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


def pattern_collector(sequence):
    """
    collect pattern candidate if its length >= length_pattern_minimum
    :param sequence: a line, NOT a list of lines
    :return:
    """
    pattern_candidates = []
    for ii_start in xrange(0, len(sequence)-1):
        for ii_end in xrange(ii_start+1, len(sequence)):
            pattern_candidate = sequence[ii_start:ii_end+1]
            if sum_length_pattern(pattern_candidate) >= length_pattern_minimum:
                pattern_candidates.append(tuple(pattern_candidate))
    return pattern_candidates


def runProcess(filepath_sequence_pkl, filepath_pattern_candidates_json):
    """
    run the process of parsing sequence from Rafa to patter dictionary
    :param filepath_sequence_pkl:
    :param filepath_pattern_candidates_json:
    :return:
    """
    sequences = sequence_pkl_reader(filepath_sequence_pkl)

    # collect pattern candidates in each line (sequence)
    dict_pattern_candidates = {}
    for ii_sequence, sequence in enumerate(sequences):
        dict_pattern_candidates[ii_sequence] = tuple(pattern_collector(sequence))

    with open(filepath_pattern_candidates_json, 'wb') as outfile:
        json.dump(dict_pattern_candidates, outfile)

if __name__ == '__main__':

    from file_path_global import *

    runProcess(filepath_sequence_pkl_w_ornament, filepath_pattern_candidates_w_ornament_json)
    runProcess(filepath_sequence_pkl_wo_ornament, filepath_pattern_candidates_wo_ornament_json)