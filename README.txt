*************************************************************
** Resistance Calculator for Diablo 2: Lord of Destruction **
*************************************************************

------------------
- 0 Introduction -
------------------
Unique Monsters in D2:LoD may spawn with up to three modifiers enhancing them in various ways. There are 7 modifiers which (potentially) improve a monster's resistances:
- Magic Resistant, Spectral Hit, Cold Enchanted, Fire Enchanted, Lightning Enchanted, Mana Burn and Stone Skin

The order in which the modifiers are assigned plays a crucial role in the determination of the monster's final resistances. Since there are a total of 13 (12 for melee monsters) modifiers to choose from there are 13^(3)=1716 (or 12^(2)=1320 for melee monsters) possible combinations of modifiers in Hell difficulty. To calculate the resistances of a monster for each of those combinations by hand is not feasible. This calculator can do this work for us and thus can provide a statistic of which resistances a boss monster can have together with the corresponding chance for each resistance percentage.

It can also take into account whether the monster is under the influence of the Conviction aura provided by the runeword "Infinity" or whether its cold resistances are affected by Cold Mastery.

Currently it does not take into account other sources of resistance reduction such as Rainbow Facets, Griffon's Eye, etc...

Finally monsters of the "Leaper" type may not spawn with "Lightning Enchanted" in any difficulty. This is not yet taken into account, so this calculator will yield wrong results if you feed it a Leaper's resistances.


------------------
- 1 Execution    -
------------------
Follow these steps:
	1. Open the Python Shell/Prompt.
	2. Navigate to the directory in which "resistancecalc.py" is stored.
	3. Type "python resistancecalc.py". (see section 2 for parameters)
	4. Input the base resistances of the monster you want to analyze separated by spaces in the order:
		Physical Magic Cold Fire Lightning Poison
	5. Press Enter.
If you are unsure what resistances a monster has you should visit the Amazon Basin

------------------
- 2 Parameters   -
------------------
The following parameters are available
	-r=?		Whether the monster is ranged type (?=1) or not (?=0). If it is ranged type then it may spawn with "Multiple Shots" modifier.
				Default: ?=0
				
	-d=?		Difficulty: normal (?=0), nightmare (?=1), hell (?=2). Unique Monsters gain a total of ? modifiers.
				Modifier "Magic Resistant" can't spawn if ?=0
				Default: ?=2
				
	-inf		Set this if you use infinity.
	
	-cm=?		Cold Mastery lvl given by ?.
				Default: ?=0

	-ecr=?		-% Enemy Cold Resist given by ?.
				Default: ?=0

	-efr=?		-% Enemy Fire Resist given by ?.
				Default: ?=0

	-elr=?		-% Enemy Lightning Resist given by ?.
				Default: ?=0

	-epr=?		-% Enemy Poison Resist given by ?.
				Default: ?=0

















