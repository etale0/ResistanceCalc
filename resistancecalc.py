# -*- coding: utf-8 -*-
"""
Created on Sun Dec 20 20:21:38 2020.

@author: etale
"""

from itertools import permutations
from collections import Counter
import sys
import re

# sys.argv.extend(["-conv=0", "-efr=20", "-epr=20"])

# Index of difficulty: name of difficulty
diff_dic = {0: "Normal", 1: "Nightmare", 2: "Hell"}

# Index of resistance type: name of resistance type
res_d = {0: "Physical", 1: "Magic", 2: "Cold",
         3: "Fire", 4: "Lightning", 5: "Poison"}

# "Mod": (ResType, ResBonus)
mod_dic = {"": (0, 0), "SS": (0, 50), "MB": (1, 20),
           "CE": (2, 75), "FE": (3, 75), "LE": (4, 75)}


class Parameters:
    """Container for command line options."""

    def __init__(self, parms):
        """
        Initialize the parameter vector.

        Contains the command line options for conviction, lower resist, cold
        mastery, -% enemy resist, ranged type, difficulty and leaper.
        """
        self.conv = parms[0]
        self.lr = parms[1]
        self.cm = parms[2]
        self.er = parms[3]
        self.rtype = parms[4]
        self.diff = parms[5]
        self.leap = parms[6]

    def __str__(self):
        """List all parameters for convenience."""
        info_str = "*************************\n"
        info_str += "Difficulty: {}\n".format(diff_dic[self.diff])
        info_str += "Ranged Type: {}\n".format("Yes" if self.rtype else "No")
        info_str += "Conviction Level: {}\n".format(self.conv)
        info_str += "Lower Resist Level: {}\n".format(self.lr)
        info_str += "Cold Mastery Level: {}\n".format(self.cm)
        info_str += "-% Enemy Resist: \n"
        enemy_res = ["\t{}: {}".format(res_d[i], self.er[i]) for i in range(6)]
        info_str += "\n".join(enemy_res)
        info_str += "\n*************************"
        return info_str


def read_cmd():
    """Collect all command line options and put them in a Parameters object."""
    par = Parameters([0, 0, 0, 6*[0], 0, 2, 0])
    for x in sys.argv:
        # -conv=conviction lvl
        if bool(re.fullmatch(r"-conv=\d+", x)):
            par.conv = int(x[6:])
        # -lr=lower resist lvl
        if bool(re.fullmatch(r"-lr=\d+", x)):
            par.lr = int(x[4:])
        # -cm=cold mastery lvl
        if bool(re.fullmatch(r"-cm=\d+", x)):
            par.cm = int(x[4:])
        # -ecr=-% Enemey Cold Resist
        if bool(re.fullmatch(r"-ecr=\d+", x)):
            par.er[2] = int(x[5:])
        # -efr=-% Enemey Fire Resist
        if bool(re.fullmatch(r"-efr=\d+", x)):
            par.er[3] = int(x[5:])
        # -elr=-% Enemey Lightning Resist
        if bool(re.fullmatch(r"-elr=\d+", x)):
            par.er[4] = int(x[5:])
        # -epr=-% Enemey Poison Resist
        if bool(re.fullmatch(r"-epr=\d+", x)):
            par.er[5] = int(x[5:])
        # -r=rangetype
        if bool(re.fullmatch(r"-r=[01]", x)):
            par.rtype = int(x[3])
        # -d=difficulty
        if bool(re.fullmatch(r"-d=[012]", x)):
            par.diff = int(x[3])
        # -leap=leaper y/n
        if bool(re.fullmatch(r"-leap", x)):
            par.leap = 1
    return par


def dimin(x, a, b):
    """
    Implement a D2 style diminishing returns formula.

    Takes input x and modifies it with parameters a and b.
        f(x)=int(a*x/(x+b))
    """
    return int(a*x/(b+x))


