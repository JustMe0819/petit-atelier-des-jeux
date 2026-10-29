/**
 * Gestion du catalogue en ligne de commande (en attendant une interface d'administration).
 *   npm run catalogue -- liste
 *   npm run catalogue -- publier <id> --relu-par "Prénom"
 *   npm run catalogue -- depublier <id>
 *   npm run catalogue -- prix <id> <euros>        ex. 4.90
 *   npm run catalogue -- verifier
 */
import fs from 'node:fs';
import path from 'node:path';
import { Catalogue } from '../catalogue';
import { formatPrix } from '../../shared/format';

const racine = process.cwd();
const FICHIER = path.resolve(racine, process.env.FICHIER_CATALOGUE ?? 'catalogue/catalogue.json');
const STOCKAGE = path.resolve(racine, process.env.DOSSIER_FICHIERS ?? 'storage');

const lire = () => JSON.parse(fs.readFileSync(FICHIER, 'utf8'));
const ecrire = (d: unknown) => fs.writeFileSync(FICHIER, JSON.stringify(d, null, 2) + '\n');
const stop = (m: string): never => {
  console.error(`✗ ${m}`);
  process.exit(1);
};

const [commande, ...args] = process.argv.slice(2);
const option = (nom: string) => {
  const i = args.indexOf(nom);
  return i >= 0 ? args[i + 1] : undefined;
};

function produit(d: any, id: string) {
  return d.produits.find((p: any) => p.id === id) ?? stop(`Produit inconnu : ${id}`);
}

switch (commande) {
  case 'liste': {
    const cat = new Catalogue(FICHIER, STOCKAGE);
    console.log('\nStatut            En vente  Prix     Contenu réel        Identifiant');
    for (const p of cat.tous()) {
      const contenu = p.contenu.nb_pages ? `${p.contenu.nb_pages} p. / ${p.contenu.nb_jeux ?? '-'} jeux` : 'non généré';
      console.log(`${p.statut.padEnd(18)}${(cat.estAchetable(p.id) ? 'oui' : 'non').padEnd(10)}${formatPrix(p.prix_centimes).padEnd(9)}${contenu.padEnd(20)}${p.id}`);
    }
    console.log('');
    break;
  }
  case 'publier': {
    const id = args[0] ?? stop('Précisez l’identifiant du produit.');
    const reluPar = option('--relu-par') ?? stop('Indiquez qui a relu le PDF : --relu-par "Prénom". La publication suppose une relecture humaine complète.');
    const d = lire();
    const p = produit(d, id);
    if (p.composants.length > 0) {
      for (const c of p.composants) {
        if (produit(d, c).statut !== 'publie') stop(`Le coffret contient « ${c} », qui n'est pas encore publié.`);
      }
    } else {
      if (p.statut !== 'en_verification') stop(`Le produit est « ${p.statut} ». Il doit d'abord être généré et passer les contrôles (statut en_verification).`);
      if (!p.qa?.valide_automatiquement) stop('Les contrôles automatiques ne sont pas validés (voir le rapport qualité).');
      for (const k of ['pdf', 'corriges', 'encre_eco']) {
        if (p.fichiers[k] && !fs.existsSync(path.join(STOCKAGE, p.fichiers[k]))) stop(`Fichier manquant : storage/${p.fichiers[k]}`);
      }
      if (!p.fichiers.pdf) stop('Aucun fichier PDF associé.');
    }
    p.statut = 'publie';
    p.qa = { ...p.qa, relu_par: reluPar, relu_le: new Date().toISOString() };
    ecrire(d);
    console.log(`✓ « ${p.titre} » est publié et peut être acheté.`);
    break;
  }
  case 'depublier': {
    const d = lire();
    const p = produit(d, args[0] ?? stop('Précisez l’identifiant.'));
    p.statut = p.composants.length > 0 ? 'brouillon' : 'en_verification';
    for (const autre of d.produits) {
      if (autre.composants.includes(p.id) && autre.statut === 'publie') {
        autre.statut = 'brouillon';
        console.log(`  (le coffret « ${autre.titre} » est aussi retiré de la vente)`);
      }
    }
    ecrire(d);
    console.log(`✓ « ${p.titre} » est retiré de la vente (les clients ayant acheté gardent leur accès).`);
    break;
  }
  case 'prix': {
    const d = lire();
    const p = produit(d, args[0] ?? stop('Précisez l’identifiant.'));
    const euros = Number(String(args[1] ?? '').replace(',', '.'));
    if (!Number.isFinite(euros) || euros < 0.5 || euros > 500) stop('Prix invalide (entre 0,50 € et 500 €).');
    p.prix_centimes = Math.round(euros * 100);
    ecrire(d);
    console.log(`✓ Nouveau prix de « ${p.titre} » : ${formatPrix(p.prix_centimes)}`);
    break;
  }
  case 'verifier': {
    new Catalogue(FICHIER, STOCKAGE);
    console.log('✓ Le catalogue est valide.');
    break;
  }
  default:
    console.log('Commandes : liste | publier <id> --relu-par "Prénom" | depublier <id> | prix <id> <euros> | verifier');
}
