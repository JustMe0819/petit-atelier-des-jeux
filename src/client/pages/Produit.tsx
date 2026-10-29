import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { Icone } from '../components/Icone';
import { BoutonAjouter, CarteProduit, infoContenu } from '../components/Cartes';
import { Alerte, Chargement, EtatVide, FilAriane } from '../components/Divers';
import { useCatalogue } from '../lib/catalogue';
import { usePanier } from '../lib/panier';
import { useTitre } from '../lib/useTitre';
import { formatPrix } from '../../shared/format';
import { CATEGORIES, DIFFICULTES, libelleTheme } from '../../shared/libelles';

export default function Produit() {
  const { slug = '' } = useParams();
  const { parId, chargement, enVente, aVenir } = useCatalogue();
  const { ajouter, contient } = usePanier();
  const navigate = useNavigate();
  const produit = parId(slug);
  const [vue, setVue] = useState(0);
  useTitre(produit?.titre ?? 'Produit', produit?.description);

  if (chargement) return <Chargement />;
  if (!produit) {
    return <EtatVide icone="search_off" titre="Produit introuvable" texte="Ce produit n’existe pas ou plus." action={<Link to="/boutique" className="btn-primaire">Retour à la boutique</Link>} />;
  }

  const cat = CATEGORIES.find((c) => c.id === produit.categorie)!;
  const images = [{ src: produit.couverture, legende: `Couverture : ${produit.titre}`, couverture: true }, ...produit.apercus.map((a) => ({ ...a, couverture: false }))];
  const image = images[Math.min(vue, images.length - 1)];
  const composants = produit.composants.map((c) => parId(c)).filter((p) => !!p);
  const valeurUnitaire = composants.reduce((s, p) => s + p!.prixCentimes, 0);
  const autres = [...enVente, ...aVenir].filter((p) => p.id !== produit.id && !produit.composants.includes(p.id)).slice(0, 4);
  const acheter = () => {
    if (!contient(produit.id)) ajouter(produit.id);
    navigate('/panier');
  };

  return (
    <div className="conteneur pb-28 md:pb-space-xl">
      <FilAriane etapes={[{ a: '/', libelle: 'Accueil' }, { a: `/boutique?type=${produit.categorie}`, libelle: cat.libelle }, { libelle: produit.titre }]} />

      {!produit.disponible && (
        <div className="mb-space-md">
          <Alerte type="attention">
            <strong>Bientôt disponible.</strong> Ce produit est en cours de {produit.statut === 'en_verification' ? 'relecture' : 'création'} et ne peut pas encore être acheté.
            {produit.apercus.length > 0 && ' Les aperçus ci-dessous proviennent de la version en cours de relecture.'}
          </Alerte>
        </div>
      )}

      <div className="grid grid-cols-1 gap-space-xl lg:grid-cols-2">
        {/* GALERIE */}
        <section aria-label="Aperçus" className="relative overflow-hidden rounded-3xl bg-surface-container-lowest p-space-md shadow-doux md:p-space-lg">
          <div className="pointer-events-none absolute -right-12 -top-12 h-44 w-44 rounded-full bg-primary-container/25 blur-2xl" />
          <div className="relative mx-auto aspect-[1/1.2] w-full max-w-[420px] overflow-hidden rounded-xl bg-surface-container-low shadow-carte">
            <span className="pastille absolute left-2.5 top-2.5 z-10 bg-secondary-container text-on-secondary-container shadow-sm"><Icone nom="child_care" className="text-[14px]" /> {produit.age}</span>
            {!image.couverture && <span className="pastille absolute right-2.5 top-2.5 z-10 bg-inverse-surface text-inverse-on-surface">Extrait réel du PDF</span>}
            <img src={image.src} alt={image.legende} className={`h-full w-full ${image.couverture ? 'object-cover' : 'bg-white object-contain'}`} />
          </div>
          <p className="mt-space-sm text-center font-texte text-caption text-on-surface-variant">{image.legende}</p>
          {images.length > 1 && (
            <div className="mt-space-md flex gap-space-sm overflow-x-auto pb-1 sans-barre" role="tablist" aria-label="Choisir un aperçu">
              {images.map((im, i) => (
                <button key={im.src} type="button" role="tab" aria-selected={i === vue} aria-label={im.legende} onClick={() => setVue(i)}
                  className={`shrink-0 rounded-lg p-1 transition-all ${i === vue ? 'bg-primary-container/40 ring-2 ring-primary' : 'bg-surface-container-low'}`}>
                  <img src={im.src} alt="" loading="lazy" className="aspect-[1/1.3] w-16 rounded bg-white object-cover object-top" />
                </button>
              ))}
            </div>
          )}
          {produit.apercus.length > 0 && (
            <p className="mt-space-sm flex items-start gap-2 rounded-lg bg-surface-container-high/60 p-2.5 font-texte text-caption text-on-surface-variant">
              <Icone nom="verified" className="shrink-0 text-[18px] text-secondary" />
              Les aperçus sont des pages du vrai PDF, affichées en basse définition avec la mention « aperçu ». Le fichier acheté est en qualité d’impression.
            </p>
          )}
        </section>

        {/* INFOS + ACHAT */}
        <section className="flex flex-col gap-space-md">
          <div>
            <p className="mb-1 flex items-center gap-1.5 font-texte text-caption font-bold uppercase tracking-wider text-on-tertiary-container">
              <Icone nom={cat.icone} className="text-[16px]" /> {cat.libelle} • {produit.themes.map(libelleTheme).join(', ')}
            </p>
            <h1 className="font-titre text-headline-lg-mobile text-marine md:text-headline-lg">{produit.titre}</h1>
            <p className="font-titre text-title-md text-on-surface-variant">{produit.sousTitre}</p>
          </div>
          <div className="grid grid-cols-3 gap-2">
            {[
              { i: 'cake', c: 'text-primary', v: produit.age, l: 'Âge conseillé' },
              { i: 'layers', c: 'text-secondary', v: infoContenu(produit), l: produit.nbPages && produit.categorie !== 'cahiers' ? `${produit.nbPages} pages A4` : 'Format PDF A4' },
              { i: 'trending_up', c: 'text-tertiary', v: produit.difficultes.length > 1 ? 'Progressive' : DIFFICULTES.find((d) => d.id === produit.difficultes[0])?.libelle ?? '', l: 'Difficulté' },
            ].map((s) => (
              <div key={s.l} className="flex flex-col items-center rounded-xl bg-surface-container-low p-2.5 text-center">
                <Icone nom={s.i} className={`text-[20px] ${s.c}`} />
                <span className="mt-1 font-texte text-label-md">{s.v}</span>
                <span className="font-texte text-caption text-on-surface-variant">{s.l}</span>
              </div>
            ))}
          </div>

          <div className="flex flex-col gap-space-md rounded-2xl bg-surface-container-lowest p-space-md shadow-carte">
            <div className="flex items-baseline justify-between gap-2">
              <span className="font-titre text-display-hero-mobile">{formatPrix(produit.prixCentimes)}</span>
              <span className="pastille bg-primary-container/50 text-on-primary-container">Paiement unique</span>
            </div>
            {composants.length > 0 && valeurUnitaire > produit.prixCentimes && (
              <p className="-mt-2 font-texte text-body-sm text-secondary">
                Achetés séparément, ces {composants.length} produits coûtent {formatPrix(valeurUnitaire)} au total.
              </p>
            )}
            <p className="-mt-2 font-texte text-caption text-on-surface-variant">PDF à télécharger après paiement • Aucun abonnement • Impressions illimitées pour votre foyer</p>
            {produit.disponible ? (
              <div className="flex flex-col gap-space-sm sm:flex-row">
                <BoutonAjouter produit={produit} taille="grand" className="flex-1" />
                <button type="button" onClick={acheter} className="btn-sombre py-3.5">
                  <Icone nom="arrow_forward" className="text-[18px]" /> Acheter maintenant
                </button>
              </div>
            ) : (
              <BoutonAjouter produit={produit} />
            )}
            <p className="font-texte text-caption text-on-surface-variant">
              <Icone nom="info" className="mr-1 align-[-3px] text-[16px]" />
              Un seul exemplaire suffit : vous pourrez imprimer les pages autant de fois que nécessaire pour les enfants de votre foyer.
            </p>
            <ul className="flex flex-col gap-2 rounded-xl bg-surface-container-low/70 p-space-sm">
              {[
                { i: 'bolt', f: 'bg-secondary-container text-on-secondary-container', t: <><strong>Téléchargement dès la confirmation du paiement</strong>, à l’écran et par e-mail.</> },
                { i: 'eco', f: 'bg-tertiary-container text-on-tertiary-container', t: <><strong>Pages de jeu en noir et blanc</strong>{produit.versionEncreEco ? ', avec une version économie d’encre en plus.' : ', faciles à imprimer à la maison.'}</> },
                { i: 'lock_reset', f: 'bg-primary-container text-on-primary-container', t: <><strong>Lien perdu ?</strong> Recevez de nouveaux liens depuis « Mes téléchargements ».</> },
              ].map((x) => (
                <li key={x.i} className="flex items-center gap-2.5">
                  <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${x.f}`}><Icone nom={x.i} className="text-[15px]" /></span>
                  <span className="font-texte text-caption text-on-surface">{x.t}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>

      {/* DESCRIPTION */}
      <section className="mt-space-xl grid grid-cols-1 gap-space-xl lg:grid-cols-2">
        <div>
          <p className="surtitre font-bold text-secondary">Ce que contient le PDF</p>
          <h2 className="mb-space-sm mt-1 font-titre text-headline-md">Ce que votre enfant va faire</h2>
          <p className="mb-space-md font-texte text-body-md text-on-surface-variant">{produit.description}</p>
          <ul className="space-y-space-sm">
            {produit.pointsCles.map((p) => (
              <li key={p} className="flex items-start gap-3 rounded-xl bg-surface-container-lowest p-space-md shadow-doux">
                <Icone nom="check_circle" className="text-[22px] text-secondary" />
                <span className="font-texte text-body-md">{p}</span>
              </li>
            ))}
          </ul>
          {composants.length > 0 && (
            <div className="mt-space-md rounded-2xl bg-surface-container-lowest p-space-md shadow-doux">
              <h3 className="mb-space-sm font-titre text-title-md">Produits inclus dans le coffret</h3>
              <ul className="space-y-2">
                {composants.map((c) => (
                  <li key={c!.id} className="flex items-center justify-between gap-2 font-texte text-body-sm">
                    <Link to={`/produit/${c!.slug}`} className="lien">{c!.titre}</Link>
                    <span className="text-on-surface-variant">{infoContenu(c!)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-space-md flex items-center gap-3 rounded-xl bg-primary-container/30 p-space-md">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-container text-on-primary-container"><Icone nom="fact_check" /></span>
            <div>
              <h3 className="font-titre text-title-md">Corrigés</h3>
              <p className="font-texte text-body-sm text-on-surface-variant">{produit.corriges.texte}</p>
            </div>
          </div>
        </div>
        <div>
          <p className="surtitre font-bold text-tertiary">Guide pratique</p>
          <h2 className="mb-space-md mt-1 font-titre text-headline-md">Conseils d’impression</h2>
          <div className="space-y-2.5">
            {[
              { i: 'description', c: 'text-secondary', t: 'Quel papier choisir ?', x: <>Le papier blanc standard <strong>80 g</strong> convient parfaitement aux crayons de couleur. Pour les feutres, préférez un papier <strong>100 à 120 g</strong>.</> },
              { i: 'tune', c: 'text-primary', t: 'Réglages simples', x: <>Format <strong>A4</strong>, option « Taille réelle » ou « Ajuster à la page ». Vous pouvez imprimer tout le fichier ou seulement quelques pages.</> },
              { i: 'devices', c: 'text-tertiary', t: 'Ouvrir le fichier', x: <>C’est un PDF standard : il s’ouvre sur ordinateur, tablette ou téléphone, avec le navigateur ou un lecteur PDF gratuit.</> },
            ].map((c) => (
              <div key={c.t} className="flex items-start gap-3 rounded-xl bg-surface-container-lowest p-space-md shadow-doux">
                <Icone nom={c.i} className={`text-[24px] ${c.c}`} />
                <div>
                  <h3 className="font-titre text-title-md">{c.t}</h3>
                  <p className="font-texte text-body-sm text-on-surface-variant">{c.x}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {autres.length > 0 && (
        <section className="mt-space-xl">
          <div className="mb-space-md flex items-end justify-between">
            <div>
              <h2 className="font-titre text-headline-sm">Vous aimerez aussi</h2>
              <p className="font-texte text-caption text-on-surface-variant">D’autres jeux à imprimer pour les 6-8 ans</p>
            </div>
            <Link to="/boutique" className="flex items-center gap-0.5 font-texte text-label-md text-tertiary">Tout voir <Icone nom="chevron_right" className="text-[16px]" /></Link>
          </div>
          <div className="grid grid-cols-1 gap-gutter sm:grid-cols-2 lg:grid-cols-4">
            {autres.map((p) => <CarteProduit key={p.id} produit={p} />)}
          </div>
        </section>
      )}

      {produit.disponible && (
        <div className="fixed inset-x-3 bottom-[72px] z-40 flex items-center justify-between gap-3 rounded-xl bg-surface/95 p-2.5 shadow-fort backdrop-blur-md md:hidden">
          <div className="pl-1">
            <span className="block font-texte text-caption text-on-surface-variant">PDF A4</span>
            <span className="font-titre text-title-md">{formatPrix(produit.prixCentimes)}</span>
          </div>
          <BoutonAjouter produit={produit} />
        </div>
      )}
    </div>
  );
}
