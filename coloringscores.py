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
colors = ['red', 'violet', 'blue']

with open(inPkl, 'rb') as f:
    recodedScore = pickle.load(f)

with open(outPkl, 'rb') as f:
    clusters = pickle.load(f)

toDisplay = [0]#range(len(clusters))

print('Loaded clusters:')
totalSequences = 0
for i in range(len(clusters)):
    sequences = len(clusters[i])    
    totalSequences += sequences
    print(str(i)+':', sequences)

print('There are', len(clusters), 'clusters and', totalSequences,
      'sequences in total')

for i in toDisplay:
    print('\nCluster number', i)
    s = converter.parse(original)
    sectionLimits = [0]
    sectionLimits.extend(subdivision)
    sectionLimits.append(len(s.parts[0].getElementsByClass('Measure')))
    # print(clusters[i])
    for sequence in clusters[i]:
        position = sequence[-1]
        partNum = int(position[0]/3)
        dou = position[0]%3
        seqNotes = sequence[:-1]
        print(seqNotes)
        print(partNum, dou, position, len(seqNotes))
        p = s.parts[partNum]
        section = p.measures(sectionLimits[dou]+1, sectionLimits[dou+1])
        scoreNotes = list(section.recurse().notesAndRests)
        # Skip the possible rests at the beginning of a section
        adjustment = 0
        while scoreNotes[adjustment].isRest:
            adjustment += 1
        """
        # Start from the index given in the outpost sequence
        adjustment += position[1]

        if not withOrnaments:
            toRemove = []
            for j in range(len(scoreNotes)):
                if scoreNotes[j].quarterLength == 0: toRemove.append(j)
            toRemove.sort(reverse=True)
            for r in toRemove:
                scoreNotes.pop(r)
            
            for j in range(len(seqNotes)):
                nombre = sequence[j][0]
                indice = j+adjustment
                nota = scoreNotes[indice]
                if nota.name in nombre:
                    if nota.color == None:
                        col = colors[0]                        
                        nota.color = col
                    else:
                        col = colors[colors.index(nota.color)+1]
                        nota.color = col
                if (nota.tie != None) and (nota.tie.type == 'start'):
                    adjustment += 1
                    scoreNotes[indice+1].color = col
                        
        if withOrnaments:
            raise Exception('No code for withOrnaments yet')
        """
    s.show()

####################################
###     OLD SEARCHING METHOD     ###
####################################

#colors = ['red', 'orange', 'green', 'blue', 'indigo', 'violet']
#
#if len(clusters) > len(colors):
#    print('There are', len(clusters)-len(colors), 'more clusters than colors')
#
#for c in range(len(clusters)):
#    foundPatterns = []
#    s = converter.parse(original)
#    # Patterns to search: p2s
#    col = 'red'
##    col = colors[c]
#    patterns2search = clusters[c]
#    for p2s in patterns2search:
#        for i in range(len(recodedScore)):
#            line = recodedScore[i]
#            for j in range(len(line)):
#                n = line[j]
#                if (n == p2s[0]) and (len(line)-j >= len(p2s)):
#                    # Pattern 2 check:
#                    p2c = []
#                    for k in range(len(p2s)):
#                        p2c.append(line[j+k])
#                    if p2c == p2s:
#                        p = int(i/3.0)
#                        section = i - (p*3)
#                        foundPatterns.append((p, section, j, len(p2s), col))
#
#    for pattern in foundPatterns:
#        p = s.parts[pattern[0]]
#        notes = list(p.recurse().notesAndRests)
#        col = pattern[-1]
#        # Remove ornaments if needed    
#        if not withOrnaments:
#            removeOrnaments = []
#            for i in range(len(notes)):
#                if notes[i].quarterLength == 0:
#                    removeOrnaments.append(i)
#            removeOrnaments = sorted(removeOrnaments, reverse=True)
#            for i in removeOrnaments:
#                notes.pop(i)
#                    
#        preIndex = 0
#        if pattern[1] == 0:
#            pos = 0
#            while notes[pos].name == 'rest':
#                pos += 1
#            preIndex += pos
#        elif pattern[1] == 1:
#            preNotes = p.measures(0, subdivision[0]).flat.notesAndRests
#            if not withOrnaments:
#                toSubtract = 0
#                for i in preNotes:
#                    if i.quarterLength == 0:
#                        toSubtract += 1
#                preIndex += len(preNotes) - toSubtract
#            else:
#                preIndex += len(preNotes)
#        elif pattern[1] == 2:
#            preNotes = p.measures(0, subdivision[1]).flat.notesAndRests
#            if not withOrnaments:
#                toSubtract = 0
#                for i in preNotes:
#                    if i.quarterLength == 0:
#                        toSubtract += 1
#                preIndex += len(preNotes) - toSubtract
#            else:
#                preIndex += len(preNotes)
#        # To solve ties
#        tiegap = 0
#    
#        # Coloring (accounting for ties)
#        for i in range(pattern[-2]):
#            loc = preIndex + pattern[2] + i + tiegap
#            n4c = notes[loc]
#            if (n4c.tie != None) and (n4c.tie.type == 'start'):
#                tiegap += 1
#                notes[loc+1].color = col
#            n4c.color = col
#    
#    s.show()