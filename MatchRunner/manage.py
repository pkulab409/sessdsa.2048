# -*- coding: utf-8 -*-
"""
Created on Fri May 29 02:02:10 2020

@author: 田晨霄
"""


import os
from random import shuffle
import random
import sys

import singlematchrunner as runner
import information as inf
"""==========================================================================="""
def mkdir(path):
    folder=os.path.exists(path)
    if folder==False:
        os.makedirs(path)
    else:
        path=path+"_"+"1"
        while os.path.exists(path)==True:
            path=path[0:-1]+str(int(path[-1])+1)
        os.makedirs(path)
    return path
fileList = os.listdir("F19players")
if fileList[-1]=="__pycache__":
    fileList.pop()
s=input("Please input F19 first to start match F19 first : ")
while s!= "F19 first":
    if s=="Break":
        sys.exit(0)
    s=input("Please input F19 first to start match F19 first : ")
"""============================================================================"""
####F19 first比赛####
players1=[]
players2=[]
players=[]
def f(string):
    if string[-1]==".":
        return string[0]
    else:
        return string
for i in range(len(fileList)):
    if int(f(fileList[i][6:8]))>4 and int(f(fileList[i][6:8]))<9:
        players1.append("F19players"+"/"+fileList[i])   
    elif (int(f(fileList[i][6:8]))>8 and int(f(fileList[i][6:8]))<13):
        players2.append("F19players"+"/"+fileList[i])
    else:
        players.append("F19players"+"/"+fileList[i])
seed=[0,1,2,3]
shuffle(seed)
players2=[players2[i] for i in seed]
allplayerlist1=[]
for i in range(4):
    everypair=[]
    everypair.append(players1[i])
    everypair.append(players2[i])
    allplayerlist1.append(everypair)
nextstage1=[]
path=mkdir('F19 first result')
for i in range(len(allplayerlist1)):    
    nextstage1.append(runner.main(allplayerlist1[i],savepath=path+"/"+allplayerlist1[i][0][11:-3]+" "+"vs"+" "+allplayerlist1[i][1][11:-3],toGet=True)[3])  
print(nextstage1)
f = open(path+'/'+"winners F19 first.txt", 'w')
f.write("F19 first winners:"+"\n")
for i in range(len(nextstage1)):
    f.write(nextstage1[i][11:-3]+"\n")
