"""Dessins en couleurs (créations originales) pour les coloriages codés.

Chaque lettre correspond à une couleur de crayon ; `.` = case laissée blanche.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DessinCouleur:
    id: str
    titre: str
    legende: dict[str, str]   # lettre → nom de couleur (voir theme.COULEURS_CRAYON)
    motif: str


COCCINELLE = DessinCouleur("coccinelle", "La coccinelle", {"N": "noir", "R": "rouge", "V": "vert"}, """
....NNNN....
...NNNNNN...
..RRRNNRRR..
.RRRRNNRRRR.
.RNNRNNRNNR.
RRNNRNNRNNRR
RRRRRNNRRRRR
RRRRRNNRRRRR
RNNRRNNRRNNR
.RNNRNNRNNR.
..RRRNNRRR..
VVVVVVVVVVVV""")

POISSON = DessinCouleur("poisson", "Le poisson", {"O": "orange", "J": "jaune", "N": "noir", "B": "bleu"}, """
.........B..
....JJJ.....
...OOOOO..B.
..OOOOJOO..J
.OONOOJOOOJJ
OOOOOOJOOJJJ
.OOOOOJOOOJJ
..OOOOJOO..J
...OOOOO....
....JJJ.....
.B..........
BBBBBBBBBBBB""")

CHAMPIGNON = DessinCouleur("champignon", "Le champignon", {"R": "rouge", "M": "marron", "V": "vert"}, """
....RRRR....
..RRR..RRR..
.RR.RRRR.RR.
.RRRRRRRRRR.
RR..RRRR..RR
RRRRRRRRRRRR
....MMMM....
....MMMM....
....MMMM....
...MMMMMM...
V.V.V..V.V.V
VVVVVVVVVVVV""")

DINO_VERT = DessinCouleur("dino-vert", "Le petit diplodocus", {"V": "vert", "J": "jaune", "N": "noir", "M": "marron"}, """
.........VV.
........VVNV
........VVVV
........VV..
........VV..
...VVVVVVV..
..VVJVVJVVV.
VVVVVVVVVVV.
...VJVVVJV..
...VV...VV..
...VV...VV..
MMMMMMMMMMMM""")

VOLCAN = DessinCouleur("volcan", "Le volcan", {"G": "gris", "R": "rouge", "O": "orange", "M": "marron", "V": "vert"}, """
.G..G...G...
..G.G..G....
....RORR....
....MRRM....
...MMORMM...
...MMMRMM...
..MMMMRMMM..
..MMMMMMMM..
.MMMMMMMMMM.
.MMMMMMMMMM.
MMMMMMMMMMMM
VVVVVVVVVVVV""")

OEUF = DessinCouleur("oeuf", "L'œuf de dinosaure", {"J": "jaune", "V": "vert", "M": "marron"}, """
....JJJJ....
...JJJJJJ...
..JJVVJJJJ..
..JVVVVJJJ..
.JJJVVJJVVJ.
.JJJJJJVVVJ.
.JVVJJJJVJJ.
.VVVVJJJJJJ.
.JVVJJJVVJJ.
..JJJJVVVJ..
M..JJJJJJ..M
MMMMMMMMMMMM""")

CAHIER = [COCCINELLE, POISSON, CHAMPIGNON]
DINO = [DINO_VERT, VOLCAN, OEUF]


# ---------------------------------------------------------------- cahiers-aventures (espace, pirates, magie)
FUSEE = DessinCouleur("fusee", "La fusée", {"R": "rouge", "G": "gris", "B": "bleu", "O": "orange", "J": "jaune"}, """
.....RR.....
....RRRR....
....GGGG....
...GGBBGG...
...GBBBBG...
...GGBBGG...
...GGGGGG...
..RGGGGGGR..
.RRGGGGGGRR.
.RR.OJJO.RR.
....OJJO....
.....OO.....""")

PLANETE = DessinCouleur("planete", "La planète", {"B": "bleu", "J": "jaune", "U": "violet", "P": "rose"}, """
BBBBBBBBBBJB
BJBBBUUUBBBB
BBBBUUUUUBBB
BBBUUPPUUUBB
BBBUUUUUUUBB
JJJJJJJJJJJJ
BBBUUUUUUUBB
BBBBUUPUUBBB
BBBBBUUUBBBB
BJBBBBBBBBBB
BBBBBBBBBJBB
BBBJBBBBBBBB""")

EXTRATERRESTRE = DessinCouleur("extraterrestre", "L'extraterrestre", {"V": "vert", "N": "noir", "B": "bleu", "G": "gris"}, """
...V....V...
....V..V....
...VVVVVV...
..VVVVVVVV..
..VNNVVNNV..
..VVVVVVVV..
...VVNNVV...
....VVVV....
..GGGGGGGG..
.GGBBBBBBGG.
GGGGGGGGGGGG
.N..N..N..N.""")

BATEAU_PIRATE = DessinCouleur("bateau-pirate", "Le bateau pirate", {"N": "noir", "R": "rouge", "M": "marron", "G": "gris", "B": "bleu"}, """
.....NRR....
.....N......
...N.N.N....
..NN.N.NN...
.NNN.N.NNN..
NNNN.N.NNNN.
.....N......
MMMMMMMMMMMM
.MMGMMGMMGM.
..MMMMMMMM..
BBBBBBBBBBBB
BB.BBB.BBB.B""")

PERROQUET = DessinCouleur("perroquet", "Le perroquet", {"R": "rouge", "J": "jaune", "N": "noir", "V": "vert", "M": "marron", "B": "bleu"}, """
....RRRR....
...RRRRRR...
..RRNRRRJJ..
..RRRRRRJJJ.
..RRRRRR.J..
...RVVRR....
...VVVVR....
...VVVVR....
MMMMMMMMMMMM
....BBB.....
....BBB.....
.....BB.....""")

COFFRE = DessinCouleur("coffre", "Le trésor", {"J": "jaune", "O": "orange", "M": "marron", "N": "noir"}, """
...J..O..J..
..JOJJJOJJ..
.MMMMMMMMMM.
.MJMMMMMMJM.
MMJMMMMMMJMM
JJJJJJJJJJJJ
MMJMMNNMMJMM
MMJMMNNMMJMM
MMJMMMMMMJMM
MMJMMMMMMJMM
MMMMMMMMMMMM
............""")

CHATEAU = DessinCouleur("chateau", "Le château", {"U": "violet", "G": "gris", "J": "jaune", "M": "marron", "V": "vert"}, """
.U........U.
UUU......UUU
UUU..J...UUU
GGG.G.G.GGG.
GJG.GGG.GJG.
GGGGGGGGGGG.
GGGGGGGGGGG.
GGGGMMMGGGG.
GGGMMMMMGGG.
GGGMMMMMGGG.
GGGMMMMMGGG.
VVVVVVVVVVVV""")

DRAGON = DessinCouleur("dragon", "Le petit dragon", {"V": "vert", "U": "violet", "J": "jaune", "N": "noir", "O": "orange"}, """
........VVV.
.......VNVVV
...U...VVVVV
..UUU..VVO..
.UUUUU.VV...
..UVVVVVV...
.VVVJJJVV...
VVVVJJJVV...
.O.VJJJVV...
...VVVVVV...
...VV..VV...
...VV..VV...""")

POTION = DessinCouleur("potion", "La potion", {"M": "marron", "C": "bleu clair", "P": "rose", "U": "violet"}, """
.....MM.....
.....MM.....
....CCCC....
.....CC.....
.....CC.....
....CCCC....
...CCCCCC...
..PPPPPPPP..
..PPUPPPPP..
..PPPPPUPP..
...PPPPPP...
....PPPP....""")

ESPACE = [FUSEE, PLANETE, EXTRATERRESTRE]
PIRATES = [BATEAU_PIRATE, PERROQUET, COFFRE]
MAGIE = [CHATEAU, DRAGON, POTION]
