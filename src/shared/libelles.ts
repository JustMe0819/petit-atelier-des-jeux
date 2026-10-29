import type { Categorie, Difficulte, Theme } from './types';

export const CATEGORIES: { id: Categorie; libelle: string; court: string; icone: string; emoji: string }[] = [
  { id: 'labyrinthes', libelle: 'Labyrinthes', court: 'Labyrinthes', icone: 'alt_route', emoji: '🌀' },
  { id: 'logique', libelle: 'Logique & déduction', court: 'Logique', icone: 'extension', emoji: '🧩' },
  { id: 'nonogrammes', libelle: 'Nonogrammes', court: 'Nonogrammes', icone: 'grid_on', emoji: '⬛' },
  { id: 'cahiers', libelle: "Cahiers d'activités", court: 'Cahiers', icone: 'menu_book', emoji: '📖' },
  { id: 'packs', libelle: 'Packs & coffrets', court: 'Coffrets', icone: 'inventory_2', emoji: '📦' },
];

export const THEMES: { id: Theme; libelle: string; sousTitre: string; icone: string; couleur: string }[] = [
  { id: 'animaux', libelle: 'Animaux & nature', sousTitre: 'Forêt, prairie et océans', icone: 'cruelty_free', couleur: 'bg-secondary-container text-on-secondary-container' },
  { id: 'dinosaures', libelle: 'Dinosaures', sousTitre: 'Vallées préhistoriques', icone: 'egg', couleur: 'bg-primary-container text-on-primary-container' },
  { id: 'espace', libelle: 'Espace', sousTitre: 'Planètes & étoiles', icone: 'rocket_launch', couleur: 'bg-tertiary-container text-on-tertiary-container' },
  { id: 'pirates', libelle: 'Pirates & trésors', sousTitre: 'Îles & cartes secrètes', icone: 'sailing', couleur: 'bg-rose text-on-rose' },
  { id: 'magie', libelle: 'Magie & créatures', sousTitre: 'Sortilèges et dragons gentils', icone: 'auto_fix_high', couleur: 'bg-surface-container-highest text-on-surface' },
];

export const DIFFICULTES: { id: Difficulte; libelle: string }[] = [
  { id: 'debutant', libelle: 'Débutant (dès 6 ans)' },
  { id: 'intermediaire', libelle: 'Intermédiaire (7 ans)' },
  { id: 'defi', libelle: 'Défi (8 ans)' },
];

export const TRANCHES_PRIX = [
  { id: 'moins-5', libelle: 'Moins de 5 €', min: 0, max: 499 },
  { id: '5-10', libelle: 'De 5 € à 10 €', min: 500, max: 1000 },
  { id: 'plus-10', libelle: 'Plus de 10 €', min: 1001, max: Infinity },
] as const;

export function libelleCategorie(c: Categorie) {
  return CATEGORIES.find((x) => x.id === c)?.libelle ?? c;
}
export function libelleTheme(t: Theme) {
  return THEMES.find((x) => x.id === t)?.libelle ?? t;
}
