import fs from 'node:fs';
import path from 'node:path';
import nodemailer from 'nodemailer';
import boutique from '../../config/boutique.json' with { type: 'json' };
import { formatDate, formatPrix } from '../shared/format';

export interface Message {
  a: string;
  sujet: string;
  texte: string;
  html: string;
  repondreA?: string;
}

export interface Messagerie {
  type: 'smtp' | 'fichiers_locaux' | 'non_configuree';
  envoyer(m: Message): Promise<void>;
}

/** Envoi réel par SMTP (Gmail avec mot de passe d'application, Resend, Brevo…). Port 465 = connexion chiffrée directe. */
export function messagerieSmtp(cfg: { host: string; port: number; user?: string; pass?: string }, expediteur: string): Messagerie {
  const transport = nodemailer.createTransport({
    host: cfg.host,
    port: cfg.port,
    secure: cfg.port === 465,
    auth: cfg.user ? { user: cfg.user, pass: cfg.pass } : undefined,
  });
  return {
    type: 'smtp',
    async envoyer(m) {
      await transport.sendMail({ from: expediteur, to: m.a, subject: m.sujet, text: m.texte, html: m.html, replyTo: m.repondreA });
    },
  };
}

/** Sans SMTP configuré : les e-mails sont écrits dans data/boite-envoi/ (pratique en développement). */
export function messagerieFichiers(dossier: string): Messagerie {
  return {
    type: 'fichiers_locaux',
    async envoyer(m) {
      fs.mkdirSync(dossier, { recursive: true });
      const nom = `${new Date().toISOString().replace(/[:.]/g, '-')}-${m.sujet.replace(/[^a-z0-9]+/gi, '-').slice(0, 40)}`;
      fs.writeFileSync(path.join(dossier, `${nom}.html`), `<!-- À : ${m.a} | Sujet : ${m.sujet} -->\n${m.html}`);
      fs.writeFileSync(path.join(dossier, `${nom}.txt`), `À : ${m.a}\nSujet : ${m.sujet}\n\n${m.texte}`);
      console.info(`[e-mail non envoyé — SMTP non configuré] « ${m.sujet} » pour ${m.a} → ${dossier}`);
    },
  };
}

/** En ligne sans SMTP : rien ne peut être écrit sur le disque, l'e-mail est seulement signalé dans les journaux. */
export function messagerieJournal(): Messagerie {
  return {
    type: 'non_configuree',
    async envoyer(m) {
      console.warn(`[e-mail NON ENVOYÉ — SMTP non configuré] « ${m.sujet} » pour ${m.a}`);
    },
  };
}

// ---------- Modèles ----------

const echap = (s: string) => s.replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!);

function gabarit(titre: string, corpsHtml: string): string {
  return `<!doctype html><html lang="fr"><body style="margin:0;background:#FFF9F0;font-family:Arial,Helvetica,sans-serif;color:#34343A">
<div style="max-width:560px;margin:0 auto;padding:24px">
<p style="font-size:20px;font-weight:bold;margin:0 0 16px">${echap(boutique.nom)}</p>
<div style="background:#ffffff;border-radius:16px;padding:24px">
<h1 style="font-size:20px;margin:0 0 12px">${echap(titre)}</h1>
${corpsHtml}
</div>
<p style="font-size:12px;color:#544C3E;margin-top:16px">${echap(boutique.nom)} — produits 100 % numériques, aucun colis n'est expédié.</p>
</div></body></html>`;
}

const bouton = (url: string, texte: string) =>
  `<p style="margin:20px 0"><a href="${echap(url)}" style="background:#FFD66B;color:#34343A;text-decoration:none;font-weight:bold;padding:12px 20px;border-radius:10px;display:inline-block">${echap(texte)}</a></p>`;

