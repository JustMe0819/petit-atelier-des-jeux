// Regroupe le serveur (TypeScript) en un seul fichier JavaScript pour la fonction Vercel.
// Les dépendances (express, stripe…) restent dans node_modules : Vercel les embarque automatiquement.
import { build } from 'esbuild';

await build({
  entryPoints: ['src/server/vercel.ts'],
  outfile: 'build-serveur/serveur.mjs',
  bundle: true,
  platform: 'node',
  format: 'esm',
  target: 'node22',
  packages: 'external',
  sourcemap: false,
  logLevel: 'info',
});
