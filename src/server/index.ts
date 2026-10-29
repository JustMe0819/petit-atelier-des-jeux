import { chargerConfig, ErreurConfiguration } from './config';
import { assembler } from './demarrage';

try {
  const config = chargerConfig();
  const { app, messagerie, catalogue, db } = assembler(config);
  db.prete().catch(() => console.error('  ⚠️  Base de données injoignable : vérifiez TURSO_DATABASE_URL et TURSO_AUTH_TOKEN.'));
  const publies = catalogue.tous().filter((p) => catalogue.estAchetable(p.id)).length;
  app.listen(config.port, () => {
    const modes: Record<string, string> = {
      simulation: 'SIMULATION (aucun paiement réel — développement uniquement)',
      stripe_test: 'Stripe — MODE TEST (cartes de test, aucun argent réel)',
      stripe_live: 'Stripe — MODE RÉEL (paiements encaissés)',
      non_configure: 'désactivé (PAIEMENT_MODE non configuré)',
    };
    console.info(`\n  Petit Atelier des Jeux — serveur prêt sur http://localhost:${config.port}`);
    console.info(`  Paiement : ${modes[config.paiement.mode]}`);
    const emails = { smtp: 'envoi SMTP', fichiers_locaux: 'écrits dans data/boite-envoi (SMTP non configuré)', non_configuree: 'NON ENVOYÉS (SMTP non configuré)' };
    console.info(`  E-mails  : ${emails[messagerie.type]}`);
    console.info(`  Base     : ${config.baseDeDonnees.distante ? 'Turso (en ligne)' : config.baseDeDonnees.url}`);
    console.info(`  Produits en vente : ${publies}${publies === 0 ? ' — aucun produit publié (voir « npm run catalogue -- liste »)' : ''}\n`);
    if (config.production && messagerie.type !== 'smtp') console.warn('  ⚠️  Production sans SMTP : les clients ne recevront pas leurs e-mails.');
  });
} catch (e) {
  if (e instanceof ErreurConfiguration) {
    console.error(`\n  Configuration invalide : ${e.message}\n`);
    process.exit(1);
  }
  throw e;
}
