// Types partagés entre le site (client) et le serveur.

export type Statut = 'brouillon' | 'en_verification' | 'publie';
export type Categorie = 'labyrinthes' | 'logique' | 'nonogrammes' | 'cahiers' | 'packs';
export type Theme = 'animaux' | 'dinosaures' | 'espace' | 'pirates' | 'magie';
export type Difficulte = 'debutant' | 'intermediaire' | 'defi';

export interface Apercu {
  src: string;
  legende: string;
}

/** Produit tel qu'exposé publiquement par l'API (jamais de chemin de fichier). */
export interface ProduitPublic {
  id: string;
  slug: string;
  titre: string;
  sousTitre: string;
  description: string;
  prixCentimes: number;
  categorie: Categorie;
  themes: Theme[];
  age: string;
  difficultes: Difficulte[];
  objectif: string;
  pointsCles: string[];
  corriges: { inclus: boolean; separes: boolean; texte: string };
  couverture: string;
  apercus: Apercu[];
  nbPages: number | null;
  nbJeux: number | null;
  versionEncreEco: boolean;
  dateAjout: string;
  composants: string[];
  /** true uniquement si le produit est publié ET ses fichiers sont présents. */
  disponible: boolean;
  statut: Statut;
}

export interface Gratuit {
  id: string;
  titre: string;
  description: string;
  fichier: string;
  apercu: string;
  nb_pages: number;
  competences: string[];
  age: string;
}

export interface CatalogueReponse {
  produits: ProduitPublic[];
  gratuits: Gratuit[];
}

export type StatutCommande = 'en_attente' | 'payee' | 'echouee' | 'expiree' | 'anomalie';

export interface FichierTelechargeable {
  type: 'pdf' | 'corriges' | 'encre_eco';
  libelle: string;
  url: string;
  tailleOctets: number;
}

export interface CommandeResume {
  id: string;
  statut: StatutCommande;
  totalCentimes: number;
  emailMasque: string;
  creeLe: string;
  payeeLe: string | null;
  lignes: { produitId: string; titre: string; prixCentimes: number }[];
  consentement: { executionImmediateLe: string | null; texte: string };
  telechargements: { produitId: string; titre: string; fichiers: FichierTelechargeable[] }[];
  liensExpirentLe: string | null;
  accesExpireLe: string;
  modePaiement: ModePaiement;
}

export type ModePaiement = 'stripe_test' | 'stripe_live' | 'simulation' | 'non_configure';

export interface StatutServeur {
  paiement: ModePaiement;
  emails: 'smtp' | 'fichiers_locaux' | 'non_configuree';
  production: boolean;
}
