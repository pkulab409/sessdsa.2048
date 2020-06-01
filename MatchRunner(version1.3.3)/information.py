# -*- coding: utf-8 -*-
"""
Created on Fri May 29 00:31:46 2020

@author: 田晨霄
"""
F19=["Uniform","Echo","Zulu","Golf","November","Sierra","X-ray","3721","Bravo","007","666","Remeo"]
N19=["Sierra"," X-ray","777"," Bravo"," 666","404","8848"," Remeo"]
information={}
for i in range(len(F19)):
    information["player"+str(i+1)]=F19[i]
for j in range(len(N19)):
    information["Player"+str(j+1)]=N19[j]
    