class ResistVector:
    """Container for all resistances of a monster."""

    def __init__(self, resistances):
        """
        Initialize the ResistVector as a list of 6 resistances.

        Order of resistances:
            Physical, Magic, Cold, Fire, Lightning, Poison
        """
        self.res = resistances

    def lower_cap(self):
        """Apply the lower cap of -100 to the ResistVector (IN PLACE)."""
        self.res = [max(-100, x) for x in self.res]

    def conviction(self, slvl=0):
        """
        Apply slvl Conviction to the ResistVector (IN PLACE).

        Provides:
            -min(25+5*slvl, 150) %
        to cold, fire and lightning resistance.
        """
        malus = min(25+5*slvl, 150) if slvl else 0
        for i in range(2, 5):
            real_malus = malus if self.res[i] < 100 else malus//5
            self.res[i] = self.res[i]-real_malus
        self.lower_cap()

    def lower_resist(self, slvl):
        """
        Apply slvl Lower Resist to the ResistVector (IN PLACE).

        Provides:
           -min(25+45*dimin(slvl, 110, 6)/100), 70) %
        to all resistances except magic and physcial, with:
            dimin(slvl, 110, 6)=110*slvl/(6+slvl)
        """
        malus = min(25+(45*dimin(slvl, 110, 6))//100, 70) if slvl else 0
        for i in range(2, 6):
            real_malus = malus if self.res[i] < 100 else malus//5
            self.res[i] = self.res[i]-real_malus
        self.lower_cap()

    def enemy_resist(self, malus):
        """
        Apply -% enemy resist to the ResistVector (IN PLACE).

        malus vector consists of -EPhR, -EMR, -ECR, -EFR, -ELR and -EPR.
        """
        self.res = [x-m if x < 100 else x for (x, m) in zip(self.res, malus)]
        self.lower_cap()

    def cold_mastery(self, slvl):
        """
        Apply slvl Cold Mastery to the Resist Vector (IN PLACE).

        Provides:
            -(15+5*slvl) %
        to enemy cold resist.
        """
        malus = 15+5*slvl if slvl else 0
        if self.res[2] < 100:
            self.res[2] -= malus
        self.lower_cap()

    def generic_bonus(self, res_type, bonus):
        """
        Apply bonus to resistance (IN PLACE).

        Adds bonus to type resistance of index res_type if this does not
        result in a third immunity or increase one of two or more immunities.
        """
        if self.res[res_type] < 100-bonus:
            self.res[res_type] += bonus
        elif 2 <= sum(1 for x in self.res if 100 <= x):
            pass
        else:
            self.res[res_type] += bonus

    def apply_mod(self, mod):
        """
        Apply the mod's bonuses to the ResistVector (IN PLACE).

        Key:
        SS - Stone Skin             +50 to phys. resistance
        MB - Mana Burn              +20 to magic resistance
        CE - Cold Enchangted        +75 to cold resistance
        FE - Fire Enchanted         +75 to fire resistance
        LE - Lightning Enchanted    +75 to light. resistance
        SH - Spectral Hit           +20 to cold, fire and light. resistance
                                    if respective resistance is less than 75
        MR - Magic Resistant        +40 to cold, fire and lightning resistance
                                    if respective resistance is less than 100
                                    and it does not result in a third immunity
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
    Return Counter with possible values/multiplicities for each resistance.

    Each Counter object has the possible resistance values as keys and the
    amount of their occurences in all modifier permutations as values.

    Modifier list consists of all 13 modifiers minus up to three:
        Magic Resistant         only in nightmare & hell
        Multiple Shots          only on ranged monsters.
        Lightning Enchanted     not on leapers
    """
    mods = ["FE", "CE", "SS", "SH", "MB"].extend(["LE"]*(par.leap == 0))
    mods.extend([""]*(5+par.rtype)+["MR"]*(par.diff != 0))
    lst = []

    def temp_func(res_vec, par, mod_vec):
        for j in range(0, par.diff+1):
            if mod_vec[j] != "":
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
        lst.append(temp.res)
    r = tuple(zip(*lst))
    return [Counter(r[i]) for i in range(0, 6)]


def percentage_list(resistances, par):
    """Return a list of possible resistances and their probability."""
    def percentages(dic):
        total = sum(dic.values())
        return {key: "{:.2%}".format(dic[key]/total) for key in dic.keys()}
    res_list = resist_list(resistances, par)
    for i in range(0, 6):
        pairs = sorted(percentages(res_list[i]).items())
        print("\n{}:".format(res_d[i]))
        for a in pairs:
            print("{}: {}".format(a[0], a[1]))


def main():
    """Get resistances from user and output statistic and options."""
    # Plague Bearer (Hell)
    # Resists = ResistVector([50, 100, 0, 0, 0, 75])
    prompt = "Enter Resistances: "
    print(read_cmd())
    Resists = ResistVector([int(x) for x in input(prompt).split(" ")])
    percentage_list(Resists, read_cmd())


if __name__ == "__main__":
    main()
