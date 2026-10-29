import fs from 'node:fs';
import type { Catalogue, TypeFichier } from './catalogue';
import { libelleFichier } from './catalogue';
import type { Config } from './config';
import type { Db, Instruction } from './db';
import { emailConfirmationCommande, emailRenouvellement, type Messagerie } from './emails';
import type { EvenementPaiement, FournisseurPaiement } from './paiement';
import { empreinte, masquerEmail, normaliserEmail, nouveauJeton, nouvelIdCommande, signerLien, verifierLien } from './securite';
import { TEXTE_ACCEPTATION_CGV, TEXTE_CONSENTEMENT_RETRACTATION } from '../shared/format';
import type { CommandeResume, StatutCommande } from '../shared/types';

export class ErreurMetier extends Error {
  constructor(public code: string, message: string, public statutHttp = 400) {
    super(message);
  }
}

interface LigneCommandeDb {
  commande_id: string;
  produit_id: string;
  titre: string;
  prix_centimes: number;
}

interface CommandeDb {
  id: string;
  email: string;
  statut: StatutCommande;
  total_centimes: number;
  mode_paiement: string;
  cle_idempotence: string;
  empreinte_panier: string;
  session_paiement: string | null;
  url_paiement: string | null;
  consentement_execution_le: string;
  texte_consentement: string;
  cree_le: string;
  payee_le: string | null;
  email_confirmation_le: string | null;
}

export interface EntreeCommande {
  produits: string[];
  email: string;
  accepteCgv: boolean;
  renonceRetractation: boolean;
  cleIdempotence: string;
}

const MAX_ARTICLES = 20;
const DELAI_REUTILISATION_SESSION_MS = 25 * 60_000;

/**
 * Logique métier de la boutique : commandes, confirmation de paiement, accès aux fichiers.
 * Indépendante d'Express pour être testable directement.
 */
export class Boutique {
  constructor(
    private db: Db,
    private catalogue: Catalogue,
    private paiement: FournisseurPaiement | null,
    private messagerie: Messagerie,
    private config: Config,
    private maintenant: () => number = Date.now,
  ) {}

  private iso(ms = this.maintenant()) {
    return new Date(ms).toISOString();
  }

  private commande(id: string): Promise<CommandeDb | undefined> {
    return this.db.get<CommandeDb>('SELECT * FROM commandes WHERE id = ?', id);
  }

  private lignes(id: string): Promise<LigneCommandeDb[]> {
    return this.db.all<LigneCommandeDb>('SELECT * FROM lignes_commande WHERE commande_id = ? ORDER BY rowid', id);
  }

  /** Prépare un nouveau lien d'accès (le jeton n'est stocké que sous forme d'empreinte). */
  private preparerLienAcces(commandeId: string): { jeton: string; expireLe: string; instruction: Required<Instruction> } {
    const jeton = nouveauJeton();
    const expireLe = this.iso(this.maintenant() + this.config.dureeAccesCommandeMs);
    const instruction = {
      sql: 'INSERT INTO liens_acces (empreinte_jeton, commande_id, expire_le, cree_le) VALUES (?, ?, ?, ?)',
      args: [empreinte(jeton), commandeId, expireLe, this.iso()],
    };
    return { jeton, expireLe, instruction };
  }

  private async creerLienAcces(commandeId: string): Promise<{ jeton: string; expireLe: string }> {
    const l = this.preparerLienAcces(commandeId);
    await this.db.run(l.instruction.sql, ...l.instruction.args);
    return { jeton: l.jeton, expireLe: l.expireLe };
  }

  urlCommande(commandeId: string, jeton: string) {
    return `${this.config.urlPublique}/commande/${encodeURIComponent(commandeId)}?t=${encodeURIComponent(jeton)}`;
  }

  // ------------------------------------------------------------------ Commande

