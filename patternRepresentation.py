"""
Functions convert pattern in (E4, 2.0) format to different representations
"""

import json

def solmization_2_midinote(solmization):
    """
    convert solmization name to midinote
    :param solmization:
    :return:
    """

    if solmization == 'rest':
        return -1
    Notes = [["C"], ["C#", "Db"], ["D"], ["D#", "Eb"], ["E"], ["F"], ["F#", "Gb"], ["G"], ["G#", "Ab"], ["A"],
             ["A#", "Bb"], ["B"]]
    midinote = 0
    i = 0
    # Note
    letter = solmization[:-1].upper()
    for note in Notes:
        if letter in note:
            midinote = i
        i += 1
    # Octave
    midinote += (int(solmization[-1])) * 12
    return midinote


def note_tuple_2_midi_tuple(note):
    """
    convert ('C4', 2) to (48, 2)
    :param note:
    :return:
    """
    midi_tuple = (solmization_2_midinote(note[0]), note[1])
    return midi_tuple


def replication_representation(pattern):
    """
    convert ('C4', 3) to ('C4', 'C4', 'C4')
    :param pattern:
    :return:
    """
    pattern_replication = []
    for note in pattern:
        pattern_replication += [note[0]]*int(note[1])
    return tuple(pattern_replication)


def runProcess(filepath_pattern_candidates_json,
               filepath_pattern_candidates_replication_json,
               filepath_pattern_candidates_replication_midinote_json):
    """
    replicate the pattern candidates
    :param filepath_pattern_candidates_json:
    :param filepath_pattern_candidates_replication_json:
    :param filepath_pattern_candidates_replication_midinote_json:
    :return:
    """
    with open(filepath_pattern_candidates_json, 'r') as openfile:
        dict_pattern_candidates = json.load(openfile)

        # shitty part of converting the pattern candidates to replication form
        # then convert to midinote form
    dict_pattern_candidates_replication = {}
    dict_pattern_candidates_replication_midinote = {}
    for key in dict_pattern_candidates:
        pattern_candidates_replication = []
        pattern_candidates_replication_midinote = []
        for pattern_candidate in dict_pattern_candidates[key]:
            pattern_candidate_replication = replication_representation(pattern_candidate[:-1])
            pattern_candidates_replication.append(pattern_candidate_replication)
            pattern_candidate_replication_midinote = []
            for solmization_note in pattern_candidate_replication:
                pattern_candidate_replication_midinote.append(solmization_2_midinote(solmization_note))
            pattern_candidates_replication_midinote.append(pattern_candidate_replication_midinote)


        dict_pattern_candidates_replication[key] = pattern_candidates_replication
        dict_pattern_candidates_replication_midinote[key] = pattern_candidates_replication_midinote

    with open(filepath_pattern_candidates_replication_json, 'w') as outfile:
        json.dump(dict_pattern_candidates_replication, outfile)

    with open(filepath_pattern_candidates_replication_midinote_json, 'w') as outfile:
        json.dump(dict_pattern_candidates_replication_midinote, outfile)


if __name__ == '__main__':
    from file_path_global import *

    runProcess(filepath_pattern_candidates_w_ornament_json,
               filepath_pattern_candidates_replication_w_ornament_json,
               filepath_pattern_candidates_replication_midinote_w_ornament_json)

    runProcess(filepath_pattern_candidates_wo_ornament_json,
               filepath_pattern_candidates_replication_wo_ornament_json,
               filepath_pattern_candidates_replication_midinote_wo_ornament_json)