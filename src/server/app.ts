import fs from 'node:fs';
import path from 'node:path';
import express, { type NextFunction, type Request, type Response } from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { z } from 'zod';
import type { Catalogue } from './catalogue';
import type { Config } from './config';
import { Boutique, ErreurMetier } from './boutique';
import { emailContact, type Messagerie } from './emails';
import { ErreurSignature, type FournisseurPaiement } from './paiement';
import type { StatutServeur } from '../shared/types';

export interface Dependances {
  config: Config;
  catalogue: Catalogue;
  boutique: Boutique;
  paiement: FournisseurPaiement | null;
  messagerie: Messagerie;
  /** Dossier du site compilé (production). */
  dossierSite?: string;
}

const limiteur = (max: number, fenetreMinutes: number) =>
  rateLimit({
    windowMs: fenetreMinutes * 60_000,
    limit: max,
    standardHeaders: 'draft-8',
    legacyHeaders: false,
    message: { code: 'TROP_DE_REQUETES', message: 'Trop de demandes. Merci de patienter quelques minutes.' },
  });

const schemaCommande = z.object({
  produits: z.array(z.string().max(80)).min(1).max(20),
  email: z.string().trim().email('Adresse e-mail invalide.').max(254),
  accepteCgv: z.boolean(),
  renonceRetractation: z.boolean(),
  cleIdempotence: z.string().uuid(),
});

const schemaEmail = z.object({ email: z.string().trim().email('Adresse e-mail invalide.').max(254) });

const schemaContact = z.object({
  nom: z.string().trim().min(1, 'Indiquez votre nom.').max(100),
  email: z.string().trim().email('Adresse e-mail invalide.').max(254),
  sujet: z.enum(['commande', 'impression', 'pedagogie', 'autre']),
  message: z.string().trim().min(10, 'Votre message est un peu court.').max(5000),
  site: z.string().max(0).optional(), // champ piège anti-robots, doit rester vide
});

const SUJETS: Record<string, string> = { commande: 'Question sur une commande', impression: "Conseil d'impression", pedagogie: 'Question pédagogique', autre: 'Autre demande' };

