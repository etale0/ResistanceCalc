# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:21:38 2020

@author: etale
"""

from itertools import permutations
from collections import Counter

#Resistances - 0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison
Resists=[50,100,0,0,0,75] #Plague Bearer (Hell)

def Immunities(Res):
    return sum(1 for x in Res if 100<=x)

def ResPlus(Res,ResType,ResBonus):
    if Res[ResType]<100-ResBonus:
        Res[ResType]+=ResBonus
        return Res
    else:
        if 2<=Immunities(Res):
            return Res
        else:
            Res[ResType]+=ResBonus
            return Res

def MagicResistant(Res):
    for i in range(2,5):
        if Res[i]<100:
            Res=ResPlus(Res,i,40)
    return Res

def SpectralHit(Res):
    for i in range(2,5):
        if Res[i]<75:
            Res[i]+=20
    return Res

#"Mod": (ResType, ResBonus)
mod_dict={"": (0,0),"SS": (0,50),"MB": (1,20),
          "CE": (2,75),"FE": (3,75),"LE": (4,75)}
def ChangeRes(Res,Mod):
    a=Res[:]
    if Mod=="MR":
        return MagicResistant(a)
    elif Mod=="SH":
        return SpectralHit(a)
    elif Mod=="":
        return a
    else:
        return ResPlus(a,mod_dict[Mod][0],mod_dict[Mod][1])

res_dict={0:"Physical",1:"Magic",2:"Cold",3:"Fire",4:"Lightning",5:"Poison"}
#rangedtype: 0 Melee, 1 Ranged
#Difficulty: 0 Normal, 1 Nightmare, 2 Hell
def ResistList(Res,rangedtype,difficulty):
    Mods=[""]*(5+rangedtype)+["FE","CE","LE","SS","SH","MB"]+["MR"]*(difficulty!=0)
    l=[]
    for i in permutations(Mods,difficulty+1):
        x=Res
        for j in range(0,difficulty+1):
            x=ChangeRes(x,i[j])
        l.append(x)
    r=tuple(zip(*l))
    def pCounter(d):
        t=sum(d.values())
        for i in d.keys():
            d[i]="{:.2%}".format(d[i]/t)
        return d
    for i in range(0,5):
        d=sorted(pCounter(Counter(r[i])).items())
        print(res_dict[i]+":")
        for a in d:
            print("{}: {}".format(a[0],a[1]))

ResistList(Resists,0,2)