f.close()
s=input("是否显示出线小组详细信息 (Yes or No) : ")
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学出线!")
        for i in range(len(nextstage1)):
            print(inf.information[nextstage1[i][11:-3]])
        break
    else:
        s=input("是否显示出线小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""============================================================================"""
####F19 8 4####
s=input("Please input F19 8 4 to start match F19 8 4 : ")
while s!= "F19 8 4":
    if s=="Break":
        sys.exit(0)
    s=input("Please input F19 8 4 first to start match F19 8 4 : ")

allplayerlist2=[]    
seed=[0,1,2,3]
shuffle(seed)
players=[players[i] for i in seed] 
for i in range(4):
    everypair=[]
    everypair.append(players[i])
    everypair.append(nextstage1[i])
    allplayerlist2.append(everypair)
nextstage2=[]
path=mkdir('F19 8 4')
for i in range(len(allplayerlist2)):    
    nextstage2.append(runner.main(allplayerlist2[i],savepath=path+"/"+allplayerlist2[i][0][11:-3]+" "+"vs"+" "+allplayerlist2[i][1][11:-3],toGet=True)[3])  
print(nextstage2) 
f = open(path+'/'+"winners F19 8 4.txt", 'w')
f.write("F19 8 4 winners:"+"\n")
for i in range(len(nextstage2)):
    f.write(nextstage2[i][11:-3]+"\n")
f.close()
s=input("是否显示出线小组详细信息 (Yes or No) : ")
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学出线!")
        for i in range(len(nextstage2)):
            print(inf.information[nextstage2[i][11:-3]])
        break
    else:
        s=input("是否显示出线小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""==========================================================================="""
####F19 4 2 ####
s=input("Please input F19 4 2 to start match F19 4 2 : ")
while s!= "F19 4 2":
    if s=="Break":
        sys.exit(0)
    s=input("Please input F19 4 2 first to start match F19 4 2 : ")

allplayerlist3=[] 
a=random.randint(0,1) 
b=random.randint(2,3)  
players1=[nextstage2[a],nextstage2[b]]
players2=[nextstage2[1-a],nextstage2[5-b]]
for i in range(2):
    everypair=[]
    everypair.append(players1[i])
    everypair.append(players2[i])
    allplayerlist3.append(everypair)
nextstage3=[]
path=mkdir('F19 4 2')
for i in range(len(allplayerlist3)):    
    nextstage3.append(runner.main(allplayerlist3[i],savepath=path+"/"+allplayerlist3[i][0][11:-3]+" "+"vs"+" "+allplayerlist3[i][1][11:-3],toGet=True)[3])  
print(nextstage3)  
f = open(path+'/'+"winners F19 4 2.txt", 'w')
f.write("F19 4 2 winners:"+"\n")
for i in range(len(nextstage3)):
    f.write(nextstage3[i][11:-3]+"\n")
f.close()
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学出线!")
        for i in range(len(nextstage3)):
            print(inf.information[nextstage3[i][11:-3]])
        break
    else:
        s=input("是否显示出线小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""========================================================================="""
####F19 final####
s=input("Please input F19 final to start match F19 final : ")
while s!= "F19 final":
    if s=="Break":
        sys.exit(0)
    s=input("Please input F19 final first to start match F19 final : ")
path=mkdir('F19 final')
winnerF19=runner.main(nextstage3,savepath=path+"/"+nextstage3[0][11:-3]+" "+"vs"+" "+nextstage3[1][11:-3],toGet=True)[3]
print(winnerF19) 
f = open(path+'/'+"winners F19 final.txt", 'w')
f.write("F19 final winners:"+"\n")
f.write(winnerF19)
f.close()   
while s!="No":
    if s=="Yes":
        print("恭喜以下小组为F19组冠军!")
        print(inf.information[winnerF19[11:-3]])
        break
    else:
        s=input("是否显示F19冠军小组详细信息 (Yes or No,输入No开始N19组比赛) : ") 
"""=========================================================================="""
####N19 比赛####          
fileList = os.listdir("N19players")
if fileList[-1]=="__pycache__":
    fileList.pop()
####N19 8 4####
s=input("Please input N19 8 4 to start match N19 8 4 : ")
while s!= "N19 8 4":
    if s=="Break":
        sys.exit(0)
    s=input("Please input N19 8 4 first to start match N19 8 4 : ")
players1=[]
players2=[]
for i in range(len(fileList)):
    if int(fileList[i][6])>4 and int(fileList[i][6])<9:
        players2.append("N19players"+"/"+fileList[i])   
    else:
        players1.append("N19players"+"/"+fileList[i])
seed=[0,1,2,3]
shuffle(seed)
players1=[players1[i] for i in seed] 
allplayerlistN1=[]
for i in range(4):
    everypair=[]
    everypair.append(players1[i])
    everypair.append(players2[i])
    allplayerlistN1.append(everypair)
nextstageN1=[]
path=mkdir('N19 8 4')
for i in range(len(allplayerlistN1)):    
    nextstageN1.append(runner.main(allplayerlistN1[i],savepath=path+"/"+allplayerlistN1[i][0][11:-3]+" "+"vs"+" "+allplayerlistN1[i][1][11:-3],toGet=True)[3])  
print(nextstageN1)
f=open(path+"/"+"winners N19 8 4 .txt", 'w')
f.write("N19 8 4 winners:"+"\n")
for i in range(len(nextstageN1)):
    f.write(nextstageN1[i][11:-3]+"\n")
f.close()
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学出线!")
        for i in range(len(nextstageN1)):
            print(inf.information[nextstageN1[i][11:-3]])
        break
    else:
        s=input("是否显示出线小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""=========================================================================="""
####N19 4 2 ####
s=input("Please input N19 4 2 to start match N19 4 2 : ")
while s!= "N19 4 2":
    if s=="Break":
        sys.exit(0)
    s=input("Please input N19 4 2 first to start match N19 4 2 : ")

allplayerlistN2=[] 
a=random.randint(0,1) 
b=random.randint(2,3)  
players1=[nextstageN1[a],nextstageN1[b]]
players2=[nextstageN1[1-a],nextstageN1[5-b]]
for i in range(2):
    everypair=[]
    everypair.append(players1[i])
    everypair.append(players2[i])
    allplayerlistN2.append(everypair)
nextstageN3=[]
path=mkdir('N19 4 2')
for i in range(len(allplayerlistN2)):    
    nextstageN3.append(runner.main(allplayerlistN2[i],savepath=path+"/"+allplayerlistN2[i][0][11:-3]+" "+"vs"+" "+allplayerlistN2[i][1][11:-3],toGet=True)[3])  
print(nextstageN3) 
third=[]
for i in range(len(nextstageN1)):
    if nextstageN1[i] not in nextstageN3:
        third.append(nextstageN1[i])
f = open(path+'/'+"winners N19 4 2.txt", 'w')
f.write("N19 4 2 winners:"+"\n")
for i in range(len(nextstageN3)):
    f.write(nextstageN3[i][11:-3]+"\n")
f.close()
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学出线!")
        for i in range(len(nextstageN3)):
            print(inf.information[nextstageN3[i][11:-3]])
        break
    else:
        s=input("是否显示出线小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""=========================================================================="""
###N19季军###
s=input("Please input N19 third to start match N19 third : ")
while s!= "N19 third":
    if s=="Break":
        sys.exit(0)
    s=input("Please input N19 third to start match N19 third : ") 
path=mkdir('N19 third')
third=runner.main(third,savepath=path+"/"+third[0][11:-3]+" "+"vs"+" "+third[1][11:-3],toGet=True)[3]
print(third) 
f = open(path+'/'+"third N19 final.txt", 'w')
f.write("N19 third:"+"\n")
f.write(third)
f.close()
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学获得N19组季军!")
        print(inf.information[third[11:-3]])
        break
    else:
        s=input("是否显示N19组季军小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""========================================================================---"""        
####N19 final####
s=input("Please input N19 final to start match N19 final : ")
while s!= "N19 final":
    if s=="Break":
        sys.exit(0)
    s=input("Please input N19 final to start match N19 final : ") 
path=mkdir('N19 final')
winnerN19=runner.main(nextstageN3,savepath=path+"/"+nextstageN3[0][11:-3]+" "+"vs"+" "+nextstageN3[1][11:-3],toGet=True)[3]
print(winnerN19) 
f = open(path+'/'+"winners N19 final.txt", 'w')
f.write("N19 final winners:"+"\n")
f.write(winnerN19)
f.close()
second=[]
for i in range(len(nextstageN3)):
    if nextstageN3[i]!=winnerN19:
        second.append(nextstageN3[i])
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学获得N19组冠军!")
        print(inf.information[winnerN19[11:-3]])
        break
    else:
        s=input("是否显示N19组冠军小组详细信息 (Yes or No,输入No开始下一场比赛) : ")
"""=========================================================================="""
####Friendship####
finalplayerlist=[winnerN19,winnerF19]
s=input("Please input all final to start match all final : ")
while s!= "all final":
    if s=="Break":
        sys.exit(0)
    s=input("Please input all final to start match all final : ")
path=mkdir('all final')
winnerfinal=runner.main(finalplayerlist,savepath=path+"/"+" "+winnerN19[11:-3]+"vs"+" "+winnerF19[11:-3],toGet=True)[3]
print(winnerfinal)
f = open(path+'/'+"all final.txt", 'w')
f.write("all final winners:"+"\n")
f.write(winnerfinal)
f.close()
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学获得本次对抗2048比赛总冠军!")
        print(inf.information[winnerfinal[11:-3]])
        break
    else:
        s=input("是否显示总冠军小组详细信息 (Yes or No,输入No进入颁奖) : ")
"""=============================================================================="""
###比赛冠亚季军汇报###
s=input("是否输入命令汇报比赛冠亚季军结果 (Yes or No) : ")
while s!="No":
    if s=="Yes":
        print("恭喜以下小组同学获得本次对抗2048比赛冠亚季军!")
        print("F19组季军: ")
        for i in range(len(nextstage2)):
            if nextstage2[i] not in nextstage3:
                print(inf.information[nextstage2[i][11:-3]])
        print("F19组亚军: ")
        for i in range(len(nextstage3)):
            if nextstage3[i]!=winnerF19:
                print(inf.information[nextstage3[i][11:-3]])
        print("F19组冠军: ")
        print(inf.information[winnerF19[11:-3]])
        print("N19组季军: ")
        print(inf.information[third[11:-3]])
        print("N19组亚军: ")
        print(inf.information[second[0][11:-3]])
        print("N19组冠军: ")
        print(inf.information[winnerN19[11:-3]])
        print("总冠军: ")
        print(inf.information[winnerfinal[11:-3]])
        break
    else:
        s=input("是否输入 Report 命令开始汇报比赛冠亚季军结果 (Yes or No,输入No结束比赛) : ")
print("比赛结束!")