import path from 'node:path';
import { z } from 'zod';
import type { ModePaiement } from '../shared/types';

/**
 * Lecture et validation des variables d'environnement.
 * Les secrets (clés Stripe, SMTP, secret de signature) ne quittent jamais le serveur.
 */
const schema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().int().positive().default(8787),
  URL_PUBLIQUE: z.string().url().optional(),
  /** Fourni automatiquement par Vercel (ex. petit-atelier-des-jeux.vercel.app). */
  VERCEL_PROJECT_PRODUCTION_URL: z.string().optional(),
  VERCEL: z.string().optional(),
  SECRET_LIENS: z.string().optional(),

  PAIEMENT_MODE: z.enum(['stripe', 'simulation', 'desactive']).default('desactive'),
  STRIPE_SECRET_KEY: z.string().optional(),
  STRIPE_WEBHOOK_SECRET: z.string().optional(),
  STRIPE_CODES_PROMO: z.enum(['true', 'false']).default('false'),

  TURSO_DATABASE_URL: z.string().optional(),
  TURSO_AUTH_TOKEN: z.string().optional(),

  SMTP_HOST: z.string().optional(),
  SMTP_PORT: z.coerce.number().int().default(587),
  SMTP_USER: z.string().optional(),
  SMTP_PASS: z.string().optional(),
  EMAIL_EXPEDITEUR: z.string().default('Petit Atelier des Jeux <ne-pas-repondre@example.invalid>'),
  EMAIL_BOUTIQUE: z.string().optional(),

  DUREE_LIEN_TELECHARGEMENT_HEURES: z.coerce.number().positive().default(24),
  DUREE_ACCES_COMMANDE_JOURS: z.coerce.number().positive().default(30),

  DOSSIER_DONNEES: z.string().default('data'),
  DOSSIER_FICHIERS: z.string().default('storage'),
  FICHIER_CATALOGUE: z.string().default('catalogue/catalogue.json'),
});

export type Env = z.infer<typeof schema>;

export interface Config {
  env: Env['NODE_ENV'];
  production: boolean;
  port: number;
  urlPublique: string;
  secretLiens: string;
  paiement: {
    mode: ModePaiement;
    stripeSecretKey?: string;
    stripeWebhookSecret?: string;
    codesPromo: boolean;
  };
  email: {
    smtp?: { host: string; port: number; user?: string; pass?: string };
    expediteur: string;
    boutique?: string;
  };
  dureeLienTelechargementMs: number;
  dureeAccesCommandeMs: number;
  dossierDonnees: string;
  /** Base de données : Turso en ligne, fichier local sinon. */
  baseDeDonnees: { url: string; authToken?: string; distante: boolean };
  /** true sur Vercel (disque en lecture seule, fonctions sans état). */
  vercel: boolean;
  dossierFichiers: string;
  fichierCatalogue: string;
}

export class ErreurConfiguration extends Error {}

export function chargerConfig(source: NodeJS.ProcessEnv = process.env, racine = process.cwd()): Config {
  const e = schema.parse(source);
  const production = e.NODE_ENV === 'production';

  let secretLiens = e.SECRET_LIENS ?? '';
  if (secretLiens.length < 32) {
    if (production) {
      throw new ErreurConfiguration('SECRET_LIENS doit contenir au moins 32 caractères en production (voir .env.example).');
    }
    secretLiens = 'secret-de-developpement-uniquement-ne-pas-utiliser-en-production';
  }

  let mode: ModePaiement = 'non_configure';
  if (e.PAIEMENT_MODE === 'simulation') {
    if (production) {
      throw new ErreurConfiguration('PAIEMENT_MODE=simulation est interdit en production.');
    }
    mode = 'simulation';
  } else if (e.PAIEMENT_MODE === 'stripe') {
    const cle = e.STRIPE_SECRET_KEY ?? '';
    if (!cle.startsWith('sk_test_') && !cle.startsWith('sk_live_') && !cle.startsWith('rk_')) {
      throw new ErreurConfiguration('STRIPE_SECRET_KEY manquante ou invalide (elle commence par sk_test_ ou sk_live_).');
    }
    if (!e.STRIPE_WEBHOOK_SECRET?.startsWith('whsec_')) {
      throw new ErreurConfiguration('STRIPE_WEBHOOK_SECRET manquant (il commence par whsec_). Sans lui, les paiements ne peuvent pas être confirmés.');
    }
    const live = cle.startsWith('sk_live_') || cle.startsWith('rk_live_');
    if (live && !production) {
      throw new ErreurConfiguration('Clé Stripe LIVE détectée hors production. Utilisez une clé sk_test_ en développement.');
    }
    mode = live ? 'stripe_live' : 'stripe_test';
  }

  const urlPublique = e.URL_PUBLIQUE
    ?? (e.VERCEL_PROJECT_PRODUCTION_URL ? `https://${e.VERCEL_PROJECT_PRODUCTION_URL}` : 'http://localhost:5173');

  const dossierDonnees = path.resolve(racine, e.DOSSIER_DONNEES);
  let baseDeDonnees: Config['baseDeDonnees'];
  if (e.TURSO_DATABASE_URL) {
    const distante = !e.TURSO_DATABASE_URL.startsWith('file:') && e.TURSO_DATABASE_URL !== ':memory:';
    if (distante && !e.TURSO_AUTH_TOKEN) {
      throw new ErreurConfiguration('TURSO_AUTH_TOKEN manquant : il est fourni par Turso avec l’adresse de la base (voir docs/CONFIGURATION-SERVICES.md).');
    }
    baseDeDonnees = { url: e.TURSO_DATABASE_URL, authToken: e.TURSO_AUTH_TOKEN, distante };
  } else {
    if (production) {
      throw new ErreurConfiguration('TURSO_DATABASE_URL manquante en production : sans elle, les commandes ne seraient pas conservées (voir docs/CONFIGURATION-SERVICES.md).');
    }
    baseDeDonnees = { url: 'file:' + path.join(dossierDonnees, 'boutique.sqlite').replace(/\\/g, '/'), distante: false };
  }

  const smtp = e.SMTP_HOST ? { host: e.SMTP_HOST, port: e.SMTP_PORT, user: e.SMTP_USER, pass: e.SMTP_PASS } : undefined;

  return {
    env: e.NODE_ENV,
    production,
    port: e.PORT,
    urlPublique: urlPublique.replace(/\/$/, ''),
    secretLiens,
    paiement: {
      mode,
      stripeSecretKey: e.STRIPE_SECRET_KEY,
      stripeWebhookSecret: e.STRIPE_WEBHOOK_SECRET,
      codesPromo: e.STRIPE_CODES_PROMO === 'true',
    },
    email: { smtp, expediteur: e.EMAIL_EXPEDITEUR, boutique: e.EMAIL_BOUTIQUE },
    dureeLienTelechargementMs: e.DUREE_LIEN_TELECHARGEMENT_HEURES * 3600_000,
    dureeAccesCommandeMs: e.DUREE_ACCES_COMMANDE_JOURS * 86_400_000,
    dossierDonnees,
    baseDeDonnees,
    vercel: !!e.VERCEL,
    dossierFichiers: path.resolve(racine, e.DOSSIER_FICHIERS),
    fichierCatalogue: path.resolve(racine, e.FICHIER_CATALOGUE),
  };
}
