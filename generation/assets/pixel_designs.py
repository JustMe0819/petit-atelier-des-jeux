"""Dessins en pixels (créations originales) utilisés pour les nonogrammes.

`#` = case coloriée, `.` = case vide. Chaque dessin est vérifié par le solveur
(solution unique et résolution possible ligne par ligne) avant d'être utilisé.
Les dessins sont répartis en « réserves » pour qu'un même dessin n'apparaisse
pas dans deux produits différents.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dessin:
    id: str
    titre: str
    indice: str
    motif: str


def _d(id: str, titre: str, indice: str, motif: str) -> Dessin:
    return Dessin(id, titre, indice, motif)


# ---------------------------------------------------------------- 5 × 5 (pack)
PETITS_PACK: list[Dessin] = [
    _d("coeur", "Le cœur", "Un symbole d'amour.", """
.#.#.
#####
#####
.###.
..#.."""),
    _d("sapin", "Le sapin", "Un arbre de la forêt.", """
..#..
.###.
#####
..#..
.###."""),
    _d("poisson", "Le poisson", "Il vit dans l'eau.", """
.##..
####.
#.###
####.
.##.."""),
    _d("chat5", "Le chat", "Un animal qui fait « miaou ».", """
#...#
##.##
#####
#.#.#
.###."""),
    _d("papillon5", "Le papillon", "Il vole de fleur en fleur.", """
#...#
##.##
.###.
##.##
#...#"""),
    _d("soleil", "Le soleil", "Il brille dans le ciel.", """
#.#.#
.###.
#####
.###.
#.#.#"""),
    _d("lune", "La lune", "On la voit la nuit.", """
.###.
##...
#....
##...
.###."""),
    _d("etoile", "L'étoile", "Elle brille la nuit.", """
..#..
#####
.###.
.#.#.
#...#"""),
    _d("lapin5", "Le lapin", "Il a de longues oreilles.", """
.#.#.
.#.#.
#####
#.#.#
.###."""),
    _d("bateau", "Le bateau", "Il flotte sur la mer.", """
..#..
..##.
..#..
#####
.###."""),
    _d("goutte", "La goutte d'eau", "Elle tombe quand il pleut.", """
..#..
..#..
.###.
#####
.###."""),
    _d("parapluie", "Le parapluie", "Utile quand il pleut.", """
.###.
#####
..#..
..#..
.##.."""),
    _d("cerise", "Les cerises", "Des fruits rouges.", """
..###
.#..#
.#..#
##.##
##.##"""),
    _d("maison", "La maison", "On y habite.", """
..#..
.###.
#####
##.##
##.##"""),
    _d("souris", "La souris", "Elle aime le fromage.", """
##.##
##.##
.###.
.###.
..#.."""),
    _d("gland", "Le gland", "Le fruit du chêne.", """
.###.
#####
.###.
.###.
..#.."""),
    _d("fleur", "La fleur", "Elle pousse dans le jardin.", """
.#.#.
#####
.###.
..#..
.##.."""),
    _d("champignon", "Le champignon", "On le trouve en forêt.", """
.###.
#####
#####
..#..
.###."""),
    _d("tortue5", "La tortue", "Elle porte sa maison.", """
.###.
#####
#####
#.#.#
....."""),
    _d("nuage", "Le nuage", "Il flotte dans le ciel.", """
.....
.##..
#####
#####
....."""),
]

