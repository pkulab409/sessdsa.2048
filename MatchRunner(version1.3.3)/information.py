# -*- coding: utf-8 -*-
"""
Created on Fri May 29 00:31:46 2020

@author: 田晨霄
"""
F19=["Tom","Jerry","SpongeBob","Cat","Sheep","Jack","Beta","Alice","Cortal","David","Eve","France"]
N19=["Apple","Banana","Pieapple","Applepen","Rick","Morty","Misaka","Mikoto","Powerpoint","Spyder","Python"]
information={}
for i in range(len(F19)):
    information["player"+str(i+1)]=F19[i]
for j in range(len(N19)):
    information["Player"+str(j+1)]=N19[j]
    
