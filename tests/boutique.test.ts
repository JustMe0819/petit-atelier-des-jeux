import { randomUUID } from 'node:crypto';
import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { boutiqueDeTest } from './outils';

const commandeValide = (produits: string[], cle = randomUUID()) => ({
  produits, email: 'Parent@Exemple.fr', accepteCgv: true, renonceRetractation: true, cleIdempotence: cle,
});

async function creerEtPayer(t: ReturnType<typeof boutiqueDeTest>, produits = ['a']) {
  const r = await request(t.app).post('/api/commandes').send(commandeValide(produits)).expect(200);
  const session = t.sessions.at(-1);
  const succes = new URL(session.params.success_url);
  const jeton = succes.searchParams.get('t')!;
  const total = session.params.line_items.reduce((s: number, l: any) => s + l.price_data.unit_amount, 0);
  const wh = t.webhook('checkout.session.completed', {
    id: session.id, payment_status: 'paid', amount_total: total, amount_subtotal: total, currency: 'eur',
    metadata: { commande_id: r.body.commandeId }, payment_intent: 'pi_123',
  });
  await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps).expect(200);
  return { commandeId: r.body.commandeId as string, jeton, session };
}

describe('Catalogue', () => {
  it("n'expose aucun chemin de fichier et indique la disponibilité réelle", async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).get('/api/catalogue').expect(200);
    expect(JSON.stringify(r.body)).not.toContain('produits/a/a.pdf');
    const dispo = Object.fromEntries(r.body.produits.map((p: any) => [p.id, p.disponible]));
    expect(dispo).toMatchObject({ a: true, b: true, brouillon: false, coffret: true, evasion: false });
  });
});

describe('Création de commande', () => {
  it('recalcule les prix côté serveur et ignore tout prix envoyé par le navigateur', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send({ ...commandeValide(['a', 'b']), prix: 1, total: 1 }).expect(200);
    expect(r.body.url).toMatch(/^https:\/\/checkout\.stripe\.com/);
    const items = t.sessions[0].params.line_items;
    expect(items.map((l: any) => l.price_data.unit_amount)).toEqual([390, 490]);
    expect(t.sessions[0].params.customer_email).toBe('parent@exemple.fr');
    expect(t.sessions[0].params.metadata.commande_id).toBe(r.body.commandeId);
  });

  it('refuse un produit non publié ou inconnu', async () => {
    const t = boutiqueDeTest();
    await request(t.app).post('/api/commandes').send(commandeValide(['brouillon'])).expect(409);
    await request(t.app).post('/api/commandes').send(commandeValide(['inexistant'])).expect(409);
    expect(t.sessions).toHaveLength(0);
  });

  it('exige les CGV et le consentement à l’exécution immédiate', async () => {
    const t = boutiqueDeTest();
    const r1 = await request(t.app).post('/api/commandes').send({ ...commandeValide(['a']), accepteCgv: false }).expect(400);
    expect(r1.body.code).toBe('CGV_REQUISES');
    const r2 = await request(t.app).post('/api/commandes').send({ ...commandeValide(['a']), renonceRetractation: false }).expect(400);
    expect(r2.body.code).toBe('CONSENTEMENT_REQUIS');
  });

  it('valide les données (e-mail, panier vide, quantités)', async () => {
    const t = boutiqueDeTest();
    await request(t.app).post('/api/commandes').send({ ...commandeValide(['a']), email: 'pas-un-email' }).expect(400);
    await request(t.app).post('/api/commandes').send(commandeValide([])).expect(400);
    // Les doublons sont fusionnés : un produit numérique ne s'achète qu'une fois.
    await request(t.app).post('/api/commandes').send(commandeValide(['a', 'a', 'a'])).expect(200);
    expect(t.sessions[0].params.line_items).toHaveLength(1);
    expect(t.sessions[0].params.line_items[0].quantity).toBe(1);
  });

  it('refuse un produit déjà inclus dans le coffret du même panier', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['coffret', 'a'])).expect(409);
    expect(r.body.code).toBe('DEJA_DANS_COFFRET');
  });

  it('ne crée pas de commande en double si la même tentative est renvoyée (double clic, rafraîchissement)', async () => {
    const t = boutiqueDeTest();
    const cle = randomUUID();
    const r1 = await request(t.app).post('/api/commandes').send(commandeValide(['a'], cle)).expect(200);
    const r2 = await request(t.app).post('/api/commandes').send(commandeValide(['a'], cle)).expect(200);
    expect(r2.body.commandeId).toBe(r1.body.commandeId);
    expect(t.sessions).toHaveLength(1);
    const n = (await t.db.get('SELECT COUNT(*) n FROM commandes')) as any;
    expect(n.n).toBe(1);
    // Même clé mais panier différent : refusé.
    await request(t.app).post('/api/commandes').send(commandeValide(['b'], cle)).expect(409);
  });

  it('répond 503 si le paiement n’est pas configuré', async () => {
    const t = boutiqueDeTest({ mode: 'desactive' });
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(503);
    expect(r.body.code).toBe('PAIEMENT_NON_CONFIGURE');
  });
});

