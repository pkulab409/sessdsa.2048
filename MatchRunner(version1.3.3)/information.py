# -*- coding: utf-8 -*-
"""
Created on Fri May 29 00:31:46 2020

@author: 田晨霄
"""
F19=["F-Uniform","F-Echo","F-Zulu","F-Golf","F-November","F-Sierra","F-X-ray","F-3721","F-Bravo","F-007","F-666","F-Remeo"]
N19=["N-Sierra","N-X-ray","N-777","N-Bravo","N-666","N-404","N-8848","N-Remeo"]
information={}
for i in range(len(F19)):
    information["player"+str(i+1)]=F19[i]
for j in range(len(N19)):
    information["Player"+str(j+1)]=N19[j]
    
