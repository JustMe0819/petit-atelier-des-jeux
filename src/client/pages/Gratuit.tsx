import { Link } from 'react-router-dom';
import { Icone } from '../components/Icone';
import { Chargement, EtatVide } from '../components/Divers';
import { useCatalogue } from '../lib/catalogue';
import { useTitre } from '../lib/useTitre';

export default function Gratuit() {
  useTitre('Activités gratuites à imprimer', 'Labyrinthes, nonogrammes et jeux de logique gratuits à imprimer pour les 6-8 ans, sans inscription.');
  const { gratuits, chargement } = useCatalogue();

  return (
    <div className="conteneur pb-space-xl pt-space-lg">
      <section className="relative mb-space-xl overflow-hidden rounded-3xl bg-surface-container-low px-6 py-12 shadow-doux md:px-12 md:py-16">
        <div className="pointer-events-none absolute -right-16 -top-16 h-80 w-80 rounded-full bg-primary-container/25 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 right-1/3 h-64 w-64 rounded-full bg-secondary-container/40 blur-2xl" />
        <div className="relative z-10 flex max-w-3xl flex-col items-start gap-4">
          <span className="pastille bg-secondary-container px-3.5 py-1.5 text-label-lg text-on-secondary-container">
            <Icone nom="verified" className="text-[18px]" /> Gratuit • sans inscription • sans carte bancaire
          </span>
          <h1 className="font-titre text-display-hero-mobile text-marine md:text-display-hero">Le coin gratuit de l'atelier</h1>
          <p className="max-w-2xl font-texte text-body-md text-on-surface-variant md:text-body-lg">
            Testez nos jeux à la maison : des fiches de labyrinthes, de nonogrammes et de logique, avec leurs solutions. Ce sont de vrais extraits fabriqués avec les mêmes outils que les cahiers de la boutique.
          </p>
          <div className="flex flex-wrap items-center gap-6 pt-2 text-on-surface-variant">
            {[
              ['print', 'text-primary', 'Format A4 noir et blanc'],
              ['bolt', 'text-secondary', 'Téléchargement direct'],
              ['child_care', 'text-tertiary', 'Pour les 6-8 ans'],
            ].map(([i, c, t]) => (
              <span key={t} className="flex items-center gap-2 font-texte text-body-sm font-semibold">
                <span className={`flex h-7 w-7 items-center justify-center rounded-lg bg-surface-container-highest ${c}`}><Icone nom={i} className="text-[18px]" /></span> {t}
              </span>
            ))}
          </div>
        </div>
        <img src="/images/decor/renard-carte.webp" alt="" className="pointer-events-none absolute bottom-0 right-8 hidden h-44 lg:block" />
      </section>

      <div className="mb-space-lg flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="surtitre flex items-center gap-2 font-bold text-primary"><Icone nom="palette" className="text-[20px]" /> Fiches et mini-cahier</p>
          <h2 className="font-titre text-headline-lg-mobile md:text-headline-lg">À télécharger tout de suite</h2>
        </div>
        <p className="font-texte text-body-sm text-on-surface-variant">PDF A4 • solutions incluses</p>
      </div>

      {chargement ? (
        <Chargement />
      ) : gratuits.length === 0 ? (
        <EtatVide icone="hourglass_empty" titre="Les activités gratuites arrivent" texte="Elles seront disponibles très bientôt." />
      ) : (
        <section className="mb-space-xl grid grid-cols-1 gap-gutter sm:grid-cols-2 lg:grid-cols-4">
          {gratuits.map((g, i) => (
            <article key={g.id} className={`group flex flex-col overflow-hidden rounded-2xl bg-surface-container-lowest transition-all duration-300 hover:shadow-fort ${i === gratuits.length - 1 ? 'shadow-carte' : 'shadow-doux'}`}>
              <div className="relative flex aspect-[1/1.2] items-center justify-center overflow-hidden bg-surface-container p-3">
                <img src={g.apercu} alt={`Aperçu : ${g.titre}`} loading="lazy" className="h-full w-full rounded-lg bg-white object-contain shadow-sm transition-transform duration-300 group-hover:scale-[1.02]" />
                <span className="pastille absolute left-4 top-4 bg-secondary-container text-on-secondary-container">{g.age}</span>
                <span className="pastille absolute right-4 top-4 bg-surface-container-lowest/90 font-texte text-caption text-on-surface backdrop-blur-sm">PDF A4 • {g.nb_pages} page{g.nb_pages > 1 ? 's' : ''}</span>
              </div>
              <div className="flex flex-1 flex-col justify-between gap-4 p-5">
                <div className="space-y-2">
                  <h3 className="font-titre text-title-md group-hover:text-primary">{g.titre}</h3>
                  <p className="font-texte text-body-sm text-on-surface-variant">{g.description}</p>
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {g.competences.map((c) => <span key={c} className="rounded-full bg-surface-container px-2 py-0.5 font-texte text-caption text-on-surface-variant">{c}</span>)}
                  </div>
                </div>
                <a href={g.fichier} download className="btn-primaire w-full">
                  <Icone nom="download" className="text-[20px]" /> Télécharger le PDF gratuit
                </a>
              </div>
            </article>
          ))}
        </section>
      )}

      <section className="mb-space-xl rounded-3xl bg-gradient-to-r from-surface-container to-surface-container-high p-8 md:p-12">
        <div className="flex flex-col items-center justify-between gap-8 lg:flex-row">
          <div className="max-w-2xl space-y-3">
            <p className="surtitre flex items-center gap-1.5 font-bold text-primary"><Icone nom="auto_stories" className="text-[20px]" /> Envie de continuer ?</p>
            <h2 className="font-titre text-headline-lg-mobile md:text-headline-lg">Vous avez aimé ces activités ?</h2>
            <p className="font-texte text-body-md text-on-surface-variant">Les packs et grands cahiers de la boutique reprennent les mêmes types de jeux, avec davantage de pages et une difficulté progressive.</p>
          </div>
          <div className="flex w-full shrink-0 flex-col gap-4 sm:w-auto sm:flex-row">
            <Link to="/boutique?type=cahiers" className="btn-secondaire h-12">Les grands cahiers <Icone nom="menu_book" className="text-[18px]" /></Link>
            <Link to="/boutique" className="btn-primaire h-12">Voir toute la boutique <Icone nom="arrow_forward" className="text-[18px]" /></Link>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-gutter md:grid-cols-3">
        {[
          ['eco', 'text-primary', 'Encre et papier', 'Choisissez le mode « Noir et blanc » de votre imprimante : les pages de jeu sont conçues en traits noirs.'],
          ['autorenew', 'text-secondary', 'Glissez-les sous pochette', 'Une pochette plastique transparente A4 et un feutre effaçable permettent de réutiliser une fiche plusieurs fois.'],
          ['school', 'text-tertiary', 'Écoles et périscolaire', 'Les fiches gratuites peuvent être imprimées pour votre classe ou votre groupe.'],
        ].map(([i, c, t, x]) => (
          <div key={t} className="flex flex-col items-start gap-3 rounded-2xl bg-surface-container-lowest p-6 shadow-doux">
            <span className={`flex h-10 w-10 items-center justify-center rounded-xl bg-surface-container ${c}`}><Icone nom={i} className="text-[22px]" /></span>
            <h3 className="font-titre text-title-md">{t}</h3>
            <p className="font-texte text-body-sm text-on-surface-variant">{x}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
