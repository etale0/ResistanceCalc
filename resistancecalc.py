# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:21:38 2020

@author: etale
"""

from itertools import permutations
from collections import Counter
import sys
import re

sys.argv.extend(["-conv=12", "-r=1"])

diff_dic = {0: "Normal", 1: "Nightmare", 2: "Hell"}

res_dic = {0: "Physical", 1:"Magic", 2: "Cold", 
            3: "Fire", 4: "Lightning", 5: "Poison"}

class Parameters:
    def __init__(self, parms):
        """
        Initializes the parameter vector which contains the switches/values
        for conviction, lower resist, cold mastery, -% enemy resist, ranged
        type as well as difficulty.
        """
        self.conv = parms[0]
        self.lr = parms[1]
        self.cm = parms[2]
        self.er = parms[3]
        self.rtype = parms[4]
        self.diff = parms[5]
        self.leap = parms[6]
    def __str__(self):
        info_str = "*************************\n"
        info_str += "Difficulty: {}\n".format(diff_dic[self.diff])
        info_str += "Ranged Type: {}\n".format("Yes" if self.rtype else "No")
        info_str += "Conviction Level: {}\n".format(self.conv)
        info_str += "Lower Resist Level: {}\n".format(self.lr)
        info_str += "Cold Mastery Level: {}\n".format(self.cm)
        info_str += "-% Enemy Resist: \n"
        info_str += "\n".join("\t{}: {}".format(res_dic[i], self.er[i]) for i in range(0, 6))
        info_str += "\n*************************"
        return info_str

def read_cmd():
    par = Parameters([0, 0, 0, 6*[0], 0, 2, 0])
    for x in sys.argv:
        #-conv=conviction lvl
        if bool(re.fullmatch(r"-conv=\d+", x)):
            par.conv = int(x[6:])
        #-lr=lower resist lvl
        if bool(re.fullmatch(r"-lr=\d+", x)):
            par.lr = int(x[4:])
        #-cm=cold mastery lvl
        if bool(re.fullmatch(r"-cm=\d+", x)):
            par.cm = int(x[4:])
        #-ecr=-% Enemey Cold Resist
        if bool(re.fullmatch(r"-ecr=\d+", x)):
            par.er[2] = int(x[5:])
        #-efr=-% Enemey Fire Resist
        if bool(re.fullmatch(r"-efr=\d+", x)):
            par.er[3] = int(x[5:])
        #-elr=-% Enemey Lightning Resist
        if bool(re.fullmatch(r"-elr=\d+", x)):
            par.er[4] = int(x[5:])
        #-epr=-% Enemey Poison Resist
        if bool(re.fullmatch(r"-epr=\d+", x)):
            par.er[5] = int(x[5:])
        #-r=rangetype
        if bool(re.fullmatch(r"-r=[01]", x)):
            par.rtype = int(x[3])            
        #-d=difficulty
        if bool(re.fullmatch(r"-d=[012]", x)):
            par.diff = int(x[3])
        #-leap=leaper y/n
        if bool(re.fullmatch(r"-leap", x)):
            par.leap = 1
    return par

print(read_cmd())

def dimin(x, a, b):
    """
    Implements a D2 style diminishing returns formula which takes input x and
    modifies it with parameters a,b.
        f(x)=int(a*x/(x+b))
    """
    return int(a*x/(b+x))

#"Mod": (ResType, ResBonus)
mod_dic = {"": (0, 0), "SS": (0, 50), "MB": (1, 20), 
           "CE": (2, 75), "FE": (3, 75), "LE": (4, 75)}

class ResistVector:
    def __init__(self, resistances):
        """
        Initializes a ResistVector as a list of 6 resistances in the order:
            Physical, Magic, Cold, Fire, Lightning, Poison
        """
        self.res = resistances
    def lower_cap(self):
        """
        IN PLACE
        Applies the lower cap of -100 to the ResistVector.        
        """
        self.res=[max(-100, x) for x in self.res]
    def conviction(self, slvl = 0):
        """
        IN PLACE
        Applies slvl Conviction to the ResistVector, for reference:
            Fire/Cold/Lightning Resist -% = min(25+5*slvl,150)                
        """
        malus = min(25+5*slvl, 150) if slvl else 0
        for i in range(2, 5):
            self.res[i] = self.res[i]-(malus if self.res[i] < 100 else malus//5)
        self.lower_cap()
    def lower_resist(self, slvl):
        """
        IN PLACE
        Applies slvl Lower Resist to the ResistVector, for reference:
            Fire/Cold/Light/Poison Resist -% = min(25+45*dimin(slvl,110,6)/100), 70)                
        with dimin(slvl,110,6)=110*slvl/(6+slvl)
        """
        malus = min(25+(45*dimin(slvl, 110, 6))//100, 70) if slvl else 0
        for i in range(2, 6):
            self.res[i] = self.res[i]-(malus if self.res[i] < 100 else malus//5)
        self.lower_cap()
    def enemy_resist(self, malus):
        '''
        IN PLACE
        Applies the malus vector consisting of -EPR, -EMR, -ECR, -EFR, -ELR
        and -EPR. to the ResistVector.
        '''
        self.res=[x-malus[i] if x < 100 else x for (i, x) in enumerate(self.res)]
        self.lower_cap()
    def cold_mastery(self, slvl):
        '''
        IN PLACE
        Applies slvl Cold Mastery to the Resist Vector, for reference:
            Cold Resist -% = 15+5*slvl
        '''
        malus = 15+5*slvl if slvl else 0
        if self.res[2] < 100:
            self.res[2] -= malus
        self.lower_cap()
    def generic_bonus(self, res_type, bonus):
        '''
        IN PLACE
        Applies bonus to resistance of type res_type if this does not result
        in a third immunity or increases one of two or more immunities.
        '''
        if self.res[res_type] < 100-bonus:
            self.res[res_type] += bonus
        elif 2 <= sum(1 for x in self.res if 100 <= x):
            pass
        else:
            self.res[res_type] += bonus
    def apply_mod(self, mod):
        """
        IN PLACE
        Applies the resistance bonus of "mod" to the Resist Vector. Key:
        SS - Stone Skin             +50 to phys. resistance
        MB - Mana Burn              +20 to magic resistance
        CE - Cold Enchangted        +75 to cold resistance
        FE - Fire Enchanted         +75 to fire resistance
        LE - Lightning Enchanted    +75 to light. resistance
        SH - Spectral Hit           +20 to cold, fire and light. resistance
                                    if respective resistance is less than 75
        MR - Magic Resistant        +40 to cold, fire and lightning resistance
                                    if respective resistance is less than 100
                                    and this does not result in a third immunity
                                    or increase one of two immunities
           - else                   +0 to all       
        """
        if mod == "MR":
            for i in range(2, 5):
                if self.res[i] < 100:
                    self.generic_bonus(i, 40)
        elif mod == "SH":
            for i in range(2, 5):
                if self.res[i] < 75:
                    self.res[i] += 20
        else:
            self.generic_bonus(mod_dic[mod][0], mod_dic[mod][1])



def resist_list(resistances, par):
    """
    Magic Resistant may not spawn in Normal difficulty and Multiple Shot only
    spawns for monsters that have rtype set to 1.
    
    Returns
    -------
    One Counter object for each resistance. Each counter has the possible
    resistances as keys and the number of their occurence in all the possible
    modifier permutations as values.
    """
    mods = ["FE", "CE", "SS", "SH", "MB"]
    mods.extend(["LE"]*(par.leap == 0)+[""]*(5+par.rtype)+["MR"]*(par.diff != 0))
    l = []
    def temp_func(res_vec,par,mod_vec):
        for j in range(0, par.diff+1):
            if mod_vec[j]!="":
                res_vec.apply_mod(mod_vec[j])
        if par.conv:
            res_vec.conviction(par.conv)
        if par.lr:
            res_vec.lower_resist(par.lr)
        if par.cm:
            res_vec.cold_mastery(par.cm)
        if sum(par.er):
            res_vec.enemy_resist(par.er)
        return res_vec
        
    for i in permutations(mods, par.diff+1):
        temp = ResistVector(resistances.res[:])
        temp = temp_func(temp, par, i)
        l.append(temp.res)
    r = tuple(zip(*l))
    return [Counter(r[i]) for i in range(0, 6)]

def percentage_list(resistances, par):
    '''
    Returns a list of possible resistances and their probability for the given
    res_type.

    Parameters
    ----------
    res_type: Resistance Type
    '''
    def percentages(dic):
        total = sum(dic.values())
        return {key:"{:.2%}".format(dic[key]/total) for key in dic.keys()}
    res_list = resist_list(resistances, par)
    for i in range(0,6):
        pairs = sorted(percentages(res_list[i]).items())
        print("\n{}:".format(res_dic[i]))
        for a in pairs:
            print("{}: {}".format(a[0], a[1]))

#Plague Bearer (Hell)
#Resists = ResistVector([50, 100, 0, 0, 0, 75])

Resists=ResistVector([int(x) for x in input("Enter Resistances: ").split(" ")])


percentage_list(Resists, read_cmd())