  async creerCommande(entree: EntreeCommande): Promise<{ commandeId: string; url: string }> {
    if (!this.paiement) {
      throw new ErreurMetier('PAIEMENT_NON_CONFIGURE', "Le paiement en ligne n'est pas encore activé sur cette boutique.", 503);
    }
    if (!entree.accepteCgv) throw new ErreurMetier('CGV_REQUISES', 'Vous devez accepter les conditions générales de vente.');
    if (!entree.renonceRetractation) {
      throw new ErreurMetier('CONSENTEMENT_REQUIS', "Votre accord pour l'accès immédiat aux fichiers est nécessaire pour finaliser la commande.");
    }
    const ids = [...new Set(entree.produits)];
    if (ids.length === 0) throw new ErreurMetier('PANIER_VIDE', 'Votre panier est vide.');
    if (ids.length > MAX_ARTICLES) throw new ErreurMetier('PANIER_TROP_GRAND', 'Trop d’articles dans le panier.');

    // Prix recalculés à partir du catalogue serveur : le navigateur n'envoie que des identifiants.
    const produits = ids.map((id) => {
      const p = this.catalogue.trouver(id);
      if (!p || !this.catalogue.estAchetable(p.id)) {
        throw new ErreurMetier('PRODUIT_INDISPONIBLE', `Un produit de votre panier n'est plus disponible${p ? ` (« ${p.titre} »)` : ''}.`, 409);
      }
      return p;
    });
    for (const coffret of produits.filter((p) => p.composants.length > 0)) {
      const doublon = produits.find((p) => coffret.composants.includes(p.id));
      if (doublon) {
        throw new ErreurMetier('DEJA_DANS_COFFRET', `« ${doublon.titre} » est déjà inclus dans « ${coffret.titre} ».`, 409);
      }
    }

    const email = normaliserEmail(entree.email);
    const empreintePanier = empreinte([...produits.map((p) => p.id)].sort().join('|') + '#' + email);

    const existante = await this.db.get<CommandeDb>('SELECT * FROM commandes WHERE cle_idempotence = ?', entree.cleIdempotence);
    if (existante) {
      const recente = this.maintenant() - Date.parse(existante.cree_le) < DELAI_REUTILISATION_SESSION_MS;
      if (existante.empreinte_panier === empreintePanier && existante.statut === 'en_attente' && recente && existante.url_paiement) {
        return { commandeId: existante.id, url: existante.url_paiement };
      }
      throw new ErreurMetier('CLE_REUTILISEE', 'Cette tentative de paiement a déjà été utilisée. Merci de réessayer.', 409);
    }

    const commandeId = nouvelIdCommande();
    const total = produits.reduce((s, p) => s + p.prix_centimes, 0);
    const maintenant = this.iso();
    const lien = this.preparerLienAcces(commandeId);
    const jeton = lien.jeton;
    try {
      await this.db.transaction([
        {
          sql: `INSERT INTO commandes (id, email, statut, total_centimes, mode_paiement, cle_idempotence, empreinte_panier,
                  consentement_cgv_le, consentement_execution_le, texte_consentement, cree_le)
                VALUES (?, ?, 'en_attente', ?, ?, ?, ?, ?, ?, ?, ?)`,
          args: [commandeId, email, total, this.paiement.mode, entree.cleIdempotence, empreintePanier, maintenant, maintenant,
            `${TEXTE_ACCEPTATION_CGV} ${TEXTE_CONSENTEMENT_RETRACTATION}`, maintenant],
        },
        ...produits.map((p) => ({
          sql: 'INSERT INTO lignes_commande (commande_id, produit_id, titre, prix_centimes) VALUES (?, ?, ?, ?)',
          args: [commandeId, p.id, p.titre, p.prix_centimes],
        })),
        lien.instruction,
      ]);
    } catch (e) {
      // Deux requêtes simultanées avec la même clé : la contrainte UNIQUE n'en laisse passer qu'une.
      if (String((e as Error).message).includes('UNIQUE')) {
        throw new ErreurMetier('CLE_REUTILISEE', 'Cette tentative de paiement a déjà été utilisée. Merci de réessayer.', 409);
      }
      throw e;
    }

    try {
      const session = await this.paiement.creerSession({
        commandeId,
        email,
        lignes: produits.map((p) => ({ produitId: p.id, titre: p.titre, prixCentimes: p.prix_centimes })),
        urlSucces: this.urlCommande(commandeId, jeton),
        urlAnnulation: `${this.config.urlPublique}/panier?paiement=annule`,
      });
      await this.db.run('UPDATE commandes SET session_paiement = ?, url_paiement = ? WHERE id = ?', session.id, session.url, commandeId);
      return { commandeId, url: session.url };
    } catch (e) {
      await this.db.run("UPDATE commandes SET statut = 'echouee', note = ? WHERE id = ?", `Création de session impossible : ${(e as Error).message}`, commandeId);
      console.error('[paiement] création de session impossible', e);
      throw new ErreurMetier('PAIEMENT_INDISPONIBLE', 'Le service de paiement ne répond pas. Aucun montant n’a été débité, merci de réessayer dans un instant.', 502);
    }
  }

