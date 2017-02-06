# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 16:10:29 2017

@author: Rafael.Ctt
"""

import os
import pickle
from music21 import *

filename1 = 'clusters_knn0_w_ornament_normalized.pkl'
filename2 = 'clusters_knn5_w_ornament_normalized.pkl'
filename3 = 'clusters_weighted_w_ornament_normalized.pkl'
filename4 = 'clusters_knn0_wo_ornament_normalized.pkl'
filename5 = 'clusters_weighted_wo_ornament_normalized.pkl'
filename6 = 'clusters_knn5_wo_ornament_normalized.pkl'

patterns = pickle.load(open(filename6, 'rb'))

cluster = patterns[1]

s = stream.Score()

for pattern in cluster:
    line = stream.Stream()
    for nota in pattern:
        n = note.Note(nota[0])
        n.quarterLength = (nota[1] / 16.0)
        line.append(n)
    line.insert(0, key.KeySignature(4))
    s.insert(0, line)

s.makeNotation(inPlace=True)

s.show()
        