describe('Webhook de paiement', () => {
  it('refuse un webhook non signé ou falsifié', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    const wh = t.webhook('checkout.session.completed', { id: 'cs_test_1', payment_status: 'paid', amount_total: 390, currency: 'eur', metadata: { commande_id: r.body.commandeId } });
    await request(t.app).post('/api/paiement/webhook').set('content-type', 'application/json').send(wh.corps).expect(400);
    const falsifie = wh.corps.replace('390', '1');
    await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(falsifie).expect(400);
    const c = (await t.db.get('SELECT statut FROM commandes WHERE id = ?', r.body.commandeId)) as any;
    expect(c.statut).toBe('en_attente');
  });

  it('confirme la commande et envoie un seul e-mail, même si Stripe renvoie l’événement', async () => {
    const t = boutiqueDeTest();
    const { commandeId, session } = await creerEtPayer(t);
    const c = (await t.db.get('SELECT * FROM commandes WHERE id = ?', commandeId)) as any;
    expect(c.statut).toBe('payee');
    expect(c.reference_paiement).toBe('pi_123');
    expect(t.emails).toHaveLength(1);
    expect(t.emails[0].texte).toContain('L221-28');
    // Rejeu du même type d'événement (nouvel id) et du même id : pas de second e-mail.
    const wh = t.webhook('checkout.session.completed', { id: session.id, payment_status: 'paid', amount_total: 390, currency: 'eur', metadata: { commande_id: commandeId } }, 'evt_rejeu');
    for (let i = 0; i < 2; i++) {
      await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps).expect(200);
    }
    expect(t.emails).toHaveLength(1);
  });

  it('traite une seule fois un même événement reçu deux fois en même temps', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    const wh = t.webhook('checkout.session.completed', { id: 'cs_test_1', payment_status: 'paid', amount_total: 390, amount_subtotal: 390, currency: 'eur', metadata: { commande_id: r.body.commandeId } }, 'evt_double');
    const envoi = () => request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps);
    const [a, b] = await Promise.all([envoi(), envoi()]);
    expect([a.body.resultat, b.body.resultat].sort()).toEqual(['deja_traite', 'traite']);
    expect(t.emails).toHaveLength(1);
  });

  it('met la commande en anomalie si le montant payé ne correspond pas', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    const wh = t.webhook('checkout.session.completed', { id: 'cs_test_1', payment_status: 'paid', amount_total: 100, amount_subtotal: 100, currency: 'eur', metadata: { commande_id: r.body.commandeId } });
    await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps).expect(200);
    const c = (await t.db.get('SELECT statut FROM commandes WHERE id = ?', r.body.commandeId)) as any;
    expect(c.statut).toBe('anomalie');
    expect(t.emails).toHaveLength(0);
  });

  it('accepte une réduction Stripe seulement si les codes promo sont activés (contrôle sur le sous-total)', async () => {
    const t = boutiqueDeTest({ codesPromo: true });
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    expect(t.sessions[0].params.allow_promotion_codes).toBe(true);
    const wh = t.webhook('checkout.session.completed', { id: 'cs_test_1', payment_status: 'paid', amount_total: 300, amount_subtotal: 390, currency: 'eur', metadata: { commande_id: r.body.commandeId } });
    await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps).expect(200);
    expect(((await t.db.get('SELECT statut, montant_paye_centimes m FROM commandes')) as any)).toEqual({ statut: 'payee', m: 300 });
  });

  it('gère les paiements différés, les échecs et les sessions expirées', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    const id = r.body.commandeId;
    const statut = async () => ((await t.db.get('SELECT statut FROM commandes WHERE id = ?', id)) as any).statut;
    const envoyer = async (type: string, extra: any = {}) => {
      const wh = t.webhook(type, { id: 'cs_test_1', amount_total: 390, amount_subtotal: 390, currency: 'eur', metadata: { commande_id: id }, ...extra });
      await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps).expect(200);
    };
    await envoyer('checkout.session.completed', { payment_status: 'unpaid' });
    expect(await statut()).toBe('en_attente');
    await envoyer('checkout.session.async_payment_failed');
    expect(await statut()).toBe('echouee');

    const r2 = await request(t.app).post('/api/commandes').send(commandeValide(['b'])).expect(200);
    const wh = t.webhook('checkout.session.expired', { id: 'cs_test_2', metadata: { commande_id: r2.body.commandeId } });
    await request(t.app).post('/api/paiement/webhook').set('stripe-signature', wh.signature).set('content-type', 'application/json').send(wh.corps).expect(200);
    expect(((await t.db.get('SELECT statut FROM commandes WHERE id = ?', r2.body.commandeId)) as any).statut).toBe('expiree');
    expect(t.emails).toHaveLength(0);
  });
});

