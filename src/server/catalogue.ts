import fs from 'node:fs';
import path from 'node:path';
import { z } from 'zod';
import type { CatalogueReponse, Gratuit, ProduitPublic } from '../shared/types';

const produitSchema = z.object({
  id: z.string().regex(/^[a-z0-9-]+$/),
  slug: z.string().regex(/^[a-z0-9-]+$/),
  titre: z.string().min(1),
  sous_titre: z.string().default(''),
  description: z.string(),
  prix_centimes: z.number().int().positive(),
  categorie: z.enum(['labyrinthes', 'logique', 'nonogrammes', 'cahiers', 'packs']),
  themes: z.array(z.enum(['animaux', 'dinosaures', 'espace', 'pirates', 'magie'])),
  age: z.string(),
  difficultes: z.array(z.enum(['debutant', 'intermediaire', 'defi'])),
  objectif: z.object({ texte: z.string(), nb_jeux: z.number().nullable(), nb_pages: z.number().nullable() }),
  points_cles: z.array(z.string()).default([]),
  corriges: z.object({ inclus: z.boolean(), separes: z.boolean(), texte: z.string() }),
  couverture: z.string(),
  apercus: z.array(z.object({ src: z.string(), legende: z.string() })).default([]),
  fichiers: z.object({ pdf: z.string().nullable(), corriges: z.string().nullable(), encre_eco: z.string().nullable() }),
  contenu: z.object({ nb_pages: z.number().nullable(), nb_jeux: z.number().nullable(), genere_le: z.string().nullable() }),
  qa: z.object({ rapport: z.string().nullable(), valide_automatiquement: z.boolean() }).passthrough(),
  statut: z.enum(['brouillon', 'en_verification', 'publie']),
  date_ajout: z.string(),
  composants: z.array(z.string()).default([]),
});

const catalogueSchema = z.object({
  version: z.number(),
  devise: z.literal('EUR'),
  produits: z.array(produitSchema),
  gratuits: z.array(z.any()).default([]),
});

export type ProduitBrut = z.infer<typeof produitSchema>;
export type TypeFichier = 'pdf' | 'corriges' | 'encre_eco';

export interface FichierProduit {
  produitId: string;
  titreProduit: string;
  type: TypeFichier;
  cheminAbsolu: string;
  nomTelechargement: string;
}

const LIBELLES_FICHIER: Record<TypeFichier, string> = {
  pdf: 'Fichier principal (PDF A4)',
  corriges: 'Corrigés (PDF séparé)',
  encre_eco: "Version économie d'encre (PDF)",
};
export const libelleFichier = (t: TypeFichier) => LIBELLES_FICHIER[t];

/**
 * Accès au catalogue JSON. Le fichier est relu automatiquement s'il a changé
 * (pas besoin de redémarrer le serveur après une publication).
 */
export class Catalogue {
  private produits: ProduitBrut[] = [];
  private gratuits: Gratuit[] = [];
  private mtime = 0;

  constructor(private fichier: string, private dossierFichiers: string) {
    this.recharger(true);
  }

  private recharger(force = false) {
    const stat = fs.statSync(this.fichier);
    if (!force && stat.mtimeMs === this.mtime) return;
    const brut = JSON.parse(fs.readFileSync(this.fichier, 'utf8'));
    const donnees = catalogueSchema.parse(brut);
    const ids = new Set<string>();
    for (const p of donnees.produits) {
      if (ids.has(p.id)) throw new Error(`Identifiant produit en double : ${p.id}`);
      ids.add(p.id);
    }
    for (const p of donnees.produits) {
      for (const c of p.composants) if (!ids.has(c)) throw new Error(`Composant inconnu ${c} dans ${p.id}`);
    }
    this.produits = donnees.produits;
    this.gratuits = donnees.gratuits as Gratuit[];
    this.mtime = stat.mtimeMs;
  }

  tous(): ProduitBrut[] {
    this.recharger();
    return this.produits;
  }

  trouver(id: string): ProduitBrut | undefined {
    return this.tous().find((p) => p.id === id || p.slug === id);
  }

  cheminFichier(relatif: string): string | null {
    const absolu = path.resolve(this.dossierFichiers, relatif);
    // Protection contre la sortie du dossier privé (« ../ »).
    if (!absolu.startsWith(this.dossierFichiers + path.sep)) return null;
    return absolu;
  }

  private fichierPresent(relatif: string | null): boolean {
    if (!relatif) return false;
    const abs = this.cheminFichier(relatif);
    return !!abs && fs.existsSync(abs);
  }

  /** Un produit est vendable seulement s'il est publié et que ses fichiers existent réellement. */
  estAchetable(id: string): boolean {
    const p = this.trouver(id);
    if (!p || p.statut !== 'publie') return false;
    if (p.composants.length > 0) {
      return p.composants.every((c) => {
        const comp = this.trouver(c);
        return !!comp && comp.statut === 'publie' && this.fichierPresent(comp.fichiers.pdf);
      });
    }
    return this.fichierPresent(p.fichiers.pdf);
  }

  /** Liste des fichiers livrés pour un produit (un coffret livre les fichiers de ses composants). */
  fichiersLivres(id: string): FichierProduit[] {
    const p = this.trouver(id);
    if (!p) return [];
    const sources = p.composants.length > 0 ? p.composants.map((c) => this.trouver(c)!).filter(Boolean) : [p];
    const resultat: FichierProduit[] = [];
    for (const s of sources) {
      for (const type of ['pdf', 'corriges', 'encre_eco'] as const) {
        const rel = s.fichiers[type];
        if (!rel) continue;
        const abs = this.cheminFichier(rel);
        if (!abs || !fs.existsSync(abs)) continue;
        const suffixe = type === 'pdf' ? '' : type === 'corriges' ? '-corriges' : '-economie-encre';
        resultat.push({ produitId: s.id, titreProduit: s.titre, type, cheminAbsolu: abs, nomTelechargement: `${s.slug}${suffixe}.pdf` });
      }
    }
    return resultat;
  }

  versionPublique(p: ProduitBrut): ProduitPublic {
    return {
      id: p.id,
      slug: p.slug,
      titre: p.titre,
      sousTitre: p.sous_titre,
      description: p.description,
      prixCentimes: p.prix_centimes,
      categorie: p.categorie,
      themes: p.themes,
      age: p.age,
      difficultes: p.difficultes,
      objectif: p.objectif.texte,
      pointsCles: p.points_cles,
      corriges: p.corriges,
      couverture: p.couverture,
      apercus: p.apercus,
      nbPages: p.contenu.nb_pages,
      nbJeux: p.contenu.nb_jeux,
      versionEncreEco: !!p.fichiers.encre_eco,
      dateAjout: p.date_ajout,
      composants: p.composants,
      disponible: this.estAchetable(p.id),
      statut: p.statut,
    };
  }

  reponsePublique(): CatalogueReponse {
    return { produits: this.tous().map((p) => this.versionPublique(p)), gratuits: this.gratuits };
  }
}
