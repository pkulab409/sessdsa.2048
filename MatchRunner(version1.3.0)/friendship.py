# -*- coding: utf-8 -*-
"""
Created on Fri May 29 13:50:50 2020

@author: 田晨霄
"""
import sys
import os

import singlematchrunner as runner
import constants as c
import information as inf
import livequeues as live


def read_txt(input_dir):#
    im_names=[]
    ms=open(input_dir)
    for eachline in ms:
        eachline=eachline.strip('\n')
        eachline=str(eachline)
        line=eachline
        im_names.append(line)
    return im_names
s1=read_txt("F19results.txt")
s2=read_txt("N19results.txt")
NwinnerN19=s2[0]
secondN19=s2[1]
thirdN19=s2[2]
thirdsF191=s1[2]
thirdsF192=s1[3]
FwinnerF19=s1[0]
secondF19=s1[1]
def friendship(livequeue=None):
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
    
    print( """==========================================================================""")
    ####Friendship####
    s=input("Please input all final to start match all final : ")
    while s!= "all final":
        if s=="Break":
            sys.exit(0)
        s=input("Please input all final to start match all final : ")
    finalplayerlist=[NwinnerN19,FwinnerF19]
    path=mkdir('all final')
    winnerfinal=runner.main(finalplayerlist,path+"/"+" "+NwinnerN19[11:-3]+"vs"+" "+FwinnerF19[11:-3],live.queues[2],True,True,True,False,c.REPEAT,c.MAXTIME,c.ROUNDS)[3]
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
    print("""==============================================================================""")
    ###比赛冠亚季军汇报###
    s=input("是否输入命令汇报比赛冠亚季军结果 (Yes or No) : ")
    while s!="No":
        if s=="Yes":
            print("恭喜以下小组同学获得本次对抗2048比赛冠亚季军!")
            print("F19组季军: ")
            print(thirdsF191)
            print(thirdsF192)
            print("F19组亚军: ")
            print(secondF19)
            print("F19组冠军: ")
            print(inf.information[FwinnerF19[11:-3]])
            print("N19组季军: ")
            print(thirdN19)
            print("N19组亚军: ")
            print(secondN19)
            print("N19组冠军: ")
            print(inf.information[NwinnerN19[11:-3]])
            print("总冠军: ")
            print(inf.information[winnerfinal[11:-3]])
            break
        else:
            s=input("是否输入 Report 命令开始汇报比赛冠亚季军结果 (Yes or No,输入No结束比赛) : ")
    print("比赛结束!")

friendship(live.queues[2])