export function creerApp(d: Dependances) {
  const app = express();
  app.disable('x-powered-by');
  app.set('trust proxy', 1);
  app.use(
    helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          imgSrc: ["'self'", 'data:'],
          styleSrc: ["'self'", "'unsafe-inline'"],
          fontSrc: ["'self'", 'data:'],
          scriptSrc: ["'self'"],
          connectSrc: ["'self'"],
          formAction: ["'self'", 'https://checkout.stripe.com'],
          frameAncestors: ["'none'"],
        },
      },
    }),
  );

  // Webhook Stripe : AVANT express.json(), car la signature se vérifie sur le corps brut.
  app.post('/api/paiement/webhook', express.raw({ type: 'application/json', limit: '1mb' }), async (req, res) => {
    if (!d.paiement || d.paiement.mode === 'simulation') return res.status(404).end();
    if (!Buffer.isBuffer(req.body)) {
      // Le corps a déjà été lu par l'hébergeur : la signature ne peut pas être vérifiée.
      console.error('[webhook] corps brut indisponible (sur Vercel, ajoutez la variable NODEJS_HELPERS=0).');
      return res.status(400).json({ code: 'CORPS_BRUT_INDISPONIBLE' });
    }
    try {
      const evt = d.paiement.lireWebhook(req.body, req.header('stripe-signature'));
      const r = await d.boutique.traiterEvenement(evt);
      res.json({ recu: true, resultat: r });
    } catch (e) {
      if (e instanceof ErreurSignature) {
        console.warn('[webhook] signature refusée :', e.message);
        return res.status(400).json({ code: 'SIGNATURE_INVALIDE' });
      }
      console.error('[webhook] erreur de traitement', e);
      res.status(500).json({ code: 'ERREUR' }); // Stripe renverra l'événement plus tard
    }
  });

  app.use(express.json({ limit: '20kb' }));

  // ------------------------------------------------------------ API publique
  app.get('/api/statut', (_req, res) => {
    const s: StatutServeur = { paiement: d.config.paiement.mode, emails: d.messagerie.type, production: d.config.production };
    res.json(s);
  });

  app.get('/api/catalogue', (_req, res) => {
    res.set('Cache-Control', 'no-cache');
    res.json(d.catalogue.reponsePublique());
  });

  app.post('/api/commandes', limiteur(20, 15), async (req, res, next) => {
    try {
      const entree = schemaCommande.parse(req.body);
      res.json(await d.boutique.creerCommande(entree));
    } catch (e) {
      next(e);
    }
  });

  app.get('/api/commandes/:id', limiteur(120, 5), async (req, res, next) => {
    try {
      res.set('Cache-Control', 'no-store');
      res.json(await d.boutique.resume(String(req.params.id), String(req.query.t ?? '')));
    } catch (e) {
      next(e);
    }
  });

  app.get('/api/telechargements/:jeton', limiteur(60, 5), async (req, res) => {
    try {
      const f = await d.boutique.fichierPourLien(String(req.params.jeton));
      res.set('Cache-Control', 'private, no-store');
      res.set('X-Robots-Tag', 'noindex');
      res.download(f.chemin, f.nom);
    } catch (e) {
      // Navigation directe depuis un lien : on redirige vers une page explicative plutôt que du JSON.
      const raison = e instanceof ErreurMetier ? e.code.toLowerCase() : 'erreur';
      if (!(e instanceof ErreurMetier)) console.error(e);
      res.redirect(302, `/telechargement-impossible?raison=${encodeURIComponent(raison)}`);
    }
  });

  app.post('/api/acces/renouveler', limiteur(5, 60), async (req, res, next) => {
    try {
      const { email } = schemaEmail.parse(req.body);
      await d.boutique.renouvelerAcces(email);
      res.json({ ok: true, message: 'Si une commande payée correspond à cette adresse, un e-mail avec de nouveaux liens vient de partir.' });
    } catch (e) {
      next(e);
    }
  });

  app.post('/api/contact', limiteur(5, 60), async (req, res, next) => {
    try {
      const c = schemaContact.parse(req.body);
      if (c.site) return res.json({ ok: true }); // robot
      const destinataire = d.config.email.boutique ?? (d.messagerie.type === 'fichiers_locaux' ? 'boutique@exemple.invalid' : undefined);
      if (!destinataire) {
        throw new ErreurMetier('CONTACT_NON_CONFIGURE', "Le formulaire n'est pas encore relié à une boîte e-mail. Merci de réessayer plus tard.", 503);
      }
      await d.messagerie.envoyer({ a: destinataire, ...emailContact({ ...c, sujet: SUJETS[c.sujet] }) });
      res.json({ ok: true });
    } catch (e) {
      next(e);
    }
  });

  // Simulation de paiement : n'existe qu'en mode simulation (jamais en production).
  if (d.config.paiement.mode === 'simulation') {
    app.post('/api/simulation/:id/:resultat', async (req, res, next) => {
      try {
        const resultat = req.params.resultat === 'succes' ? 'succes' : 'echec';
        await d.boutique.simuler(String(req.params.id), String(req.body?.t ?? ''), resultat);
        res.json({ ok: true });
      } catch (e) {
        next(e);
      }
    });
  }

  app.use('/api', (_req, res) => res.status(404).json({ code: 'INTROUVABLE', message: 'Route inconnue.' }));

  // ------------------------------------------------------------ Site compilé (production)
  if (d.dossierSite && fs.existsSync(d.dossierSite)) {
    app.use(express.static(d.dossierSite, { index: false, maxAge: '1h' }));
    const index = path.join(d.dossierSite, 'index.html');
    app.get(/^(?!\/api\/).*/, (_req, res) => res.sendFile(index));
  }

  // ------------------------------------------------------------ Erreurs
  app.use((e: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (e instanceof z.ZodError) {
      return res.status(400).json({ code: 'DONNEES_INVALIDES', message: e.issues[0]?.message ?? 'Données invalides.' });
    }
    if (e instanceof ErreurMetier) return res.status(e.statutHttp).json({ code: e.code, message: e.message });
    if (e instanceof SyntaxError) return res.status(400).json({ code: 'JSON_INVALIDE', message: 'Requête mal formée.' });
    console.error(e);
    res.status(500).json({ code: 'ERREUR_INTERNE', message: 'Une erreur inattendue est survenue. Merci de réessayer.' });
  });

  return app;
}
