import { useState, type FormEvent } from 'react';
import { Link, useLocation, useSearchParams } from 'react-router-dom';
import { AssistantFaq } from '../components/AssistantFaq';
import { Icone } from '../components/Icone';
import { Accordeon } from '../components/Accordeon';
import { Alerte, Champ, EnTeteSection, EtatVide } from '../components/Divers';
import { FormulaireRenouvellement } from './Commande';
import { FAQ } from './contenus';
import { api } from '../lib/api';
import { BOUTIQUE, aCompleter } from '../lib/boutique';
import { useTitre } from '../lib/useTitre';

export function APropos() {
  useTitre('À propos', 'Thylia, créatrice du Petit Atelier des Jeux, conçoit des jeux à imprimer pour les 6-8 ans.');
  return (
    <>
      <section className="conteneur grid grid-cols-12 items-center gap-gutter py-space-xl">
        <div className="col-span-12 flex flex-col gap-space-md lg:col-span-7">
          <span className="pastille w-fit bg-secondary-container px-3.5 py-1.5 text-on-secondary-container"><Icone nom="verified" className="text-[18px]" /> Une boutique française de jeux à imprimer</span>
          <h1 className="font-titre text-display-hero-mobile text-marine md:text-display-hero">
            Redonner le goût du papier, <span className="italic text-primary">loin du tumulte</span> des écrans.
          </h1>
          <p className="max-w-2xl font-texte text-body-md leading-relaxed text-on-surface-variant md:text-body-lg">
            Le <strong className="text-on-surface">Petit Atelier des Jeux</strong> propose des jeux et des cahiers d’activités à imprimer pour les enfants de 6 à 8 ans : labyrinthes, logique, nonogrammes, observation. L’idée est simple : des moments calmes, une consigne claire, et la fierté de trouver par soi-même.
          </p>
          <figure className="rounded-2xl bg-surface-container-lowest p-space-md shadow-doux md:p-space-lg">
            <div className="space-y-space-sm font-texte text-body-md leading-relaxed text-on-surface-variant">
              <p>
                Bonjour, je m’appelle <strong className="text-on-surface">Thylia</strong> ! Depuis toute petite, je dessine, je découpe et j’invente des jeux sur papier. Le Petit Atelier des Jeux, c’est ma façon de partager cette passion avec les enfants d’aujourd’hui.
              </p>
              <p>
                J’ai créé cette boutique pour proposer une vraie alternative aux écrans : des activités qui occupent les enfants pour de bon et qui leur apprennent plein de choses en jouant. Observer, réfléchir, compter, persévérer… et être fier d’avoir trouvé tout seul.
              </p>
              <p>
                Chaque cahier est pensé pour être joli, clair et facile à imprimer à la maison. Bonne impression, et surtout bon jeu !
              </p>
            </div>
            <figcaption className="mt-space-md flex items-center gap-space-sm">
              <img src="/images/decor/renard-logo.webp" alt="" className="h-12 w-12 rounded-full bg-surface-container-low object-contain p-1" />
              <span>
                <span className="block font-titre text-title-md text-primary">Thylia</span>
                <span className="font-texte text-caption text-on-surface-variant">Créatrice du Petit Atelier des Jeux</span>
              </span>
            </figcaption>
          </figure>
        </div>
        <div className="relative col-span-12 lg:col-span-5">
          <div className="relative mx-auto grid max-w-md grid-cols-2 gap-4 rounded-[2rem] bg-surface-container-high p-6 shadow-carte">
            {['labyrinthes-petits-explorateurs', 'defis-de-la-logique', 'mes-premiers-nonogrammes', 'mission-dinosaures'].map((id, i) => (
              <img key={id} src={`/images/couvertures/${id}.webp`} alt="" className={`rounded-xl shadow-carte ${i % 2 ? 'rotate-2' : '-rotate-2'}`} />
            ))}
          </div>
          <div className="absolute -bottom-6 -left-2 flex max-w-xs items-center gap-space-sm rounded-2xl bg-surface-container-lowest p-space-md shadow-fort">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary-container text-on-primary-container"><Icone nom="child_care" className="text-[28px]" /></span>
            <div>
              <p className="font-titre text-headline-sm leading-tight">6 à 8 ans</p>
              <p className="font-texte text-caption text-on-surface-variant">L’âge où l’on apprend à lire les consignes seul et à chercher en autonomie</p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-surface-container-low py-space-xl">
        <div className="conteneur">
          <EnTeteSection surtitre="Transparence" titre="Comment mes jeux sont fabriqués" texte="Je préfère vous expliquer simplement ma méthode plutôt que d’enjoliver." />
          <div className="grid grid-cols-1 gap-gutter md:grid-cols-3">
            {[
              { i: 'code', f: 'bg-secondary-container text-on-secondary-container', t: '1. Des programmes génèrent les jeux', x: 'Les labyrinthes, grilles et suites logiques sont créés par des programmes à partir de règles précises. Cela permet de proposer beaucoup de jeux variés, avec une difficulté maîtrisée.', b: 'Aucun jeu n’est inventé « au hasard »' },
              { i: 'rule', f: 'bg-primary-container text-on-primary-container', t: '2. Chaque solution est vérifiée', x: 'Un programme contrôle chaque jeu : le labyrinthe a bien un chemin, le nonogramme une seule solution, la suite une seule bonne réponse. Le PDF est aussi vérifié (format A4, marges, pages vides).', b: 'Contrôles automatiques à chaque fabrication' },
              { i: 'visibility', f: 'bg-tertiary-container text-on-tertiary-container', t: '3. Je relis tout avant la vente', x: 'Un cahier n’est mis en vente qu’après que je l’ai relu entièrement, page par page. Tant que ce n’est pas fait, il reste affiché « Bientôt disponible ».', b: 'Pas de mise en vente automatique' },
            ].map((p) => (
              <div key={p.t} className="flex flex-col justify-between overflow-hidden rounded-2xl bg-surface-container-lowest shadow-doux">
                <div className="p-space-lg">
                  <span className={`mb-space-md flex h-12 w-12 items-center justify-center rounded-xl ${p.f}`}><Icone nom={p.i} className="text-[26px]" /></span>
                  <h3 className="mb-2 font-titre text-headline-sm">{p.t}</h3>
                  <p className="font-texte text-body-md leading-relaxed text-on-surface-variant">{p.x}</p>
                </div>
                <p className="flex items-center gap-1 bg-surface-container-low/60 p-space-md font-texte text-caption font-bold text-secondary"><Icone nom="check_circle" className="text-[16px]" /> {p.b}</p>
              </div>
            ))}
          </div>
          <p className="mt-space-md font-texte text-body-sm text-on-surface-variant">
            Des outils d’intelligence artificielle m’aident à imaginer des thèmes, à formuler certaines consignes et à créer les illustrations des couvertures. Ils ne servent jamais à valider une solution : ce rôle revient aux programmes de vérification et à ma relecture.
          </p>
        </div>
      </section>

      <section className="conteneur py-space-xl">
        <div className="flex flex-col items-center justify-around gap-space-md rounded-2xl bg-surface-container p-space-md md:flex-row">
          {[
            ['schedule', 'text-primary', 'Accès rapide', 'Fichiers disponibles dès la confirmation du paiement'],
            ['forest', 'text-secondary', 'Impression raisonnée', 'Pages aérées, en noir et blanc'],
            ['mail', 'text-tertiary', 'Une question ?', 'Écrivez-moi via la page Contact'],
          ].map(([i, c, t, x]) => (
            <div key={t} className="flex items-center gap-3">
              <Icone nom={i} className={`text-[28px] ${c}`} />
              <div>
                <span className="block font-titre text-headline-sm">{t}</span>
                <span className="font-texte text-caption text-on-surface-variant">{x}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

export function Faq() {
  useTitre('Questions fréquentes', 'Téléchargement, impression, paiement et droit de rétractation : toutes les réponses.');
  const { hash } = useLocation();
  const [categorie, setCategorie] = useState<string>(hash === '#impression' ? 'impression' : 'all');
  const onglets = [
    ['all', 'Toutes les questions'],
    ['telechargement', 'Téléchargement & fichiers'],
    ['impression', 'Impression'],
    ['paiement', 'Paiement'],
    ['droits', 'Rétractation & licence'],
  ];
  return (
    <div className="conteneur max-w-4xl py-space-xl">
      <EnTeteSection centre surtitre="Réponses claires" titre="Foire aux questions" texte="Tout ce qu’il faut savoir pour commander, télécharger et imprimer vos jeux." />
      <div className="mb-space-lg flex gap-space-xs overflow-x-auto pb-2 sans-barre md:justify-center" role="tablist">
        {onglets.map(([id, l]) => (
          <button key={id} type="button" role="tab" aria-selected={categorie === id} onClick={() => setCategorie(id)}
            className={`shrink-0 rounded-full px-4 py-2 font-texte text-label-lg transition-colors ${categorie === id ? 'bg-on-surface text-surface' : 'bg-surface-container text-on-surface-variant hover:text-on-surface'}`}>
            {l}
          </button>
        ))}
      </div>
      <div id="impression">
        <Accordeon grand key={categorie} elements={FAQ.filter((q) => categorie === 'all' || q.categorie === categorie)} />
      </div>
      <div className="mt-space-xl grid grid-cols-1 gap-gutter md:grid-cols-2">
        <Link to="/contact" className="flex items-start gap-space-sm rounded-2xl bg-surface-container-lowest p-space-md shadow-doux hover:shadow-carte">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-container text-on-primary-container"><Icone nom="mail" /></span>
          <div><p className="font-titre text-title-md">M’écrire</p><p className="font-texte text-body-sm text-on-surface-variant">Une question sur un jeu ou une commande ? Utilisez le formulaire de contact.</p></div>
        </Link>
        <Link to="/mes-telechargements" className="flex items-start gap-space-sm rounded-2xl bg-surface-container-lowest p-space-md shadow-doux hover:shadow-carte">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-secondary-container text-on-secondary-container"><Icone nom="download" /></span>
          <div><p className="font-titre text-title-md">Retrouver mes fichiers</p><p className="font-texte text-body-sm text-on-surface-variant">Recevez de nouveaux liens de téléchargement par e-mail.</p></div>
        </Link>
      </div>
    </div>
  );
}

export function Contact() {
  useTitre('Contact');
  const [etat, setEtat] = useState<{ ok: boolean; texte: string } | null>(null);
  const [envoi, setEnvoi] = useState(false);
  const envoyer = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(e.currentTarget)) as Record<string, string>;
    setEnvoi(true);
    try {
      await api('/api/contact', { method: 'POST', json: d });
      setEtat({ ok: true, texte: 'Merci ! Votre message a bien été envoyé. Je vous répondrai par e-mail.' });
      (e.target as HTMLFormElement).reset();
    } catch (err) {
      setEtat({ ok: false, texte: (err as Error).message });
    } finally {
      setEnvoi(false);
    }
  };
  return (
    <div className="conteneur py-space-xl">
      <div className="grid grid-cols-12 gap-gutter rounded-3xl bg-surface-container-low p-space-md md:p-space-xl">
        <div className="col-span-12 flex flex-col gap-space-md lg:col-span-5">
          <span className="pastille w-fit bg-secondary-container text-on-secondary-container"><Icone nom="support_agent" className="text-[18px]" /> Contact</span>
          <h1 className="font-titre text-headline-lg-mobile text-marine md:text-headline-lg">Une question ?<br />Écrivez-moi.</h1>
          <p className="font-texte text-body-md text-on-surface-variant">L’assistant ci-dessous répond tout de suite aux questions fréquentes. Pour un fichier qui ne s’ouvre pas ou une question sur une commande, écrivez-moi : je lis tous les messages.</p>
          <AssistantFaq idFormulaire="formulaire-contact" />
          <div className="flex items-start gap-space-sm rounded-2xl bg-surface-container-lowest p-space-md shadow-doux">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-container text-on-primary-container"><Icone nom="mail" /></span>
            <div className="min-w-0">
              <span className="block font-texte text-caption uppercase tracking-wider text-on-surface-variant">Par e-mail</span>
              {aCompleter(BOUTIQUE.email_contact) ? <Champ valeur={BOUTIQUE.email_contact} /> : <a href={`mailto:${BOUTIQUE.email_contact}`} className="lien break-all">{BOUTIQUE.email_contact}</a>}
            </div>
          </div>
        </div>
        <div className="col-span-12 lg:col-span-7">
          <form id="formulaire-contact" onSubmit={envoyer} className="scroll-mt-24 space-y-space-md rounded-2xl bg-surface-container-lowest p-space-md shadow-doux md:p-space-xl">
            <h2 className="font-titre text-headline-sm">Envoyer un message</h2>
            <div className="grid grid-cols-1 gap-space-md md:grid-cols-2">
              <div><label htmlFor="c-nom" className="etiquette">Votre prénom ou nom</label><input id="c-nom" name="nom" required maxLength={100} className="champ" autoComplete="name" /></div>
              <div><label htmlFor="c-email" className="etiquette">Votre e-mail</label><input id="c-email" name="email" type="email" required className="champ" autoComplete="email" /></div>
            </div>
            <div>
              <label htmlFor="c-sujet" className="etiquette">Objet</label>
              <select id="c-sujet" name="sujet" className="champ appearance-none">
                <option value="commande">Question sur une commande</option>
                <option value="impression">Conseil d’impression</option>
                <option value="pedagogie">Question sur un jeu ou une tranche d’âge</option>
                <option value="autre">Autre demande</option>
              </select>
            </div>
            <div><label htmlFor="c-message" className="etiquette">Votre message</label><textarea id="c-message" name="message" required minLength={10} maxLength={5000} rows={5} className="champ h-auto resize-y py-3" /></div>
            <input type="text" name="site" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden />
            <div className="flex flex-col justify-between gap-space-sm md:flex-row md:items-center">
              <p className="flex items-center gap-2 font-texte text-caption text-on-surface-variant"><Icone nom="security" className="text-[16px] text-secondary" /> Vos données servent uniquement à vous répondre. <Link to="/confidentialite" className="underline">En savoir plus</Link></p>
              <button type="submit" disabled={envoi} className="btn-primaire h-12 px-8">{envoi ? 'Envoi…' : 'Envoyer'} <Icone nom="send" className="text-[18px]" /></button>
            </div>
            {etat && <Alerte type={etat.ok ? 'succes' : 'erreur'}>{etat.texte}</Alerte>}
          </form>
        </div>
      </div>
    </div>
  );
}

export function MesTelechargements() {
  useTitre('Mes téléchargements');
  return (
    <div className="conteneur max-w-2xl space-y-space-md py-space-xl">
      <span className="pastille bg-secondary-container text-on-secondary-container"><Icone nom="download" className="text-[16px]" /> Mes téléchargements</span>
      <h1 className="font-titre text-headline-lg-mobile text-marine md:text-headline-lg">Retrouver mes fichiers</h1>
      <p className="font-texte text-body-md text-on-surface-variant">
        Pas de compte à créer : indiquez l’adresse e-mail utilisée lors de votre achat. Si une commande payée y correspond, vous recevrez un e-mail avec de nouveaux liens d’accès pour toutes vos commandes.
      </p>
      <FormulaireRenouvellement />
      <p className="font-texte text-caption text-on-surface-variant">Pas d’e-mail au bout de quelques minutes ? Vérifiez vos courriers indésirables, puis <Link to="/contact" className="underline">contactez-nous</Link> avec votre numéro de commande (PAD-…).</p>
    </div>
  );
}

export function TelechargementImpossible() {
  useTitre('Téléchargement impossible');
  const [sp] = useSearchParams();
  const raison = sp.get('raison') ?? '';
  const textes: Record<string, [string, string]> = {
    lien_expire: ['Ce lien de téléchargement a expiré', 'Pour protéger vos fichiers, chaque bouton de téléchargement fonctionne pendant une durée limitée. Recevez de nouveaux liens par e-mail ci-dessous.'],
    lien_invalide: ['Ce lien n’est pas valide', 'Le lien est incomplet ou a été modifié. Utilisez le bouton reçu par e-mail ou demandez de nouveaux liens.'],
    non_payee: ['Commande non réglée', 'Les fichiers ne sont disponibles qu’après la confirmation du paiement.'],
    introuvable: ['Fichier introuvable', 'Ce fichier ne fait pas partie de la commande. Si vous pensez qu’il s’agit d’une erreur, contactez-moi.'],
    trop_de_requetes: ['Trop de téléchargements', 'Merci de patienter quelques minutes avant de réessayer.'],
  };
  const [titre, texte] = textes[raison] ?? ['Téléchargement impossible', 'Une erreur est survenue. Réessayez ou demandez de nouveaux liens.'];
  return (
    <div className="conteneur max-w-2xl space-y-space-md py-space-xl">
      <h1 className="font-titre text-headline-lg-mobile">{titre}</h1>
      <p className="font-texte text-body-md text-on-surface-variant">{texte}</p>
      <FormulaireRenouvellement />
    </div>
  );
}

export function Introuvable() {
  useTitre('Page introuvable');
  return <EtatVide icone="explore_off" titre="Cette page s’est perdue dans le labyrinthe" texte="L’adresse n’existe pas ou plus." action={<Link to="/" className="btn-primaire">Retour à l’accueil</Link>} />;
}
