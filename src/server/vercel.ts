/**
 * Point d'entrée pour Vercel : le serveur Express devient une fonction Vercel.
 * Ce fichier est regroupé (bundle) par scripts/construire-serveur.mjs lors du déploiement,
 * puis chargé par api/index.mjs. En local, on utilise toujours src/server/index.ts.
 */
import express, { type Request, type Response } from 'express';
import { chargerConfig, ErreurConfiguration } from './config';
import { assembler } from './demarrage';

function creer(): (req: Request, res: Response) => void {
  try {
    const config = chargerConfig();
    if (process.env.NODEJS_HELPERS !== '0') {
      console.warn('[vercel] NODEJS_HELPERS=0 est absent : les webhooks Stripe risquent d’être refusés (voir docs/CONFIGURATION-SERVICES.md).');
    }
    return assembler(config).app;
  } catch (e) {
    // Configuration incomplète : on répond proprement au lieu de faire planter la fonction.
    const message = e instanceof ErreurConfiguration ? e.message : 'Erreur au démarrage du serveur.';
    console.error('[démarrage] ' + message, e instanceof ErreurConfiguration ? '' : e);
    const secours = express();
    secours.use((_req, res) => {
      res.status(503).json({ code: 'SERVICE_INDISPONIBLE', message: 'La boutique est momentanément indisponible. Merci de réessayer plus tard.' });
    });
    return secours;
  }
}

export default creer();
