import Stripe from 'stripe';
import type { ModePaiement } from '../shared/types';

export interface LigneFacturable {
  produitId: string;
  titre: string;
  prixCentimes: number;
}

export interface ParametresSession {
  commandeId: string;
  email: string;
  lignes: LigneFacturable[];
  urlSucces: string;
  urlAnnulation: string;
}

export type TypeEvenement = 'paiement_reussi' | 'paiement_en_attente' | 'paiement_echoue' | 'session_expiree' | 'ignore';

/** Événement de paiement normalisé, indépendant du prestataire. */
export interface EvenementPaiement {
  id: string;
  type: TypeEvenement;
  typeOrigine: string;
  sessionId?: string;
  commandeId?: string;
  montantCentimes?: number;
  sousTotalCentimes?: number;
  devise?: string;
  reference?: string;
}

export interface FournisseurPaiement {
  mode: ModePaiement;
  creerSession(p: ParametresSession): Promise<{ id: string; url: string }>;
  /** Vérifie la signature du webhook et renvoie l'événement. Lève une erreur si la signature est invalide. */
  lireWebhook(corpsBrut: Buffer, signature: string | undefined): EvenementPaiement;
}

export class ErreurSignature extends Error {}

/** Stripe Checkout : la page de paiement est hébergée par Stripe, aucune donnée bancaire ne transite par notre serveur. */
export class FournisseurStripe implements FournisseurPaiement {
  constructor(
    public mode: ModePaiement,
    private stripe: Stripe,
    private secretWebhook: string,
    private codesPromo: boolean,
  ) {}

  static depuisCles(mode: ModePaiement, cleSecrete: string, secretWebhook: string, codesPromo: boolean) {
    return new FournisseurStripe(mode, new Stripe(cleSecrete), secretWebhook, codesPromo);
  }

  async creerSession(p: ParametresSession) {
    const session = await this.stripe.checkout.sessions.create(
      {
        mode: 'payment',
        locale: 'fr',
        customer_email: p.email,
        client_reference_id: p.commandeId,
        metadata: { commande_id: p.commandeId },
        payment_intent_data: { metadata: { commande_id: p.commandeId } },
        line_items: p.lignes.map((l) => ({
          quantity: 1,
          price_data: {
            currency: 'eur',
            unit_amount: l.prixCentimes,
            product_data: { name: l.titre, metadata: { produit_id: l.produitId } },
          },
        })),
        allow_promotion_codes: this.codesPromo || undefined,
        success_url: p.urlSucces,
        cancel_url: p.urlAnnulation,
        // La session expire au bout de 30 minutes (minimum autorisé par Stripe).
        expires_at: Math.floor(Date.now() / 1000) + 30 * 60,
      },
      { idempotencyKey: `session-${p.commandeId}` },
    );
    if (!session.url) throw new Error('Stripe n’a pas renvoyé d’URL de paiement.');
    return { id: session.id, url: session.url };
  }

  lireWebhook(corpsBrut: Buffer, signature: string | undefined): EvenementPaiement {
    if (!signature) throw new ErreurSignature('Signature Stripe absente.');
    let evt: Stripe.Event;
    try {
      evt = this.stripe.webhooks.constructEvent(corpsBrut, signature, this.secretWebhook);
    } catch (e) {
      throw new ErreurSignature((e as Error).message);
    }
    const base = { id: evt.id, typeOrigine: evt.type };
    if (!evt.type.startsWith('checkout.session.')) return { ...base, type: 'ignore' };
    const s = evt.data.object as Stripe.Checkout.Session;
    const commun = {
      ...base,
      sessionId: s.id,
      commandeId: s.metadata?.commande_id ?? s.client_reference_id ?? undefined,
      montantCentimes: s.amount_total ?? undefined,
      sousTotalCentimes: s.amount_subtotal ?? undefined,
      devise: s.currency ?? undefined,
      reference: typeof s.payment_intent === 'string' ? s.payment_intent : s.payment_intent?.id,
    };
    switch (evt.type) {
      case 'checkout.session.completed':
        return { ...commun, type: s.payment_status === 'paid' ? 'paiement_reussi' : 'paiement_en_attente' };
      case 'checkout.session.async_payment_succeeded':
        return { ...commun, type: 'paiement_reussi' };
      case 'checkout.session.async_payment_failed':
        return { ...commun, type: 'paiement_echoue' };
      case 'checkout.session.expired':
        return { ...commun, type: 'session_expiree' };
      default:
        return { ...commun, type: 'ignore' };
    }
  }
}

/**
 * Simulation locale (développement uniquement, refusée en production par la configuration).
 * Aucun argent n'est en jeu : la page /paiement-simule permet de choisir « réussite » ou « échec ».
 */
export class FournisseurSimulation implements FournisseurPaiement {
  mode: ModePaiement = 'simulation';
  constructor(private urlPublique: string) {}
  async creerSession(p: ParametresSession) {
    const id = `sim_${p.commandeId}`;
    const retour = new URL(p.urlSucces);
    return { id, url: `${this.urlPublique}/paiement-simule/${p.commandeId}?t=${retour.searchParams.get('t') ?? ''}` };
  }
  lireWebhook(): EvenementPaiement {
    throw new ErreurSignature('Pas de webhook en mode simulation.');
  }
}
