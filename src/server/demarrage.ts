import fs from 'node:fs';
import path from 'node:path';
import { Boutique } from './boutique';
import { Catalogue } from './catalogue';
import type { Config } from './config';
import { ouvrirDb } from './db';
import { messagerieFichiers, messagerieJournal, messagerieSmtp } from './emails';
import { FournisseurSimulation, FournisseurStripe, type FournisseurPaiement } from './paiement';
import { creerApp } from './app';

/** Assemble toutes les briques à partir de la configuration. */
export function assembler(config: Config, options: { racine?: string } = {}) {
  const racine = options.racine ?? process.cwd();
  const catalogue = new Catalogue(config.fichierCatalogue, config.dossierFichiers);
  if (config.baseDeDonnees.url.startsWith('file:')) fs.mkdirSync(config.dossierDonnees, { recursive: true });
  const db = ouvrirDb(config.baseDeDonnees);
  // En ligne, le disque n'est pas modifiable : sans SMTP, les e-mails sont seulement signalés dans les journaux.
  const messagerie = config.email.smtp
    ? messagerieSmtp(config.email.smtp, config.email.expediteur)
    : config.production || config.vercel
      ? messagerieJournal()
      : messagerieFichiers(path.join(config.dossierDonnees, 'boite-envoi'));

  let paiement: FournisseurPaiement | null = null;
  if (config.paiement.mode === 'simulation') paiement = new FournisseurSimulation(config.urlPublique);
  if (config.paiement.mode === 'stripe_test' || config.paiement.mode === 'stripe_live') {
    paiement = FournisseurStripe.depuisCles(config.paiement.mode, config.paiement.stripeSecretKey!, config.paiement.stripeWebhookSecret!, config.paiement.codesPromo);
  }
  const boutique = new Boutique(db, catalogue, paiement, messagerie, config);
  const app = creerApp({ config, catalogue, boutique, paiement, messagerie, dossierSite: path.join(racine, 'dist') });
  return { app, db, catalogue, boutique, messagerie, paiement };
}