  // ------------------------------------------------------------------ Événements de paiement

  /** Traite un événement (webhook vérifié). Idempotent : un même événement n'est jamais traité deux fois. */
  async traiterEvenement(evt: EvenementPaiement): Promise<'traite' | 'deja_traite' | 'ignore'> {
    // Insertion atomique : si l'événement est déjà enregistré (même reçu en double, en parallèle), rien n'est modifié.
    const ins = await this.db.run('INSERT OR IGNORE INTO evenements_paiement (id, type, recu_le) VALUES (?, ?, ?)', evt.id, evt.typeOrigine, this.iso());
    if (ins.changes === 0) return 'deja_traite';
    try {
      return await this.appliquerEvenement(evt);
    } catch (e) {
      // Échec inattendu : on oublie l'événement pour que Stripe puisse le renvoyer et qu'il soit retraité.
      await this.db.run('DELETE FROM evenements_paiement WHERE id = ?', evt.id).catch(() => undefined);
      throw e;
    }
  }

  private async appliquerEvenement(evt: EvenementPaiement): Promise<'traite' | 'ignore'> {
    if (evt.type === 'ignore' || evt.type === 'paiement_en_attente') return 'ignore';
    const commande = evt.commandeId ? await this.commande(evt.commandeId) : undefined;
    if (!commande || (evt.sessionId && commande.session_paiement && commande.session_paiement !== evt.sessionId)) {
      console.error(`[paiement] événement ${evt.id} sans commande correspondante (${evt.commandeId ?? '?'})`);
      return 'ignore';
    }
    if (evt.type === 'paiement_reussi') {
      await this.confirmerPaiement(commande.id, evt);
    } else if (evt.type === 'paiement_echoue') {
      await this.db.run("UPDATE commandes SET statut = 'echouee' WHERE id = ? AND statut = 'en_attente'", commande.id);
    } else if (evt.type === 'session_expiree') {
      await this.db.run("UPDATE commandes SET statut = 'expiree' WHERE id = ? AND statut = 'en_attente'", commande.id);
    }
    return 'traite';
  }

  async confirmerPaiement(commandeId: string, evt: Pick<EvenementPaiement, 'montantCentimes' | 'sousTotalCentimes' | 'devise' | 'reference'>) {
    const c = await this.commande(commandeId);
    if (!c) throw new ErreurMetier('COMMANDE_INCONNUE', 'Commande introuvable.', 404);
    if (c.statut === 'payee') return;

    // Contrôle de cohérence : le montant payé doit correspondre au montant calculé par le serveur.
    const montantAttendu = this.config.paiement.codesPromo ? evt.sousTotalCentimes : evt.montantCentimes;
    const deviseOk = (evt.devise ?? 'eur').toLowerCase() === 'eur';
    if (montantAttendu !== c.total_centimes || !deviseOk) {
      await this.db.run("UPDATE commandes SET statut = 'anomalie', note = ? WHERE id = ?",
        `Montant reçu ${evt.montantCentimes} ${evt.devise} (sous-total ${evt.sousTotalCentimes}) ≠ attendu ${c.total_centimes}`, c.id);
      console.error(`[paiement] ANOMALIE de montant sur ${c.id} — vérification manuelle nécessaire`);
      return;
    }
    const maj = await this.db.run(
      "UPDATE commandes SET statut = 'payee', payee_le = ?, reference_paiement = ?, montant_paye_centimes = ? WHERE id = ? AND statut != 'payee'",
      this.iso(), evt.reference ?? null, evt.montantCentimes ?? null, c.id);
    if (Number(maj.changes) === 0) return; // déjà confirmée entre-temps
    await this.envoyerConfirmation(c.id);
  }