describe('Accès aux fichiers', () => {
  it('ne donne aucun lien tant que le paiement n’est pas confirmé', async () => {
    const t = boutiqueDeTest();
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    const jeton = new URL(t.sessions[0].params.success_url).searchParams.get('t');
    const resume = await request(t.app).get(`/api/commandes/${r.body.commandeId}?t=${jeton}`).expect(200);
    expect(resume.body.statut).toBe('en_attente');
    expect(resume.body.telechargements).toEqual([]);
  });

  it('refuse la page de commande sans le bon jeton', async () => {
    const t = boutiqueDeTest();
    const { commandeId } = await creerEtPayer(t);
    await request(t.app).get(`/api/commandes/${commandeId}`).expect(403);
    await request(t.app).get(`/api/commandes/${commandeId}?t=mauvais`).expect(403);
  });

  it('télécharge les fichiers achetés via des liens signés', async () => {
    const t = boutiqueDeTest();
    const { commandeId, jeton } = await creerEtPayer(t);
    const resume = await request(t.app).get(`/api/commandes/${commandeId}?t=${jeton}`).expect(200);
    expect(resume.body.statut).toBe('payee');
    const fichiers = resume.body.telechargements[0].fichiers;
    expect(fichiers.map((f: any) => f.type)).toEqual(['pdf', 'corriges']);
    const dl = await request(t.app).get(fichiers[0].url).expect(200);
    expect(dl.headers['content-disposition']).toContain('a.pdf');
    expect(dl.headers['cache-control']).toContain('no-store');
    expect(Buffer.from(dl.body).toString()).toContain('produit A');
  });

  it('refuse un produit non acheté même avec un lien bien formé, et les liens modifiés', async () => {
    const t = boutiqueDeTest();
    const { commandeId, jeton } = await creerEtPayer(t, ['a']);
    const resume = await request(t.app).get(`/api/commandes/${commandeId}?t=${jeton}`).expect(200);
    const url: string = resume.body.telechargements[0].fichiers[0].url;
    const [corps, sig] = url.split('/').pop()!.split('.');
    const charge = JSON.parse(Buffer.from(corps, 'base64url').toString());
    const modifie = Buffer.from(JSON.stringify({ ...charge, p: 'b' })).toString('base64url');
    const r = await request(t.app).get(`/api/telechargements/${modifie}.${sig}`).expect(302);
    expect(r.headers.location).toContain('lien_invalide');
    // Lien signé avec le vrai secret mais pour un produit non acheté.
    const { signerLien } = await import('../src/server/securite');
    const forge = signerLien({ c: commandeId, p: 'b', f: 'pdf', e: Date.now() + 60_000 }, t.config.secretLiens);
    const r2 = await request(t.app).get(`/api/telechargements/${forge}`).expect(302);
    expect(r2.headers.location).toContain('introuvable');
  });

  it('les fichiers privés ne sont pas servis comme fichiers statiques', async () => {
    const t = boutiqueDeTest();
    await request(t.app).get('/storage/produits/a/a.pdf').expect(404);
    await request(t.app).get('/produits/a/a.pdf').expect(404);
  });

  it('les liens expirent et la page de commande l’indique', async () => {
    const t = boutiqueDeTest();
    const { commandeId, jeton } = await creerEtPayer(t);
    const resume = await request(t.app).get(`/api/commandes/${commandeId}?t=${jeton}`).expect(200);
    const url = resume.body.telechargements[0].fichiers[0].url;
    const avance = Date.now() + 31 * 86_400_000;
    (t.boutique as any).maintenant = () => avance;
    const r = await request(t.app).get(url).expect(302);
    expect(r.headers.location).toContain('lien_expire');
    const r2 = await request(t.app).get(`/api/commandes/${commandeId}?t=${jeton}`).expect(410);
    expect(r2.body.code).toBe('LIEN_EXPIRE');
  });

  it('un coffret donne accès aux fichiers de tous ses produits', async () => {
    const t = boutiqueDeTest();
    const { commandeId, jeton } = await creerEtPayer(t, ['coffret']);
    const resume = await request(t.app).get(`/api/commandes/${commandeId}?t=${jeton}`).expect(200);
    expect(resume.body.telechargements.map((x: any) => x.produitId)).toEqual(['a', 'b']);
  });

  it('ne sort jamais du dossier privé (protection « ../ »)', () => {
    const t = boutiqueDeTest();
    expect(t.catalogue.fichiersLivres('evasion')).toEqual([]);
    expect(t.catalogue.estAchetable('evasion')).toBe(false);
  });

  it('renouvelle l’accès par e-mail sans révéler si une adresse existe', async () => {
    const t = boutiqueDeTest();
    await creerEtPayer(t);
    const inconnu = await request(t.app).post('/api/acces/renouveler').send({ email: 'inconnu@exemple.fr' }).expect(200);
    const connu = await request(t.app).post('/api/acces/renouveler').send({ email: 'PARENT@exemple.fr' }).expect(200);
    expect(inconnu.body).toEqual(connu.body);
    expect(t.emails).toHaveLength(2); // confirmation + renouvellement
    const lien = t.emails[1].texte.match(/http:\/\/boutique\.test\/commande\/\S+/)![0];
    const u = new URL(lien);
    await request(t.app).get(`/api/commandes/${u.pathname.split('/').pop()}?t=${u.searchParams.get('t')}`).expect(200);
  });
});

