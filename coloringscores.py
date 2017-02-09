# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:20:53 2017

@author: Rafael.Ctt
"""

from music21 import *
import pickle

inPkl = './sequences/pitchWithOut.pkl'
outPkl = './clusters/clusters_knn5_wo_ornament_normalized.pkl'
original = './scoreXML/Pat-lsxpybs1.xml'
subdivision = [2, 7]
withOrnaments = False


with open(inPkl, 'rb') as f:
    recodedScore = pickle.load(f)

with open(outPkl, 'rb') as f:
    patterns = pickle.load(f)

s = converter.parse(original)

# Starting index of the found patterns
foundPatterns = []

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

if len(patterns) > len(colors):
    print('There are', len(patterns) - len(colors), 'more patterns than colors')

for c in [1]:#range(len(patterns)):
    # Patterns to search: p2s
    col = 'red'
    patterns2search = patterns[c]
    for p2s in patterns2search:
        for i in range(len(recodedScore)):
            line = recodedScore[i]
            for j in range(len(line)):
                n = line[j]
                if (n == p2s[0]) and (len(line) - j >= len(p2s)):
                    # Pattern 2 check:
                    p2c = []
                    for k in range(len(p2s)):
                        p2c.append(line[j + k])
                    if p2c == p2s:
                        p = int(i / 3.0)
                        section = i - (p * 3)
                        foundPatterns.append((p, section, j, len(p2s), col))

for pattern in foundPatterns:
    p = s.parts[pattern[0]]
    notes = list(p.recurse().notesAndRests)
    col = pattern[-1]
    # Remove ornaments if needed
    if not withOrnaments:
        removeOrnaments = []
        for i in range(len(notes)):
            if notes[i].quarterLength == 0:
                removeOrnaments.append(i)
        removeOrnaments = sorted(removeOrnaments, reverse=True)
        for i in removeOrnaments:
            notes.pop(i)

    preIndex = 0
    if pattern[1] == 0:
        pos = 0
        while notes[pos].name == 'rest':
            pos += 1
        preIndex += pos
    elif pattern[1] == 1:
        preNotes = p.measures(0, subdivision[0]).flat.notesAndRests
        if not withOrnaments:
            toSubtract = 0
            for i in preNotes:
                if i.quarterLength == 0:
                    toSubtract += 1
            preIndex += len(preNotes) - toSubtract
        else:
            preIndex += len(preNotes)
    elif pattern[1] == 2:
        preNotes = p.measures(0, subdivision[1]).flat.notesAndRests
        if not withOrnaments:
            toSubtract = 0
            for i in preNotes:
                if i.quarterLength == 0:
                    toSubtract += 1
            preIndex += len(preNotes) - toSubtract
        else:
            preIndex += len(preNotes)
    # To solve ties
    tiegap = 0

    # Coloring (accounting for ties)
    for i in range(pattern[-2]):
        loc = preIndex + pattern[2] + i + tiegap
        n4c = notes[loc]
        if (n4c.tie != None) and (n4c.tie.type == 'start'):
            tiegap += 1
            notes[loc + 1].color = col
        n4c.color = col

s.show()