# ---------------------------------------------------------------- 10 × 10 (pack)
GRANDS_PACK: list[Dessin] = [
    _d("chat", "Le chat", "Un animal qui fait « miaou ».", """
.#......#.
.##....##.
.########.
##.####.##
##.####.##
##########
####..####
.########.
..######..
...####..."""),
    _d("lapin", "Le lapin", "Il adore les carottes.", """
.##....##.
.##....##.
.##....##.
.########.
##########
##.####.##
##########
####..####
.########.
..######.."""),
    _d("poisson10", "Le poisson", "Il vit dans la rivière.", """
..........
...###....
..#####..#
.#######.#
#.#######.
##########
.#######.#
..#####..#
...###....
.........."""),
    _d("oiseau", "L'oiseau", "Il fait son nid dans les arbres.", """
...##.....
..####....
.##.##....
#######...
..#######.
..########
...######.
....####..
....#..#..
...##.##.."""),
    _d("arbre", "L'arbre", "Il a des feuilles et des branches.", """
...####...
.########.
##########
##########
##########
.########.
...####...
....##....
....##....
..######.."""),
    _d("papillon", "Le papillon", "Il a de grandes ailes.", """
##......##
###.##.###
####..####
##########
.########.
..######..
.########.
###.##.###
##..##..##
....##...."""),
    _d("escargot", "L'escargot", "Il avance tout doucement.", """
..........
....####..
...##..##.
..##.##.##
..#.#..#.#
..#.#.##.#
#.#..#..##
##.##..##.
.########.
##########"""),
    _d("tortue", "La tortue", "Elle rentre la tête dans sa carapace.", """
..........
...####...
..######..
.##.##.###
.#########
##########
.#.#..#.#.
.#.#..#.#.
..........
.........."""),
    _d("canard", "Le canard", "Il nage dans la mare.", """
..........
...###....
..#.####..
..#####...
...##.....
.#####...#
##########
###....###
.########.
..######.."""),
    _d("chouette", "La chouette", "Elle ouvre grand les yeux la nuit.", """
#........#
##......##
.########.
##..##..##
#.#.##.#.#
##..##..##
.###..###.
.########.
..######..
..#....#.."""),
    _d("souris10", "La souris", "Elle a de grandes oreilles rondes.", """
###....###
####..####
####..####
.########.
.##.##.##.
.########.
..######..
...####...
....##....
.........."""),
    _d("ours", "L'ours", "Il aime le miel.", """
##......##
###.##.###
.########.
.#.####.#.
.########.
.###..###.
..#....#..
..##..##..
...####...
.........."""),
    _d("coccinelle", "La coccinelle", "Elle a des points sur le dos.", """
....##....
...####...
..##..##..
.###..###.
.#.#..#.#.
.###..###.
.##.##.##.
.###..###.
..##..##..
...####..."""),
    _d("fleur10", "La fleur", "Elle aime le soleil.", """
..##..##..
.########.
..######..
.###..###.
..######..
.########.
..##..##..
....##....
.##.##.##.
..######.."""),
    _d("champignon10", "Le champignon", "Il a un chapeau à pois.", """
...####...
.##.##.##.
##########
#.######.#
##########
....##....
....##....
...####...
...####...
.........."""),
    _d("pomme", "La pomme", "Un fruit qui pousse sur un arbre.", """
.....#....
....#.##..
....###...
.###..###.
##########
##.#######
##########
##########
.########.
..##..##.."""),
    _d("grenouille", "La grenouille", "Elle saute et fait « croâ ».", """
.##....##.
#..#..#..#
#.##..##.#
##########
##########
#........#
.########.
..######..
.##....##.
##......##"""),
    _d("abeille", "L'abeille", "Elle fabrique du miel.", """
..##..##..
.#..##..#.
..##..##..
...####...
..######..
..#....#..
..######..
..#....#..
...####...
....##...."""),
    _d("baleine", "La baleine", "Le plus gros animal de la mer.", """
..#.#.....
...#......
.######...
########..
##.#####..
#########.
##########
.######..#
..........
.........."""),
    _d("herisson", "Le hérisson", "Il a des piquants sur le dos.", """
..........
..#.#.#...
.#######..
##########
##########
.########.
#.#######.
##########
.#.#..#.#.
.........."""),
]

# ---------------------------------------------------------------- réserves pour les autres produits
PETITS_CAHIER: list[Dessin] = [
    _d("pied", "La chaussette", "On la met au pied.", """
.##..
.##..
.##..
.####
.####"""),
    _d("cle", "La clé", "Elle ouvre une porte.", """
###..
#.#..
###..
.####
...##"""),
    _d("arc", "Le pont", "On le traverse au-dessus de la rivière.", """
#####
#####
##.##
#...#
#...#"""),
    _d("verre", "La glace", "Un dessert bien froid.", """
.###.
#####
.###.
..#..
..#.."""),
]
GRANDS_CAHIER: list[Dessin] = [
    _d("renard", "Le renard", "Un animal roux de la forêt.", """
#........#
##......##
###....###
##########
#.##..##.#
##########
.########.
..######..
...####...
....##...."""),
    _d("ecureuil", "L'écureuil", "Il cache des noisettes.", """
......###.
.##..#####
.##.######
.###.#####
######.###
######..##
.#####.##.
..######..
..####....
.######..."""),
    _d("vache", "La vache", "Elle donne du lait.", """
##......##
.########.
.#.####.#.
.########.
..######..
.##....##.
.#.#..#.#.
.##....##.
..######..
.........."""),
    _d("maison10", "La maison", "On y vit en famille.", """
....##....
...####...
..######..
.########.
##########
.########.
.##.##.##.
.##.##.##.
.#####..#.
.#####..#."""),
]
PETITS_DINO: list[Dessin] = [
    _d("oeuf", "L'œuf", "Un bébé dinosaure va en sortir.", """
..#..
.###.
##.##
#####
.###."""),
    _d("os", "L'os", "On en trouve en fouillant le sol.", """
.....
#...#
#####
#...#
....."""),
]
GRANDS_DINO: list[Dessin] = [
    _d("trex", "Le tyrannosaure", "Un grand dinosaure avec de petits bras.", """
....######
....#.####
....######
....###...
#..#####..
##########
.#######..
..#####...
..##.##...
..##.##..."""),
    _d("diplodocus", "Le diplodocus", "Un dinosaure au très long cou.", """
.......##.
.......###
.......#..
.......#..
..####.#..
.########.
##########
#.#######.
..##..##..
..##..##.."""),
    _d("stegosaure", "Le stégosaure", "Il a des plaques sur le dos.", """
....#.#...
...######.
..#.#.#.#.
.#########
##########
.#.######.
..##..##..
..##..##..
..........
.........."""),
]
PETITS_GRATUITS: list[Dessin] = [
    _d("arbre5", "L'arbre", "Il pousse dans la forêt.", """
.###.
#####
#####
..#..
..#.."""),
    _d("escargot5", "L'escargot", "Il porte sa coquille.", """
.##..
#..#.
#.##.
#...#
#####"""),
    _d("canard5", "Le canard", "Il fait « coin-coin ».", """
.##..
###..
.#...
#####
.###."""),
]