  private async envoyerConfirmation(commandeId: string) {
    const c = (await this.commande(commandeId))!;
    const { jeton, expireLe } = await this.creerLienAcces(c.id);
    const msg = emailConfirmationCommande({
      commandeId: c.id,
      lignes: (await this.lignes(c.id)).map((l) => ({ titre: l.titre, prixCentimes: l.prix_centimes })),
      totalCentimes: c.total_centimes,
      lienAcces: this.urlCommande(c.id, jeton),
      accesExpireLe: expireLe,
      consentementLe: c.consentement_execution_le,
      texteConsentement: c.texte_consentement,
      urlSite: this.config.urlPublique,
    });
    try {
      await this.messagerie.envoyer({ a: c.email, ...msg });
      await this.db.run('UPDATE commandes SET email_confirmation_le = ? WHERE id = ?', this.iso(), c.id);
    } catch (e) {
      // Le client garde l'accès via la page de confirmation et peut redemander un lien.
      console.error(`[e-mail] échec d'envoi de la confirmation ${c.id}`, e);
    }
  }

  /** Mode simulation uniquement (développement). */
  async simuler(commandeId: string, jeton: string, resultat: 'succes' | 'echec') {
    if (this.paiement?.mode !== 'simulation') throw new ErreurMetier('INTERDIT', 'Simulation désactivée.', 403);
    if ((await this.verifierAcces(commandeId, jeton)) !== 'ok') throw new ErreurMetier('ACCES_REFUSE', 'Lien invalide.', 403);
    const c = (await this.commande(commandeId))!;
    await this.traiterEvenement({
      id: `sim_evt_${commandeId}_${resultat}`,
      typeOrigine: `simulation.${resultat}`,
      type: resultat === 'succes' ? 'paiement_reussi' : 'paiement_echoue',
      commandeId,
      sessionId: c.session_paiement ?? undefined,
      montantCentimes: c.total_centimes,
      sousTotalCentimes: c.total_centimes,
      devise: 'eur',
      reference: `simulation-${commandeId}`,
    });
  }

  // ------------------------------------------------------------------ Accès aux fichiers

  async verifierAcces(commandeId: string, jeton: string): Promise<'ok' | 'expire' | 'invalide'> {
    if (!jeton) return 'invalide';
    const lien = await this.db.get<{ expire_le: string }>(
      'SELECT * FROM liens_acces WHERE empreinte_jeton = ? AND commande_id = ?', empreinte(jeton), commandeId);
    if (!lien) return 'invalide';
    if (Date.parse(lien.expire_le) < this.maintenant()) return 'expire';
    return 'ok';
  }

