import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Icone } from './Icone';

/**
 * Petit assistant de questions fréquentes, sans intelligence artificielle :
 * il compare les mots tapés à une liste de mots-clés et affiche la réponse prévue.
 * Tout se passe dans le navigateur : rien n'est envoyé ni enregistré.
 */

interface Reponse {
  id: string;
  /** Mots-clés sans accents, en minuscules (une partie de mot suffit : « imprim » trouve « imprimer »). */
  mots: string[];
  texte: string;
  liens?: { vers: string; libelle: string }[];
}

const REPONSES: Reponse[] = [
  {
    id: 'lien',
    mots: ['perdu', 'expire', 'lien', 'retrouv', 'recuper', 'pas recu', 'recu aucun', 'spam', 'courrier indesirable', 'plus acces', 'acceder'],
    texte: 'Pas de souci : sur la page « Mes téléchargements », indiquez l’adresse e-mail utilisée lors de l’achat. Si une commande payée y correspond, vous recevez tout de suite de nouveaux liens pour toutes vos commandes. Pensez aussi à regarder dans vos courriers indésirables.',
    liens: [{ vers: '/mes-telechargements', libelle: 'Recevoir de nouveaux liens' }],
  },
  {
    id: 'reception',
    mots: ['recoit', 'recevoir', 'apres achat', 'apres paiement', 'apres le paiement', 'livraison', 'colis', 'comment ca marche', 'telecharg'],
    texte: 'Dès que le paiement est confirmé, les boutons de téléchargement s’affichent sur la page de confirmation, et un e-mail récapitulatif vous est envoyé avec un lien vers cette page. Aucun compte n’est nécessaire et aucun colis n’est expédié : ce sont des fichiers PDF.',
  },
  {
    id: 'impression',
    mots: ['imprim', 'papier', 'a4', 'format', 'taille', 'feutre', 'marge', 'coupe'],
    texte: 'Toute imprimante de maison au format A4 convient. Du papier standard de 80 g suffit (100 à 120 g si votre enfant utilise des feutres). Dans la fenêtre d’impression, choisissez « Taille réelle » ou « Ajuster à la page ». Vous pouvez n’imprimer que les pages souhaitées.',
  },
  {
    id: 'encre',
    mots: ['encre', 'economi', 'noir et blanc', 'couleur', 'cartouche', 'toner'],
    texte: 'Les pages de jeux sont en noir et blanc, avec des traits nets. Pour les grands cahiers, une version « économie d’encre » est fournie en plus du fichier principal.',
  },
  {
    id: 'corriges',
    mots: ['solution', 'corrig', 'reponse'],
    texte: 'Oui, les solutions sont fournies : à la fin du PDF ou dans un fichier séparé selon le produit (c’est indiqué sur chaque fiche). Vous pouvez ainsi imprimer les jeux sans donner les réponses.',
  },
  {
    id: 'paiement',
    mots: ['paie', 'payer', 'carte', 'stripe', 'apple pay', 'google pay', 'securis', 'paypal', 'bancaire', 'cb'],
    texte: 'Le paiement se fait sur la page sécurisée de Stripe. Vos données bancaires sont saisies chez Stripe et ne passent jamais par notre site. Les moyens proposés (carte bancaire et, selon votre appareil, Apple Pay ou Google Pay) s’affichent sur la page de paiement.',
  },
  {
    id: 'retractation',
    mots: ['rembours', 'retract', 'annul', 'defectueux', 'casse', 'illisible', 'incomplet', 'erreur de commande', 'trompe'],
    texte: 'Pour un fichier numérique, vous renoncez au délai de rétractation au moment de la commande afin d’accéder tout de suite aux fichiers. En revanche, si un fichier est défectueux (illisible, incomplet), la garantie légale de conformité s’applique : écrivez-nous et nous trouverons une solution.',
    liens: [{ vers: '/cgv', libelle: 'Lire les CGV' }],
  },
  {
    id: 'ouvrir',
    mots: ['ouvre pas', 'ouvrir', 'lecteur', 'adobe', 'tablette', 'ipad', 'smartphone', 'portable', 'fichier pdf'],
    texte: 'Les fichiers sont des PDF classiques : ils s’ouvrent avec le lecteur intégré à votre ordinateur, tablette ou téléphone (ou Adobe Acrobat Reader, gratuit). Si un fichier refuse de s’ouvrir, téléchargez-le à nouveau ; si le problème continue, écrivez-nous.',
  },
  {
    id: 'age',
    mots: ['age', 'ans', 'niveau', 'difficult', 'cp', 'ce1', 'ce2', 'maternelle', 'trop dur', 'trop facile'],
    texte: 'Les jeux sont pensés pour les enfants de 6 à 8 ans (du CP au CE2). Chaque produit progresse du niveau débutant (dès 6 ans) au niveau défi (8 ans). Le niveau est indiqué sur chaque fiche produit.',
    liens: [{ vers: '/boutique', libelle: 'Voir la boutique' }],
  },
  {
    id: 'licence',
    mots: ['partag', 'frere', 'soeur', 'plusieurs enfants', 'reimprim', 'combien de fois', 'revend', 'licence', 'droit d utiliser'],
    texte: 'Vous pouvez imprimer les fichiers autant de fois que nécessaire pour les enfants de votre foyer. Ils ne doivent pas être partagés en dehors du foyer, publiés ni revendus.',
  },
  {
    id: 'classe',
    mots: ['classe', 'ecole', 'enseign', 'professeur', 'maitre', 'eleve', 'centre de loisirs', 'association'],
    texte: 'Les activités du Coin gratuit peuvent être imprimées pour votre classe. Les produits payants sont prévus pour un usage familial : pour un usage en classe, écrivez-nous afin de convenir d’une licence adaptée.',
    liens: [{ vers: '/activites-gratuites', libelle: 'Le Coin gratuit' }],
  },
  {
    id: 'gratuit',
    mots: ['gratuit', 'essai', 'tester', 'exemple', 'apercu', 'echantillon'],
    texte: 'Oui ! Des activités gratuites sont à télécharger sans inscription dans le Coin gratuit. Chaque fiche produit montre aussi de vraies pages du PDF en aperçu.',
    liens: [{ vers: '/activites-gratuites', libelle: 'Voir les activités gratuites' }],
  },
  {
    id: 'coffret',
    mots: ['coffret', 'pack', 'lot', 'ensemble', 'tout acheter', 'reduction', 'promo'],
    texte: 'Le grand coffret réunit plusieurs produits en un seul achat, moins cher que s’ils étaient achetés séparément. Son contenu exact est détaillé sur sa fiche.',
    liens: [{ vers: '/boutique?type=packs', libelle: 'Voir le coffret' }],
  },
  {
    id: 'compte',
    mots: ['compte', 'inscri', 'mot de passe', 'connexion', 'connecter', 'identifiant'],
    texte: 'Aucun compte n’est nécessaire : vos fichiers sont liés à l’adresse e-mail indiquée lors de l’achat. Si besoin, de nouveaux liens se demandent depuis « Mes téléchargements ».',
    liens: [{ vers: '/mes-telechargements', libelle: 'Mes téléchargements' }],
  },
  {
    id: 'facture',
    mots: ['facture', 'recu de paiement', 'justificatif', 'ticket'],
    texte: 'Le récapitulatif de votre commande vous est envoyé par e-mail après le paiement. Si vous avez besoin d’une facture, écrivez-nous avec votre numéro de commande (il commence par PAD-).',
  },
  {
    id: 'humain',
    mots: ['humain', 'ecrire', 'parler', 'joindre', 'contacter', 'telephone', 'appeler', 'question'],
    texte: 'Bien sûr : écrivez-nous avec le formulaire de cette page. Nous lisons tous les messages et répondons par e-mail.',
  },
];