export function emailConfirmationCommande(p: {
  commandeId: string;
  lignes: { titre: string; prixCentimes: number }[];
  totalCentimes: number;
  lienAcces: string;
  accesExpireLe: string;
  consentementLe: string;
  texteConsentement: string;
  urlSite: string;
}): Omit<Message, 'a'> {
  const lignesTxt = p.lignes.map((l) => `- ${l.titre} : ${formatPrix(l.prixCentimes)}`).join('\n');
  const lignesHtml = p.lignes.map((l) => `<li>${echap(l.titre)} — ${formatPrix(l.prixCentimes)}</li>`).join('');
  const consentement = `Le ${formatDate(p.consentementLe, true)}, vous avez accepté les conditions générales de vente et donné l'accord suivant : « ${p.texteConsentement} »`;
  return {
    sujet: `Votre commande ${p.commandeId} — vos fichiers sont prêts`,
    texte: `Merci pour votre commande !\n\nCommande : ${p.commandeId}\n${lignesTxt}\nTotal payé : ${formatPrix(p.totalCentimes)}\n\nTéléchargez vos fichiers ici :\n${p.lienAcces}\n(ce lien est valable jusqu'au ${formatDate(p.accesExpireLe)} ; vous pourrez en demander un nouveau sur ${p.urlSite}/mes-telechargements)\n\nConfirmation de votre accord (à conserver) :\n${consentement}\n\nConseil : imprimez sur du papier A4 standard, option « Ajuster à la page ».`,
    html: gabarit(
      'Merci pour votre commande !',
      `<p>Commande <strong>${echap(p.commandeId)}</strong></p><ul>${lignesHtml}</ul>
<p><strong>Total payé : ${formatPrix(p.totalCentimes)}</strong></p>
${bouton(p.lienAcces, 'Télécharger mes fichiers')}
<p style="font-size:14px">Ce lien est valable jusqu'au ${formatDate(p.accesExpireLe)}. Ensuite, vous pourrez recevoir un nouveau lien depuis la page <a href="${echap(p.urlSite)}/mes-telechargements">Mes téléchargements</a>.</p>
<p style="font-size:13px;background:#FBF3E7;border-radius:10px;padding:12px"><strong>Confirmation de votre accord (à conserver)</strong><br>${echap(consentement)}</p>`,
    ),
  };
}

export function emailRenouvellement(p: { commandes: { id: string; lien: string; creeLe: string }[]; expireLe: string }): Omit<Message, 'a'> {
  const txt = p.commandes.map((c) => `- Commande ${c.id} du ${formatDate(c.creeLe)} : ${c.lien}`).join('\n');
  const html = p.commandes
    .map((c) => `<p>Commande <strong>${echap(c.id)}</strong> du ${formatDate(c.creeLe)}</p>${bouton(c.lien, 'Accéder à mes fichiers')}`)
    .join('');
  return {
    sujet: 'Vos nouveaux liens de téléchargement',
    texte: `Voici vos nouveaux liens d'accès (valables jusqu'au ${formatDate(p.expireLe)}) :\n${txt}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez simplement ce message.`,
    html: gabarit('Vos nouveaux liens de téléchargement', `${html}<p style="font-size:14px">Ces liens sont valables jusqu'au ${formatDate(p.expireLe)}. Si vous n'êtes pas à l'origine de cette demande, ignorez ce message.</p>`),
  };
}

export function emailContact(p: { nom: string; email: string; sujet: string; message: string }): Omit<Message, 'a'> {
  return {
    sujet: `[Contact] ${p.sujet} — ${p.nom}`,
    texte: `De : ${p.nom} <${p.email}>\nSujet : ${p.sujet}\n\n${p.message}`,
    html: gabarit(`Message de ${p.nom}`, `<p>De : ${echap(p.nom)} &lt;${echap(p.email)}&gt;<br>Sujet : ${echap(p.sujet)}</p><p style="white-space:pre-wrap">${echap(p.message)}</p>`),
    repondreA: p.email,
  };
}
