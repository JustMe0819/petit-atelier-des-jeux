import crypto from 'node:crypto';

/** Jeton aléatoire (256 bits) — envoyé au client, seule son empreinte est stockée en base. */
export function nouveauJeton(): string {
  return crypto.randomBytes(32).toString('base64url');
}

export function empreinte(jeton: string): string {
  return crypto.createHash('sha256').update(jeton).digest('hex');
}

export function nouvelIdCommande(): string {
  // Ex. PAD-7K3M-9QX2 : lisible au téléphone, sans caractères ambigus.
  const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const octets = crypto.randomBytes(8);
  let s = '';
  for (let i = 0; i < 8; i++) s += alphabet[octets[i] % alphabet.length];
  return `PAD-${s.slice(0, 4)}-${s.slice(4)}`;
}

export interface ChargeLien {
  c: string; // commande
  p: string; // produit
  f: 'pdf' | 'corriges' | 'encre_eco';
  e: number; // expiration (ms depuis epoch)
}

/** Lien de téléchargement signé (HMAC-SHA256) et daté : impossible à fabriquer sans le secret serveur. */
export function signerLien(charge: ChargeLien, secret: string): string {
  const corps = Buffer.from(JSON.stringify(charge)).toString('base64url');
  const sig = crypto.createHmac('sha256', secret).update(corps).digest('base64url');
  return `${corps}.${sig}`;
}

export type ResultatLien = { ok: true; charge: ChargeLien } | { ok: false; raison: 'invalide' | 'expire'; charge?: ChargeLien };

export function verifierLien(jeton: string, secret: string, maintenant = Date.now()): ResultatLien {
  const [corps, sig] = jeton.split('.');
  if (!corps || !sig) return { ok: false, raison: 'invalide' };
  const attendu = crypto.createHmac('sha256', secret).update(corps).digest();
  let recu: Buffer;
  try {
    recu = Buffer.from(sig, 'base64url');
  } catch {
    return { ok: false, raison: 'invalide' };
  }
  if (recu.length !== attendu.length || !crypto.timingSafeEqual(recu, attendu)) return { ok: false, raison: 'invalide' };
  let charge: ChargeLien;
  try {
    charge = JSON.parse(Buffer.from(corps, 'base64url').toString('utf8'));
  } catch {
    return { ok: false, raison: 'invalide' };
  }
  if (typeof charge.e !== 'number' || typeof charge.c !== 'string' || typeof charge.p !== 'string') return { ok: false, raison: 'invalide' };
  if (charge.e < maintenant) return { ok: false, raison: 'expire', charge };
  return { ok: true, charge };
}

export function masquerEmail(email: string): string {
  const [local, domaine] = email.split('@');
  if (!domaine) return '***';
  const debut = local.slice(0, Math.min(2, local.length));
  return `${debut}${'•'.repeat(Math.max(1, local.length - debut.length))}@${domaine}`;
}

export function normaliserEmail(email: string): string {
  return email.trim().toLowerCase();
}