const SUGGESTIONS: { libelle: string; id: string }[] = [
  { libelle: 'J’ai perdu mon lien', id: 'lien' },
  { libelle: 'Comment imprimer ?', id: 'impression' },
  { libelle: 'Économiser de l’encre', id: 'encre' },
  { libelle: 'Le paiement est-il sûr ?', id: 'paiement' },
  { libelle: 'Puis-je être remboursé·e ?', id: 'retractation' },
  { libelle: 'Pour quel âge ?', id: 'age' },
];

const normaliser = (t: string) =>
  ` ${t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, ' ').trim()} `;

/** Renvoie la réponse dont les mots-clés correspondent le mieux, ou null. */
export function chercherReponse(question: string): Reponse | null {
  const q = normaliser(question);
  let meilleure: { r: Reponse; score: number } | null = null;
  for (const r of REPONSES) {
    let score = 0;
    for (const m of r.mots) {
      // Mots courts (« cb », « ans », « a4 ») : mot entier uniquement, pour éviter les faux positifs.
      const trouve = m.length <= 3 ? q.includes(` ${m} `) : q.includes(m);
      if (trouve) score += m.includes(' ') ? 2 : 1;
    }
    if (score > 0 && (!meilleure || score > meilleure.score)) meilleure = { r, score };
  }
  return meilleure?.r ?? null;
}

type Message =
  | { de: 'vous'; texte: string }
  | { de: 'atelier'; texte: string; liens?: Reponse['liens']; versFormulaire?: boolean };

const ACCUEIL: Message = {
  de: 'atelier',
  texte: 'Bonjour ! Je réponds aux questions les plus fréquentes. Choisissez une question ci-dessous ou tapez la vôtre.',
};

