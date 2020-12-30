*************************************************************
** Resistance Calculator for Diablo 2: Lord of Destruction **
*************************************************************

------------------
- 0 Introduction -
------------------

Unique monsters in D2:LoD may spawn with up to three modifiers enhancing them in various ways. There are 7 modifiers which (potentially) improve a monster's resistances:
- Magic Resistant
- Spectral Hit
- Cold Enchanted
- Fire Enchanted
- Lightning Enchanted
- Mana Burn
- Stone Skin
The remaining 6 modifiers provide bonuses not related to resistances and are "duds" for the purposes of this text.

How many modifiers a monster spawns with is determined by the difficulty, namely 1 is assigned in normal, 2 are assigned in nightmare and 3 are assigned in hell. What modifiers are available is dependant on the difficulty as well as the monster type. Here are the rules for the pool:
- every modifier that is not "Lightning Enchanted", "Multiple Shots" or "Magic Resistant" is always in the pool. These are 10 modifiers.
- "Magic Resistant" is in the pool if and only if the difficulty is not normal.
- "Lightning Enchanted" is in the pool if and only if the monster is not a leaper.
- "Multiple Shots" is in the pool if and only if the monster is of ranged type.
For example a leaper in normal is not of ranged type and thus has a pool consisting of 10 modifiers whereas a skeleton archer in hell is of ranged type - is obviously not a leaper - and hence has a pool consisting of 13 modifiers.

After number of mods k and monster pool size n is determined the game will pick a modifier, add it to the monsters modifiers and remove it from the pool. If k is at least two it will repeat this step and so forth if k is three. In other words the game chooses a k-permutation of the n modifiers. See wikipedia for a technical definition:
https://en.wikipedia.org/wiki/Permutation#k-permutations_of_n
There are a total of n!/(n-k)! such permutations which to pick up the previous example means a leaper in normal has 10!/(10-1)!=10 possible modifier combinations whereas a skeleton archer in hell has a total of 13!/(13-3)!=13*12*11=1716 possible modifier combinations.

Since the order of the application of modifiers as well as the base resistances of the monster matter it is not a trivial task to calculate the distribution of resistances for each element. This program remedies that by simulating all possible modifier combinations under a variety of optional conditions (such as conviction, -% to enemey resist, etc.).


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

If you are unsure what resistances a monster has you should visit the Amazon Basin area pages:
https://www.theamazonbasin.com/wiki/index.php?title=Area
Choose the act your monster is in and then selected the area it is found in to view an extensive listing of monster properties including resists on all three difficulty levels.

See section 3 for a sample execution.

------------------
- 2 Parameters   -
------------------

The following parameters are available

	-conv=?		Applies level ? conviction aura.
				Default: ?=0

	-lr=?		Applies level ? lower resist.
				Default: ?=0

	-cm=?		Applies level ? cold mastery.
				Default: ?=0

	-ecr=?		Applies -?% to enemy cold resist.
				Default: ?=0

	-efr=?		Applies -?% enemy fire resist.
				Default: ?=0

	-elr=?		Applies -?% enemy lightning resist.
				Default: ?=0

	-epr=?		Applies -?% enemy poison resist.
				Default: ?=0

	-r=?		Whether the monster is ranged type (?=1) or not (?=0). If it is ranged type then it may spawn with "Multiple Shots" modifier.
				Default: ?=0
				
	-d=?		Difficulty: normal (?=0), nightmare (?=1), hell (?=2). Unique Monsters gain a total of ? modifiers.
				Modifier "Magic Resistant" can't spawn if ?=0
				Default: ?=2

	-leap		Set this if the monster is a leaper. They may not spawn "Lightning Enchanted".
				

------------------
- 3 Sample       -
------------------

Below is a sample application where we look at a Horror Mage in the Ancient Tunnels in Hell under the influence of conviction provided by the runeword infinity. We need to set ranged type to 1 and conviction to 12 and enter the correct resistances of a Horror Mage:

python resistancecalc.py -r=1 -conv=12
*************************
Difficulty: Hell
Ranged Type: Yes
Conviction Level: 12
Lower Resist Level: 0
Cold Mastery Level: 0
-% Enemy Resist: 
	Physical: 0
	Magic: 0
	Cold: 0
	Fire: 0
	Lightning: 0
	Poison: 0
*************************

Enter Resistances: 33 0 0 115 0 75

Physical:
33: 76.92%
83: 23.08%

Magic:
0: 76.92%
20: 23.08%

Cold:
-85: 41.96%
-65: 15.73%
-45: 15.85%
-25: 3.50%
-10: 17.48%
10: 1.75%
98: 3.55%
118: 0.17%

Fire:
98: 77.16%
173: 22.84%

Lightning:
-85: 41.96%
-65: 15.73%
-45: 15.85%
-25: 3.50%
-10: 17.60%
10: 1.75%
98: 3.44%
118: 0.17%

Poison:
75: 100.00%



------------------
- 4 Credits      -
------------------

Thanks to Luhkoh for independently verifying the resist distributions for Ancient Tunnel monsters via excel macros!

Thanks to onderduiker for curating the Amazon Basin, especially the sections on monsters and areas.

Thanks to everyone that debugged the game to find the mechanisms of modifier selection and application, it's unclear who did this exactly but this program would not be possible without them.