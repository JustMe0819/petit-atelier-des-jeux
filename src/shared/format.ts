export function formatPrix(centimes: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(centimes / 100);
}

export function formatDate(iso: string, avecHeure = false): string {
  const d = new Date(iso);
  return new Intl.DateTimeFormat('fr-FR', avecHeure
    ? { dateStyle: 'long', timeStyle: 'short', timeZone: 'Europe/Paris' }
    : { dateStyle: 'long', timeZone: 'Europe/Paris' }).format(d);
}

export function formatTaille(octets: number): string {
  if (octets < 1024 * 1024) return `${Math.max(1, Math.round(octets / 1024))} Ko`;
  return `${(octets / (1024 * 1024)).toFixed(1).replace('.', ',')} Mo`;
}

/** Texte de consentement affiché au client ET enregistré avec la commande (preuve). */
export const TEXTE_CONSENTEMENT_RETRACTATION =
  "Je demande l'accès immédiat aux fichiers numériques après le paiement et je reconnais que je perds ainsi mon droit de rétractation (article L221-28 13° du Code de la consommation).";

export const TEXTE_ACCEPTATION_CGV = "J'ai lu et j'accepte les conditions générales de vente.";