  async resume(commandeId: string, jeton: string): Promise<CommandeResume> {
    const acces = await this.verifierAcces(commandeId, jeton);
    if (acces === 'expire') throw new ErreurMetier('LIEN_EXPIRE', 'Ce lien a expiré. Vous pouvez en recevoir un nouveau par e-mail.', 410);
    if (acces !== 'ok') throw new ErreurMetier('ACCES_REFUSE', 'Lien de commande invalide.', 403);
    const c = (await this.commande(commandeId))!;
    const lignes = await this.lignes(c.id);
    const lien = (await this.db.get<{ expire_le: string }>('SELECT expire_le FROM liens_acces WHERE empreinte_jeton = ?', empreinte(jeton)))!;

    const telechargements: CommandeResume['telechargements'] = [];
    let liensExpirentLe: string | null = null;
    if (c.statut === 'payee') {
      const exp = this.maintenant() + this.config.dureeLienTelechargementMs;
      liensExpirentLe = this.iso(exp);
      const vus = new Set<string>();
      for (const l of lignes) {
        for (const f of this.catalogue.fichiersLivres(l.produit_id)) {
          if (!vus.has(f.produitId)) {
            vus.add(f.produitId);
            telechargements.push({ produitId: f.produitId, titre: f.titreProduit, fichiers: [] });
          }
          const groupe = telechargements.find((t) => t.produitId === f.produitId)!;
          if (groupe.fichiers.some((x) => x.type === f.type)) continue;
          groupe.fichiers.push({
            type: f.type,
            libelle: libelleFichier(f.type),
            url: `/api/telechargements/${signerLien({ c: c.id, p: f.produitId, f: f.type, e: exp }, this.config.secretLiens)}`,
            tailleOctets: fs.statSync(f.cheminAbsolu).size,
          });
        }
      }
    }
    return {
      id: c.id,
      statut: c.statut,
      totalCentimes: c.total_centimes,
      emailMasque: masquerEmail(c.email),
      creeLe: c.cree_le,
      payeeLe: c.payee_le,
      lignes: lignes.map((l) => ({ produitId: l.produit_id, titre: l.titre, prixCentimes: l.prix_centimes })),
      consentement: { executionImmediateLe: c.consentement_execution_le, texte: c.texte_consentement },
      telechargements,
      liensExpirentLe,
      accesExpireLe: lien.expire_le,
      modePaiement: c.mode_paiement as CommandeResume['modePaiement'],
    };
  }

  /** Vérifie un lien de téléchargement signé et renvoie le fichier à servir. */
  async fichierPourLien(jetonLien: string): Promise<{ chemin: string; nom: string }> {
    const r = verifierLien(jetonLien, this.config.secretLiens, this.maintenant());
    if (!r.ok) {
      throw r.raison === 'expire'
        ? new ErreurMetier('LIEN_EXPIRE', 'Ce lien de téléchargement a expiré.', 410)
        : new ErreurMetier('LIEN_INVALIDE', 'Lien de téléchargement invalide.', 403);
    }
    const { c: commandeId, p: produitId, f: type } = r.charge;
    const c = await this.commande(commandeId);
    if (!c || c.statut !== 'payee') throw new ErreurMetier('NON_PAYEE', "Cette commande n'est pas réglée.", 403);
    // Le produit demandé doit faire partie de la commande (directement ou via un coffret).
    const fichier = (await this.lignes(c.id))
      .flatMap((l) => this.catalogue.fichiersLivres(l.produit_id))
      .find((f) => f.produitId === produitId && f.type === (type as TypeFichier));
    if (!fichier) throw new ErreurMetier('INTROUVABLE', 'Fichier introuvable pour cette commande.', 404);
    await this.db.run('INSERT INTO telechargements (commande_id, produit_id, type_fichier, le) VALUES (?, ?, ?, ?)', c.id, produitId, type, this.iso());
    return { chemin: fichier.cheminAbsolu, nom: fichier.nomTelechargement };
  }

  /** Envoie de nouveaux liens d'accès pour toutes les commandes payées d'une adresse e-mail. */
  async renouvelerAcces(emailBrut: string): Promise<void> {
    const email = normaliserEmail(emailBrut);
    const commandes = await this.db.all<{ id: string; cree_le: string }>(
      "SELECT id, cree_le FROM commandes WHERE email = ? AND statut = 'payee' ORDER BY cree_le DESC LIMIT 20", email);
    if (commandes.length === 0) return; // Même réponse côté client : on ne révèle pas si l'adresse existe.
    let expireLe = '';
    const liens = [];
    for (const c of commandes) {
      const l = await this.creerLienAcces(c.id);
      expireLe = l.expireLe;
      liens.push({ id: c.id, creeLe: c.cree_le, lien: this.urlCommande(c.id, l.jeton) });
    }
    await this.messagerie.envoyer({ a: email, ...emailRenouvellement({ commandes: liens, expireLe }) });
  }
}