describe('Simulation (développement)', () => {
  it('suit le même chemin que le webhook et n’existe pas en mode Stripe', async () => {
    const t = boutiqueDeTest({ mode: 'simulation' });
    const r = await request(t.app).post('/api/commandes').send(commandeValide(['a'])).expect(200);
    expect(r.body.url).toContain('/paiement-simule/');
    const jeton = new URL(r.body.url).searchParams.get('t');
    await request(t.app).post(`/api/simulation/${r.body.commandeId}/succes`).send({ t: 'faux' }).expect(403);
    await request(t.app).post(`/api/simulation/${r.body.commandeId}/succes`).send({ t: jeton }).expect(200);
    const resume = await request(t.app).get(`/api/commandes/${r.body.commandeId}?t=${jeton}`).expect(200);
    expect(resume.body.statut).toBe('payee');
    const s = boutiqueDeTest();
    await request(s.app).post('/api/simulation/x/succes').send({}).expect(404);
  });
});

describe('Configuration', () => {
  it('refuse la simulation et un secret faible en production, et une clé live hors production', async () => {
    const { chargerConfig } = await import('../src/server/config');
    expect(() => chargerConfig({ NODE_ENV: 'production', SECRET_LIENS: 'x'.repeat(40), PAIEMENT_MODE: 'simulation' } as any)).toThrow(/interdit/);
    expect(() => chargerConfig({ NODE_ENV: 'production', SECRET_LIENS: 'court' } as any)).toThrow(/SECRET_LIENS/);
    expect(() => chargerConfig({ NODE_ENV: 'development', PAIEMENT_MODE: 'stripe', STRIPE_SECRET_KEY: 'sk_live_abc', STRIPE_WEBHOOK_SECRET: 'whsec_x' } as any)).toThrow(/LIVE/);
    expect(() => chargerConfig({ PAIEMENT_MODE: 'stripe', STRIPE_SECRET_KEY: 'sk_test_abc' } as any)).toThrow(/WEBHOOK/);
  });

  it('exige une base Turso (avec son jeton) en production', async () => {
    const { chargerConfig } = await import('../src/server/config');
    const base = { NODE_ENV: 'production', SECRET_LIENS: 'x'.repeat(40), PAIEMENT_MODE: 'desactive' };
    expect(() => chargerConfig(base as any)).toThrow(/TURSO_DATABASE_URL/);
    expect(() => chargerConfig({ ...base, TURSO_DATABASE_URL: 'libsql://boutique.turso.io' } as any)).toThrow(/TURSO_AUTH_TOKEN/);
    const c = chargerConfig({ ...base, TURSO_DATABASE_URL: 'libsql://boutique.turso.io', TURSO_AUTH_TOKEN: 'jeton' } as any);
    expect(c.baseDeDonnees).toEqual({ url: 'libsql://boutique.turso.io', authToken: 'jeton', distante: true });
    const v = chargerConfig({ ...base, TURSO_DATABASE_URL: 'file:x.db', VERCEL_PROJECT_PRODUCTION_URL: 'boutique.vercel.app' } as any);
    expect(v.urlPublique).toBe('https://boutique.vercel.app');
  });
});

describe('Formulaires', () => {
  it('newsletter : la route n’existe plus', async () => {
    const t = boutiqueDeTest();
    await request(t.app).post('/api/newsletter').send({ email: 'a@b.fr', consentement: true }).expect(404);
  });

  it('contact : validation et champ piège anti-robots', async () => {
    const t = boutiqueDeTest();
    await request(t.app).post('/api/contact').send({ nom: 'A', email: 'a@b.fr', sujet: 'autre', message: 'court' }).expect(400);
    await request(t.app).post('/api/contact').send({ nom: 'Camille', email: 'a@b.fr', sujet: 'impression', message: 'Bonjour, une question sur le papier.' }).expect(200);
    expect(t.emails[0].repondreA).toBe('a@b.fr');
  });
});
