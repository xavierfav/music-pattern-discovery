# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 15:54:23 2017

@author: Rafael.Ctt
"""

import os
#os.chdir('C:/Users/Rafael.Ctt/Documents/PhD/XIPI/xipi-yuanban/scores')
#path='C:/Users/Rafael.Ctt/Documents/PhD/CONFERENCES/2017.10 ISMIR/Patterning'
#os.chdir(path)
from music21 import *
import pickle

#f = 'Pat-lsxpybs1.xml'
#graceNoteValue = 2.0
#subdivision = [2, 7]
#file2write = path + '/patternsPrueba.pkl'

def recodeWithOrnaments(filename, subdivision, file2write, graceNoteValue=2.0,
                        noteName='pitch'):
    '''str, [int], str --> [[[str, float, bol]]] in a pickle file
    It takes the filename of a aligned score in xml, as produced with the
    jingjuScores.py script, a list with the number of the last measure of the
    first and second line subvidision in the score, the name of the pickle file
    to be created and the duration value for each grace note. For each line,
    the notes are converted into lists with the name of the note, its duration
    in duration units (64th notes) and True or False if the note has lyrics,
    grouped into a list for each line, all lines grouped in a list which is
    dumped into a pickle file. It returns this list.
    If noteName = 'pitch', the name of the note is its pitch class plus octave
    (e.g. 'E4'), if noteName = 'midi', the name is its midi value (e.g. 64).
    '''

    # Check that the given noteName is valid:
    if noteName not in ['pitch', 'midi']:
        raise Exception('The given noteName is invalid')

    print('The duration unit is a 64th note')
    
    print('The duration value for grace notes is ' + str(graceNoteValue) + 
          ' duration units')
        
    # Parsing the file
    s = converter.parse(filename)
    
    print('Parsing ' + filename.split('/')[-1])
    
    subdivision.append(len(s.parts[0].getElementsByClass('Measure')))
    
    recodedScore = []
    
    for p in s.parts:
        notes = list(p.flat.notesAndRests)
        line = []
        section = 0
        graceNote = 0
        notePreGrace = None
        
        for i in range(len(notes)):
            n = notes[i]        
            # Line management
            if n.measureNumber > subdivision[section]:
                recodedScore.append(line)
                line = []
                section += 1
            # Check if n is note or rest    
            if n.isRest:
                name = n.name
                dur = n.quarterLength*16
                lyr = False
            else: # If it is a note:
                # Check if it is a grace note:
                if n.quarterLength == 0:
                    # Set name
                    if noteName == 'pitch':
                        name = n.nameWithOctave
                    elif noteName == 'midi':
                        name = n.pitch.midi
                    # Set duration
                    dur = graceNoteValue
                    # Accumulate grace note value to be subtracted
                    graceNote += graceNoteValue
                    if (notePreGrace == None) and (len(line) > 0):
                        notePreGrace = line.index(line[-1])
                    lyr = False
                else:
                # If it's not a grace note, then
                    # Set name
                    if noteName == 'pitch':
                        name = n.nameWithOctave
                    elif noteName == 'midi':
                        name = n.pitch.midi
                    # Set duration
                    # Check if there is some grace note value to be subtracted
                    if (notePreGrace != None) and not n.hasLyrics():
                    # Subtract grace note value from the previous note
                        lastNote = line[notePreGrace]
                        lastNoteDur = lastNote[1]
                        if lastNoteDur <= graceNote:
                            dur = (n.quarterLength*16) - graceNote
                        else:
#                            line.pop(notePreGrace)
#                            line.insert(notePreGrace, 
#                                        (lastNote[0], lastNote[1]-graceNote))
                            lastNote[1] += -graceNote
                            dur = (n.quarterLength*16)
                    else:
                    # Subtract grace note value, if any, from current note
                        dur = (n.quarterLength*16) - graceNote
                    # Set grace note counters to start
                    notePreGrace = None
                    graceNote = 0
                    #Check if it has a tie
                    if n.tie != None:
                        if n.tie.type == 'start':
                            dur += n.next().quarterLength*16
                        else: continue
                    # Set lyric
                    if n.hasLyrics():
                        # Check if the lyric is a padding syllable
                        if '（' in n.lyric:
                            lyr = False
                        else:
                            lyr = n.hasLyrics()
                    else:
                        lyr = n.hasLyrics()
            line.append([name, dur, lyr])
        recodedScore.append(line)
    
    # Check that all durations
    for i in range(len(recodedScore)):
        for note in recodedScore[i]:
            if note[1] == 0:
                raise Exception('A note with duration 0.0 in line', i)
            
    
    # Remove rests...
    for line in recodedScore:
        toPop = []
        i = 0                # ... from the beginning of each line...
        while line[i][0] == 'rest':
            toPop.append(i)
            i += 1
        i = -1               # ... and from the end of each line
        while line[i][0] == 'rest':
            toPop.append(len(line)+i)
            i += -1
        indexes = sorted(toPop, reverse=True)
        for i in indexes:
            line.pop(i)
    
    print('Found ' + str(len(recodedScore)) + ' lines')
    
    # Dump the list into a pickle file
    with open(file2write, 'wb') as f:
        pickle.dump(recodedScore, f, protocol=2)
        
    return recodedScore
        
def recodeWithoutOrnaments(filename,subdivision,file2write,noteName='pitch'):
    '''str, [int], str --> [[[str, float, bol]]] in a pickle file
    It takes the filename of a aligned score in xml, as produced with the
    jingjuScores.py script, a list with the number of the last measure of the
    first and second line subvidision in the score, and the name of the pickle
    file to be created. For each line, the notes are converted into lists with
    the name of the note, its duration in duration units (64th notes) and True
    or False if the note has lyrics, grouped into a list for each line, all
    lines grouped in a list which is dumped into a pickle file. It returns this
    list. Grace notes are not considered.
    If noteName = 'pitch', the name of the note is its pitch class plus octave
    (e.g. 'E4'), if noteName = 'midi', the name is its midi value (e.g. 64).
    '''

    # Check that the given noteName is valid:
    if noteName not in ['pitch', 'midi']:
        raise Exception('The given noteName is invalid')

    print('The duration unit is a 64th note')
        
    # Parsing the file
    s = converter.parse(filename)
    
    print('Parsing ' + filename.split('/')[-1])
    
    subdivision.append(len(s.parts[0].getElementsByClass('Measure')))
    
    recodedScore = []
    
    for p in s.parts:
        notes = list(p.flat.notesAndRests)
        line = []
        section = 0
        
        for i in range(len(notes)):
            n = notes[i]        
            # Line management
            if n.measureNumber > subdivision[section]:
                recodedScore.append(line)
                line = []
                section += 1
            # Check if n is note or rest    
            if n.isRest:
                name = n.name
                dur = n.quarterLength*16
                lyr = False
            else: # If it is a note:
                # Check if it is a grace note in order to ignore it
                if n.quarterLength == 0: continue
                else:
                # If it's not a grace note, then
                    # Set name
                    if noteName == 'pitch':
                        name = n.nameWithOctave
                    elif noteName == 'midi':
                        name = n.pitch.midi
                    # Set duration
                    dur = (n.quarterLength*16)
                    #Check if it has a tie
                    if n.tie != None:
                        if n.tie.type == 'start':
                            dur += n.next().quarterLength*16
                        else: continue
                    # Set lyric
                    if n.hasLyrics():
                        # Check if the lyric is a padding syllable
                        if '（' in n.lyric:
                            lyr = False
                        else:
                            lyr = n.hasLyrics()
                    else:
                        lyr = n.hasLyrics()
            line.append([name, dur, lyr])
        recodedScore.append(line)
    
    # Check that all durations
    for i in range(len(recodedScore)):
        for note in recodedScore[i]:
            if note[1] == 0:
                raise Exception('A note with duration 0.0 in line', i)
            
    
    # Remove rests...
    for line in recodedScore:
        toPop = []
        i = 0                # ... from the beginning of each line...
        while line[i][0] == 'rest':
            toPop.append(i)
            i += 1
        i = -1               # ... and from the end of each line
        while line[i][0] == 'rest':
            toPop.append(len(line)+i)
            i += -1
        indexes = sorted(toPop, reverse=True)
        for i in indexes:
            line.pop(i)
    
    print('Found ' + str(len(recodedScore)) + ' lines')
    
    # Dump the list into a pickle file
    with open(file2write, 'wb') as f:
        pickle.dump(recodedScore, f, protocol=2)
    
    return recodedScore