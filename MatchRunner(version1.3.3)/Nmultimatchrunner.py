# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:30:29 2020

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
def newmain(args):
     return runner.main(*args)[3]
def N19(livequeue=None,finallivequeue=None):
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
    #####################
    print("""=================================N19 比赛======================================""")
    f = Figlet()
    print(f.renderText("             2 0 4 8     N19"))
    print("""===================================N19 第一场==================================""")
    ####N19 比赛####          
    fileList = os.listdir("N19players")
    if fileList[-1]=="__pycache__":
        fileList.pop()
    ####N19 8 4####
    s=input("Please input 1 to start match N19 8 4 : ")
    while s!= "1":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 1  to start match N19 8 4 : ")
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
    pool = Pool() 
    nextstageN1=pool.map(newmain,[(allplayerlistN1[i],path+"/"+allplayerlistN1[i][0][11:-3]+" "+"vs"+" "+allplayerlistN1[i][1][11:-3],livequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS) for i in range(len(allplayerlistN1))])  
    pool.close()
    pool.join()
    #print(nextstageN1)
    f=open(path+"/"+"winners N19 8 4 .txt", 'w')
    f.write("N19 8 4 winners:"+"\n")
    for i in range(len(nextstageN1)):
        f.write(nextstageN1[i][11:-3]+"\n")
    f.close()
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    f= Figlet()
    print("""==================================================================================""")
    print(f.renderText("Congratulations"))
    print("""===================================N19 第一场结果==================================""")
    
    while s!="N":
        if s=="Y":
            print("                           恭喜以下小组同学出线!                               ")
            for i in range(len(nextstageN1)):
                print("              "+inf.information[nextstageN1[i][11:-3]]+"                  ")
            break
        else:
            s=input("是否显示出线小组详细信息 (Y or N,输入N开始下一场比赛) : ")
    print("""================================N19 4进2==========================================""")
    ####N19 4 2 ####
    s=input("Please input 2 to start match N19 4 2 : ")
    while s!= "2":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 2 first to start match N19 4 2 : ")
    
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
    pool = Pool() 
    nextstageN3=pool.map(newmain,[(allplayerlistN2[i],path+"/"+allplayerlistN2[i][0][11:-3]+" "+"vs"+" "+allplayerlistN2[i][1][11:-3],livequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS) for i in range(len(allplayerlistN2))])  
    pool.close()
    pool.join()
   #print(nextstageN3) 
    third=[]
    for i in range(len(nextstageN1)):
        if nextstageN1[i] not in nextstageN3:
            third.append(nextstageN1[i])
    f = open(path+'/'+"winners N19 4 2.txt", 'w')
    f.write("N19 4 2 winners:"+"\n")
    for i in range(len(nextstageN3)):
        f.write(nextstageN3[i][11:-3]+"\n")
    f.close()
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    f= Figlet()
    print("""================================================================================""")
    print(f.renderText("Congratulations"))
    print("""===================================N19 4进2结果==================================""")
    while s!="N":
        if s=="Y":
            print("                         恭喜以下小组同学出线!                               ")
            for i in range(len(nextstageN3)):
                print("                 "+inf.information[nextstageN3[i][11:-3]]+"             ")
            break
        else:
            s=input("是否显示出线小组详细信息 (Y or N,输入N开始下一场比赛) : ")
    print("""===================================N19 季军====================================""")
    ###N19季军###
    s=input("Please input 3 to start match N19 third : ")
    while s!= "3":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 3 to start match N19 third : ") 
    path=mkdir('N19 third')
    third=runner.main(third,savepath=path+"/"+third[0][11:-3]+" "+"vs"+" "+third[1][11:-3],toGet=True)[3]
    #print(third) 
    f = open(path+'/'+"third N19 final.txt", 'w')
    f.write("N19 third:"+"\n")
    f.write(third)
    f.close()
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    f= Figlet()
    print("""================================================================================""")
    print(f.renderText("Congratulations"))
    print("""===================================N19 季军结果==================================""")
    while s!="N":
        if s=="Y":
            print("                      恭喜以下小组同学获得N19组季军!                           ")
            print("                      "+inf.information[third[11:-3]]+"                       ")
            break
        else:
            s=input("是否显示N19组季军小组详细信息 (Y or N,输入N开始下一场比赛) : ")
    print("""==================================N19 决赛======================================""")        
    ####N19 final####
    s=input("Please input 4 to start match N19 final : ")
    while s!= "4":
        if s=="Break":
            sys.exit(0)
        s=input("Please input 4 to start match N19 final : ") 
    path=mkdir('N19 final')
    winnerN19=runner.main(nextstageN3,path+"/"+nextstageN3[0][11:-3]+" "+"vs"+" "+nextstageN3[1][11:-3],finallivequeue,True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS)[3]
    N19=winnerN19
    #print(winnerN19) 
    f = open(path+'/'+"winners N19 final.txt", 'w')
    f.write("N19 final winners:"+"\n")
    f.write(winnerN19)
    f.close()
    second=[]
    for i in range(len(nextstageN3)):
        if nextstageN3[i]!=winnerN19:
            second.append(nextstageN3[i])
    s=input("是否显示出线小组详细信息 (Y or N) : ")
    f= Figlet()
    print("""================================================================================""")
    print(f.renderText("Congratulations"))
    print("""===================================N19 决赛结果==================================""")
    while s!="N":
        if s=="Y":
            print("                       恭喜以下小组同学获得N19组冠军!                         ")
            print("                          "+inf.information[winnerN19[11:-3]]+"                      ")
            break
        else:
            s=input("是否显示N19组冠军小组详细信息 (Y or N,输入N结束当N19组比赛) : ")
    print("""================================================================================""")
    return [N19,inf.information[second[0][11:-3]],inf.information[third[11:-3]]]
if __name__ == '__main__':
    s=N19(None,live.queues[1])  
    with open("N19results.txt","w") as f:
        f.write(s[0]+"\n")
        f.write(s[1]+"\n")
        f.write(s[2]+"\n")
        f.close() 
        
