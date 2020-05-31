# -*- coding: utf-8 -*-
"""
Created on Fri May 29 11:18:32 2020

@author: 田晨霄
"""


import os
from random import shuffle
import random
import sys
from multiprocessing import Pool 
from pyfiglet import Figlet



import singlematchrunner as runner
import information as inf
import constants as c
import livequeues as live

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
####################
def newmain(args):
        return runner.main(*args)[3]
def F19(livequeue=None,finallivequeue=None):
    print("""===================================F19组比赛===================================""")
    fileList = os.listdir("F19players")
    if "__pycache__" in fileList:
        fileList.remove("__pycache__")
    ####F19 first比赛####
    f = Figlet()
    print(f.renderText("             2 0 4 8     F19"))
    print("""===================================F19 第一场===================================""")
    s=input("Please input 1 to start match F19 first : ")
    while s!= "1":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 1 to start match F19 first : ")
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
    pool = Pool() 
    nextstage1=pool.map(newmain,[(allplayerlist1[i],path+"/"+inf.information[allplayerlist1[i][0][11:-3]]+" "+"vs"+" "+inf.information[allplayerlist1[i][1][11:-3]],livequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS) for i in range(len(allplayerlist1))])  
    pool.close()
    pool.join()
    #print(nextstage1)
    f = open(path+'/'+"winners F19 first.txt", 'w')
    f.write("F19 first winners:"+"\n")
    for i in range(len(nextstage1)):
        f.write(inf.information[nextstage1[i][11:-3]]+"\n")
    f.close()
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    print("""================================================================================""")
    f = Figlet()
    print(f.renderText("Congratulations"))
    print("""===================================F19 第一场结果===================================""")
    while s!="N":
        if s=="Y":
            print("                                恭喜以下小组同学出线!                                  ")
            for i in range(len(nextstage1)):
                print("                                "+inf.information[nextstage1[i][11:-3]]+"                  ")
            break
        else:
            s=input("是否显示出线小组详细信息 (Y or N,输入N开始下一场比赛) : ")
    print("""==================================F19 8进4======================================""")
    ####F19 8 4####
    s=input("Please input 2 to start match F19 8 4 : ")
    while s!= "2":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 2 first to start match F19 8 4 : ")
    
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
    pool = Pool() 
    nextstage2=pool.map(newmain,[(allplayerlist2[i],path+"/"+inf.information[allplayerlist1[i][0][11:-3]]+" "+"vs"+" "+inf.information[allplayerlist2[i][1][11:-3]],livequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS) for i in range(len(allplayerlist2))])  
    pool.close()
    pool.join() 
    #print(nextstage2) 
    f = open(path+'/'+"winners F19 8 4.txt", 'w')
    f.write("F19 8 4 winners:"+"\n")
    for i in range(len(nextstage2)):
        f.write(inf.information[nextstage2[i][11:-3]]+"\n")
    f.close()
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    f = Figlet()
    print("""================================================================================""")
    print(f.renderText("Congratulations"))
    print("""===================================F19 8进4结果===================================""")
    while s!="N":
        if s=="Y":
            print("                       恭喜以下小组同学出线!                                   ")
            for i in range(len(nextstage2)):
                print("                         "+inf.information[nextstage2[i][11:-3]]+"                ")
            break
        else:
            s=input("是否显示出线小组详细信息 (Y or N,输入N开始下一场比赛) : ")
    print("""=================================F19 4进2=====================================""")
    ####F19 4 2 ####
    s=input("Please input 3 to start match F19 4 2 : ")
    while s!= "3":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 3 to start match F19 4 2 : ")
    
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
    pool = Pool() 
    nextstage3=pool.map(newmain,[(allplayerlist3[i],path+"/"+inf.information[allplayerlist3[i][0][11:-3]]+" "+"vs"+" "+inf.information[allplayerlist2[i][1][11:-3]],livequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS) for i in range(len(allplayerlist3))])  
    pool.close()
    pool.join() 
    #print(nextstage3)  
    f = open(path+'/'+"winners F19 4 2.txt", 'w')
    f.write("F19 4 2 winners:"+"\n")
    for i in range(len(nextstage3)):
        f.write(inf.information[nextstage3[i][11:-3]]+"\n")
    f.close()
    s=input("是否显示出线小组详细信息 (Y or N) :" )
    print("""================================================================================""")
    f = Figlet()
    print(f.renderText("Congratulations"))
    print("""===================================F19 4进2结果===================================""")
    while s!="N":
        if s=="Y":
            print("                           恭喜以下小组同学出线!                               ")
            for i in range(len(nextstage3)):
                print("                          "+inf.information[nextstage3[i][11:-3]]+"                ")
            break
        else:
            s=input("是否显示出线小组详细信息 (Y or N,输入N开始下一场比赛) : ")
    print("""===============================F19 决赛======================================""")
    ####记录季军####
    allthirds=[]
    for i in range(len(nextstage2)):
                if nextstage2[i] not in nextstage3:
                    allthirds.append(inf.information[nextstage2[i][11:-3]])
    ####F19 final####
    s=input("Please input 4 to start match F19 final : ")
    while s!= "4":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 4 to start match F19 final : ")
    path=mkdir('F19 final')
    winnerF19=runner.main(nextstage3,path+"/"+inf.information[nextstage3[0][11:-3]]+" "+"vs"+" "+inf.information[nextstage3[1][11:-3]],finallivequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS)[3]
    F19=winnerF19
    #print(winnerF19) 
    f = open(path+'/'+"winners F19 final.txt", 'w')
    f.write("F19 final winners:"+"\n")
    f.write(inf.information[winnerF19[11:-3]])
    f.close()  
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    print("""================================================================================""")
    f = Figlet()
    print(f.renderText("Congratulations   "))
    print("""===================================F19 决赛结果===================================""")
    while s!="N":
        if s=="Y":
            print("                        恭喜以下小组为F19组冠军!                               ")
            print("                             "+inf.information[winnerF19[11:-3]]+"                      ")
            break
        else:
            s=input("是否显示F19冠军小组详细信息 (Y or N,输入N结束F19组比赛) : ") 
    print("""=============================================================================""")
    ###记录亚军###
    second=[]
    for i in range(len(nextstage3)):
                if nextstage3[i]!=winnerF19:
                    second.append(inf.information[nextstage3[i][11:-3]])
    return [F19,second,allthirds]
if __name__ == '__main__':
    s=F19(None,live.queues[0])
    with open("F19results.txt","w") as f:
        f.write(s[0]+"\n")
        f.write(s[1][0]+"\n")
        f.write(s[2][0]+"\n")
        f.write(s[2][1]+"\n")
        f.close()  
        