# ---------------------------------------------------------------- cahiers-aventures
PETITS_ESPACE: list[Dessin] = [
    _d("fusee5", "La fusée", "Elle décolle vers les étoiles.", """
..#..
.###.
.#.#.
.###.
##.##"""),
    _d("soucoupe5", "La soucoupe", "Un vaisseau venu d'ailleurs.", """
..#..
.###.
#####
.#.#.
#...#"""),
]
GRANDS_ESPACE: list[Dessin] = [
    _d("alien10", "L'extraterrestre", "Il a deux antennes sur la tête.", """
..#....#..
...#..#...
..######..
.########.
.#..##..#.
.########.
..#....#..
...####...
..######..
..#....#.."""),
    _d("planete10", "La planète", "Elle tourne autour du Soleil.", """
...####...
..######..
.########.
##########
#.######.#
.#.####.#.
..#....#..
...####...
..........
.........."""),
    _d("robot10", "Le robot", "Il a des boutons et des antennes.", """
....##....
.....#....
..######..
..#.##.#..
..######..
..#....#..
#.######.#
##########
..##..##..
..##..##.."""),
]
PETITS_PIRATES: list[Dessin] = [
    _d("ancre5", "L'ancre", "Elle retient le bateau au fond de l'eau.", """
..#..
.###.
..#..
#.#.#
.###."""),
    _d("coffre5", "Le coffre", "On y cache un trésor.", """
.###.
#####
##.##
#####
#####"""),
]
GRANDS_PIRATES: list[Dessin] = [
    _d("voilier10", "Le voilier", "Le vent pousse ses voiles.", """
....#.....
....##....
...###....
..####....
.#####.#..
######.##.
....#..###
##########
.########.
..######.."""),
    _d("palmier10", "Le palmier", "Un arbre des îles.", """
.##..##...
#####.###.
..######..
.##.##.##.
#...##...#
....#.....
....##....
.....#....
.....##...
..######.."""),
    _d("crabe10", "Le crabe", "Il marche de côté sur la plage.", """
#.#....#.#
###....###
.#......#.
.#.#..#.#.
..######..
.########.
##########
.########.
#.#....#.#
#..#..#..#"""),
]
PETITS_MAGIE: list[Dessin] = [
    _d("chapeau5", "Le chapeau", "Le magicien le porte sur la tête.", """
...#.
..##.
.###.
.###.
#####"""),
    _d("cristal5", "Le cristal", "Une pierre qui brille.", """
.###.
#####
#####
.###.
..#.."""),
]
GRANDS_MAGIE: list[Dessin] = [
    _d("chateau10", "Le château", "Il a des tours et des drapeaux.", """
#.#....#.#
###....###
.#..##..#.
.#.####.#.
##########
#.##..##.#
##########
####..####
###....###
###....###"""),
    _d("dragon10", "Le dragon", "Il a des ailes et une longue queue.", """
.......##.
......####
.#....##.#
.##..###..
.###.##...
..######..
..#######.
.#######..
##.##.##..
#..#...#.."""),
    _d("potion10", "La potion", "Un flacon rempli de magie.", """
...####...
....##....
....##....
...####...
..######..
.##.####..
.#######.#
.########.
..######..
...####..."""),
]
