# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:21:38 2020

@author: etale
"""

from itertools import permutations
from collections import Counter
import sys
import re

def ReadCmd():
    l=[0,2,0,0]
    for x in sys.argv[1:]:
        #-r=rangetype
        if bool(re.fullmatch(r"-r=[01]",x)):
            l[0]=int(x[3])            
        #-d=difficulty
        if bool(re.fullmatch(r"-d=[012]",x)):
            l[1]=int(x[3])
        #-inf = infinity y/n
        if bool(re.fullmatch(r"-inf",x)):
            l[2]=1
        #-cm=cold mastery lvl
        if bool(re.fullmatch(r"-cm=\d+",x)):
            l[3]=int(x[4:])
    return l

#Resistances - 0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison
#Resists=[50,100,0,0,0,75] #Plague Bearer (Hell)

def lowerCap(Res):
    """
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]

    Returns
    -------
    Applies the lower cap of -100 to the Resistance Array.

    """
    a=Res[:]
    for i in range(0,6):
        a[i]=max(-100,a[i])
    return a

def Infinity(Res):
    """
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]

    Returns
    -------
    Resistances after the application of lvl 12 Conviction Aura.
    """
    a=Res[:]
    for i in range(2,5):
        if a[i]<100:
            a[i]-=85
        else:
            a[i]-=17
    return lowerCap(a)

def ColdMastery(Res,CM):
    """
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]
    CM: Cold Mastery lvl
    Returns
    -------
    Resistances after the application of lvl CM Coldmastery
    """
    a=Res[:]
    if a[2]<100:
        ECR=15+5*CM if CM else 0
        a[2]-=ECR
    return lowerCap(a)

def Immunities(Res):
    """
    Parameters:
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]
    
    Returns
    -------
    Number of immunities in the Resistance Array.
    """
    return sum(1 for x in Res if 100<=x)

def ResPlus(Res,ResType,ResBonus):
    """
    Applies ResBonus to Res[ResType] if this does not result in a third
    immunity or increases one of two or more Immunities.    

    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]
    ResType: Resistance Type
    ResBonus: Resistance Bonus

    Returns
    -------
    Resistance Array after ResBonus is (potentially) applied.
    """
    a=Res[:]
    if a[ResType]<100-ResBonus:
        a[ResType]+=ResBonus
        return a
    else:
        if 2<=Immunities(a):
            return a
        else:
            a[ResType]+=ResBonus
            return a

def MagicResistant(Res):
    """
    Applies +40 to Cold, Fire and Lightning Resistance in this order, but only
    if the respective resistance is less than 100 and this would not result in
    a third immunity or increase one of two or more immunities.
    
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]

    Returns
    -------
    Resistance Array after Magic Resistant is applied.
    """
    a=Res[:]
    for i in range(2,5):
        if a[i]<100:
            a=ResPlus(a,i,40)
    return a

def SpectralHit(Res):
    """
    Applies +20 to Cold, Fire and Lightning Resistance in this order, but only
    if the respective resistance is less than 75. Since 74+20 is less than 100
    there is no need to check for possible immunities.
    
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]

    Returns
    -------
    Resistance Array after Spectral Hit is applied.
    """
    a=Res[:]
    for i in range(2,5):
        if a[i]<75:
            a[i]+=20
    return a


#"Mod": (ResType, ResBonus)
mod_dict={"": (0,0),"SS": (0,50),"MB": (1,20),
          "CE": (2,75),"FE": (3,75),"LE": (4,75)}
def ChangeRes(Res,Mod):
    """
    Applies the resistance bonus of "Mod" to resistances. Key:
        SS - Stone Skin             +50 to physical resistance
        MB - Mana Burn              +20 to magic resistance
        CE - Cold Enchangted        +75 to cold resistance
        FE - Fire Enchanted         +75 to fire resistance
        LE - Lightning Enchanted    +75 to lightning resistance
        SH - Spectral Hit           +20 to cold, fire and lightning resistance
                                    if respective resistance is less than 75
        MR - Magic Resistant        +40 to cold, fire and lightning resistance
                                    if respective resistance is less than 100
                                    and this does not result in a third immunity
                                    or increase one of two immunities
           - else                   +0 to physical resistance (technicality)
    
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]
    Mod: Identifier of the Modifier applied

    Returns
    -------
    Resistance Array after the (potential) bonuses of "Mod" have been applied.
    """
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

def ResistList(Res,rangedtype,difficulty,inf,CM):
    """
    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]
    rangedtype: 0=Melee, 1=Ranged
    difficulty: 0=Normal, 1=Nightmare, 2=Hell
    inf: 0=no Conviction, 1=lvl 12 Conviction
    CM: Cold Mastery lvl. Adds -(15+5*CM) to cold resistance if not immune
    
    Magic Resistant may not spawn in Normal difficulty and Multiple Shot only
    spawns for monsters that have rangetype set to 1.
    
    Returns
    -------
    One Counter object for each resistance. Each counter has the possible
    resistances as keys and the number of their occurence in all the possible
    modifier permutations as values.
    """
    Mods=[""]*(5+rangedtype)+["FE","CE","LE","SS","SH","MB"]+["MR"]*(difficulty!=0)
    l=[]
    for i in permutations(Mods,difficulty+1):
        x=Res
        for j in range(0,difficulty+1):
            x=ChangeRes(x,i[j])
        if inf:
            x=Infinity(x)
        if CM:
            x=ColdMastery(x,CM)
        l.append(x)
    r=tuple(zip(*l))
    return [Counter(r[i]) for i in range(0,6)]

def PercentageList(Res,ResType,rangedtype,difficulty,inf,CM):
    '''
    Returns a list of possible resistances and their probability for the given
    rangedtype, difficulty and ResType

    Parameters
    ----------
    Res: Resistance Array [0 Phys, 1 Mag, 2 Cold, 3 Fire, 4 Light, 5 Poison]
    ResType: Resistance Type
    rangedtype: 0=Melee, 1=Ranged
    difficulty: 0=Normal, 1=Nightmare, 2=Hell
    inf: 0=no Conviction, 1=lvl 12 Conviction
    CM: Cold Mastery lvl. Adds -(15+5*CM) to cold resistance if CM and not immune

    Returns
    -------
    None
    '''
    def pCounter(d):
        t=sum(d.values())
        for i in d.keys():
            d[i]="{:.2%}".format(d[i]/t)
        return d
    d=sorted(pCounter(ResistList(Res,rangedtype,difficulty,inf,CM)[ResType]).items())
    print(res_dict[ResType]+":")
    for a in d:
        print("{}: {}".format(a[0],a[1]))

#sys.argv.append("-cm=27")
l=ReadCmd()
Resists=[int(x) for x in input("Enter Resistances: ").split(" ")]
for i in range(0,6):
    print("")
    PercentageList(Resists,i,l[0],l[1],l[2],l[3])