export function AssistantFaq({ idFormulaire }: { idFormulaire: string }) {
  const [messages, setMessages] = useState<Message[]>([ACCUEIL]);
  const [saisie, setSaisie] = useState('');
  const fil = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = fil.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const repondre = (question: string, r: Reponse | null) => {
    const q = normaliser(question);
    let reponse: Message;
    if (r) {
      reponse = { de: 'atelier', texte: r.texte, liens: r.liens, versFormulaire: r.id === 'humain' || r.id === 'retractation' || r.id === 'facture' || r.id === 'classe' };
    } else if (/ (merci|super|parfait|top|genial) /.test(q)) {
      reponse = { de: 'atelier', texte: 'Avec plaisir ! Bonne impression et bons jeux.' };
    } else if (/ (bonjour|salut|bonsoir|hello|coucou) /.test(q) && q.trim().split(' ').length <= 3) {
      reponse = { de: 'atelier', texte: 'Bonjour ! Posez-moi votre question, par exemple : « Comment imprimer ? » ou « J’ai perdu mon lien ».' };
    } else {
      reponse = { de: 'atelier', texte: 'Je n’ai pas trouvé de réponse à cette question. Écrivez-nous avec le formulaire : nous vous répondrons par e-mail.', versFormulaire: true };
    }
    setMessages((m) => [...m, { de: 'vous', texte: question }, reponse]);
  };

  const envoyer = (e: FormEvent) => {
    e.preventDefault();
    const q = saisie.trim();
    if (!q) return;
    setSaisie('');
    repondre(q.slice(0, 300), chercherReponse(q));
  };

  const allerAuFormulaire = () => {
    const form = document.getElementById(idFormulaire);
    form?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    form?.querySelector<HTMLInputElement>('input[name="nom"]')?.focus({ preventScroll: true });
  };

  return (
    <section aria-labelledby="assistant-titre" className="flex flex-col rounded-2xl bg-surface-container-lowest shadow-doux">
      <header className="flex items-center gap-space-sm border-b border-surface-container-high p-space-md">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-secondary-container text-on-secondary-container"><Icone nom="support_agent" /></span>
        <div className="min-w-0 flex-1">
          <h2 id="assistant-titre" className="font-titre text-title-md">L’assistant de l’atelier</h2>
          <p className="font-texte text-caption text-on-surface-variant">Réponses immédiates aux questions fréquentes. Rien de ce que vous tapez n’est enregistré.</p>
        </div>
        {messages.length > 1 && (
          <button type="button" onClick={() => setMessages([ACCUEIL])} title="Recommencer" aria-label="Effacer la conversation"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-on-surface-variant hover:bg-surface-container">
            <Icone nom="restart_alt" className="text-[20px]" />
          </button>
        )}
      </header>

      <div ref={fil} role="log" aria-live="polite" aria-label="Conversation avec l’assistant" className="max-h-80 min-h-40 space-y-space-sm overflow-y-auto p-space-md">
        {messages.map((m, i) =>
          m.de === 'vous' ? (
            <p key={i} className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-primary-container px-4 py-2.5 font-texte text-body-sm text-on-primary-container">
              <span className="sr-only">Vous : </span>{m.texte}
            </p>
          ) : (
            <div key={i} className="w-fit max-w-[92%] rounded-2xl rounded-bl-md bg-surface-container px-4 py-2.5 font-texte text-body-sm text-on-surface">
              <span className="sr-only">Assistant : </span>
              <p>{m.texte}</p>
              {(m.liens?.length || m.versFormulaire) && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {m.liens?.map((l) => (
                    <Link key={l.vers} to={l.vers} className="inline-flex items-center gap-1 rounded-full bg-surface-container-lowest px-3 py-1 font-texte text-label-md text-primary shadow-sm hover:underline">
                      {l.libelle} <Icone nom="arrow_forward" className="text-[16px]" />
                    </Link>
                  ))}
                  {m.versFormulaire && (
                    <button type="button" onClick={allerAuFormulaire} className="inline-flex items-center gap-1 rounded-full bg-surface-container-lowest px-3 py-1 font-texte text-label-md text-primary shadow-sm hover:underline">
                      Écrire un message <Icone nom="mail" className="text-[16px]" />
                    </button>
                  )}
                </div>
              )}
            </div>
          ),
        )}
      </div>

      <div className="border-t border-surface-container-high p-space-md">
        <p className="mb-2 font-texte text-caption text-on-surface-variant" id="assistant-suggestions">Questions fréquentes :</p>
        <div className="mb-space-sm flex flex-wrap gap-2" aria-labelledby="assistant-suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s.id} type="button" onClick={() => repondre(s.libelle, REPONSES.find((r) => r.id === s.id) ?? null)}
              className="rounded-full border border-surface-container-highest bg-surface-container-low px-3 py-1.5 font-texte text-label-md text-on-surface transition-colors hover:bg-secondary-container">
              {s.libelle}
            </button>
          ))}
        </div>
        <form onSubmit={envoyer} className="flex gap-2">
          <label htmlFor="assistant-question" className="sr-only">Votre question</label>
          <input id="assistant-question" value={saisie} onChange={(e) => setSaisie(e.target.value)} maxLength={300} autoComplete="off"
            placeholder="Tapez votre question…" className="champ min-w-0 flex-1" />
          <button type="submit" className="btn-primaire h-12 shrink-0 px-4" aria-label="Poser la question">
            <Icone nom="send" className="text-[18px]" />
          </button>
        </form>
      </div>
    </section>
  );
}
