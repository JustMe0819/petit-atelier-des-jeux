// Lance une DÉMONSTRATION locale : copie du catalogue où tout est « publié », paiement simulé.
// Le vrai catalogue n'est pas modifié. Usage : npm run build && npm run demo  → http://localhost:8787
import fs from 'node:fs';
import { spawn } from 'node:child_process';

fs.mkdirSync('data/demo', { recursive: true });
const cat = JSON.parse(fs.readFileSync('catalogue/catalogue.json', 'utf8'));
for (const p of cat.produits) p.statut = 'publie';
fs.writeFileSync('data/demo/catalogue.json', JSON.stringify(cat, null, 2));
console.log('Démonstration : tous les produits sont affichés comme publiés (copie dans data/demo/).');
spawn(process.execPath, ['--import', 'tsx', 'src/server/index.ts'], {
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'development', PORT: '8787', URL_PUBLIQUE: 'http://localhost:8787', PAIEMENT_MODE: 'simulation', FICHIER_CATALOGUE: 'data/demo/catalogue.json', DOSSIER_DONNEES: 'data/demo' },
});
