import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import Stripe from 'stripe';
import { vi } from 'vitest';
import { chargerConfig } from '../src/server/config';
import { assembler } from '../src/server/demarrage';
import { FournisseurStripe } from '../src/server/paiement';
import type { Messagerie, Message } from '../src/server/emails';

export const SECRET_WEBHOOK = 'whsec_test_secret_pour_les_tests_automatiques';

/**
 * Crée une boutique isolée (dossier temporaire) avec un catalogue de test :
 * deux produits publiés avec de faux PDF, un brouillon, et un coffret.
 */
export function boutiqueDeTest(options: { mode?: 'stripe' | 'simulation' | 'desactive'; codesPromo?: boolean } = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pad-test-'));
  const stockage = path.join(dir, 'storage');
  fs.mkdirSync(path.join(stockage, 'produits/a'), { recursive: true });
  fs.mkdirSync(path.join(stockage, 'produits/b'), { recursive: true });
  fs.writeFileSync(path.join(stockage, 'produits/a/a.pdf'), '%PDF-1.4 produit A');
  fs.writeFileSync(path.join(stockage, 'produits/a/a-corriges.pdf'), '%PDF-1.4 corriges A');
  fs.writeFileSync(path.join(stockage, 'produits/b/b.pdf'), '%PDF-1.4 produit B');
  fs.writeFileSync(path.join(dir, 'secret.txt'), 'NE DOIT PAS FUITER');

  const base = (id: string, prix: number, statut: string, pdf: string | null, corriges: string | null = null, composants: string[] = []) => ({
    id, slug: id, titre: `Produit ${id.toUpperCase()}`, sous_titre: '', description: 'desc', prix_centimes: prix, categorie: composants.length ? 'packs' : 'labyrinthes',
    themes: ['animaux'], age: '6-8 ans', difficultes: ['debutant'], objectif: { texte: 'x', nb_jeux: 1, nb_pages: 1 }, points_cles: [],
    corriges: { inclus: true, separes: false, texte: '' }, couverture: '/x.webp', apercus: [],
    fichiers: { pdf, corriges, encre_eco: null }, contenu: { nb_pages: 1, nb_jeux: 1, genere_le: null },
    qa: { rapport: null, valide_automatiquement: true }, statut, date_ajout: '2026-01-01', composants,
  });
  const catalogue = {
    version: 1, devise: 'EUR',
    produits: [
      base('a', 390, 'publie', 'produits/a/a.pdf', 'produits/a/a-corriges.pdf'),
      base('b', 490, 'publie', 'produits/b/b.pdf'),
      base('brouillon', 990, 'brouillon', null),
      base('evasion', 100, 'publie', '../secret.txt'),
      base('coffret', 690, 'publie', null, null, ['a', 'b']),
    ],
    gratuits: [],
  };
  const fichierCatalogue = path.join(dir, 'catalogue.json');
  fs.writeFileSync(fichierCatalogue, JSON.stringify(catalogue));

  const mode = options.mode ?? 'stripe';
  const config = chargerConfig({
    NODE_ENV: 'test',
    URL_PUBLIQUE: 'http://boutique.test',
    SECRET_LIENS: 'x'.repeat(40),
    PAIEMENT_MODE: mode,
    STRIPE_SECRET_KEY: mode === 'stripe' ? 'sk_test_cle_factice' : undefined,
    STRIPE_WEBHOOK_SECRET: mode === 'stripe' ? SECRET_WEBHOOK : undefined,
    STRIPE_CODES_PROMO: options.codesPromo ? 'true' : 'false',
    DOSSIER_DONNEES: path.join(dir, 'data'),
    DOSSIER_FICHIERS: stockage,
    FICHIER_CATALOGUE: fichierCatalogue,
  } as NodeJS.ProcessEnv, dir);

  const assemble = assembler(config, { racine: dir });

  // Remplace la messagerie par une boîte en mémoire.
  const emails: Message[] = [];
  const messagerie: Messagerie = assemble.messagerie;
  messagerie.envoyer = async (m) => void emails.push(m);

  // Stripe : on intercepte la création de session (aucun appel réseau).
  const stripe = new Stripe('sk_test_cle_factice');
  const sessions: any[] = [];
  if (assemble.paiement instanceof FournisseurStripe) {
    (assemble.paiement as any).stripe = stripe;
    vi.spyOn(stripe.checkout.sessions, 'create').mockImplementation((async (params: any, opts: any) => {
      const s = { id: `cs_test_${sessions.length + 1}`, url: `https://checkout.stripe.com/c/pay/cs_test_${sessions.length + 1}`, params, opts };
      sessions.push(s);
      return s;
    }) as any);
  }

  /** Construit un webhook Stripe correctement signé, comme Stripe l'enverrait. */
  function webhook(type: string, session: Record<string, unknown>, id = `evt_${Math.random().toString(36).slice(2)}`) {
    const corps = JSON.stringify({ id, object: 'event', type, data: { object: { object: 'checkout.session', ...session } } });
    const signature = stripe.webhooks.generateTestHeaderString({ payload: corps, secret: SECRET_WEBHOOK });
    return { corps, signature };
  }

  return { ...assemble, config, dir, emails, sessions, webhook, stockage, fichierCatalogue };
}
