/**
 * Consultation des commandes (lecture seule) :
 *   npm run commandes -- liste [--statut payee]
 *   npm run commandes -- voir <PAD-XXXX-XXXX>
 * Avec TURSO_DATABASE_URL et TURSO_AUTH_TOKEN dans .env, la commande lit la base en ligne ;
 * sinon, elle lit la base locale data/boutique.sqlite.
 */
import { chargerConfig } from '../config';
import { ouvrirDb } from '../db';
import { formatPrix } from '../../shared/format';

const config = chargerConfig({ ...process.env, NODE_ENV: 'development' });
const db = ouvrirDb(config.baseDeDonnees);
const [commande, ...args] = process.argv.slice(2);
console.info(`Base : ${config.baseDeDonnees.distante ? 'Turso (en ligne)' : config.baseDeDonnees.url}\n`);

if (commande === 'liste') {
  const i = args.indexOf('--statut');
  const statut = i >= 0 ? args[i + 1] : null;
  const lignes = statut
    ? await db.all('SELECT * FROM commandes WHERE statut = ? ORDER BY cree_le DESC LIMIT 200', statut)
    : await db.all('SELECT * FROM commandes ORDER BY cree_le DESC LIMIT 200');
  for (const c of lignes) {
    console.log(`${c.cree_le.slice(0, 16).replace('T', ' ')}  ${c.id}  ${c.statut.padEnd(11)} ${formatPrix(c.total_centimes).padStart(9)}  ${c.mode_paiement.padEnd(12)} ${c.email}`);
  }
  const total = (await db.get("SELECT COUNT(*) n, COALESCE(SUM(total_centimes),0) s FROM commandes WHERE statut = 'payee'"))!;
  console.log(`\n${total.n} commande(s) payée(s) — ${formatPrix(Number(total.s))} au total.`);
} else if (commande === 'voir') {
  const c = await db.get('SELECT * FROM commandes WHERE id = ?', args[0] ?? '');
  if (!c) {
    console.error('Commande introuvable.');
    process.exit(1);
  }
  console.log(c);
  console.log(await db.all('SELECT produit_id, titre, prix_centimes FROM lignes_commande WHERE commande_id = ?', c.id));
  console.log('Téléchargements :', await db.all('SELECT produit_id, type_fichier, le FROM telechargements WHERE commande_id = ?', c.id));
} else {
  console.log('Commandes : liste [--statut payee] | voir <id>');
}
db.close();
