import { Link, useNavigate } from 'react-router-dom';
import { Icone } from './Icone';
import { usePanier } from '../lib/panier';
import { useCatalogue } from '../lib/catalogue';
import { formatPrix } from '../../shared/format';
import { CATEGORIES, libelleTheme } from '../../shared/libelles';
import type { ProduitPublic } from '../../shared/types';

/** Ambiances pastel des cartes de la planche (fond, pastille de prix). */
export const AMBIANCES = [
  { fond: 'bg-[#EAF4F4]', prix: 'bg-[#3E8794] text-white', point: 'bg-[#3E8794]' },
  { fond: 'bg-[#FCEFE6]', prix: 'bg-[#C9634B] text-white', point: 'bg-[#E08A6E]' },
  { fond: 'bg-[#EDF4F8]', prix: 'bg-[#3E8794] text-white', point: 'bg-[#5AA7C9]' },
  { fond: 'bg-[#FDF2E2]', prix: 'bg-[#F6B941] text-on-surface', point: 'bg-[#F0A93A]' },
  { fond: 'bg-[#EBF3EC]', prix: 'bg-[#2F7C80] text-white', point: 'bg-[#6FAE7B]' },
  { fond: 'bg-[#FCEEF1]', prix: 'bg-[#C85A7A] text-white', point: 'bg-[#E58FA6]' },
];

export function infoContenu(p: ProduitPublic): string {
  if (p.composants.length) return `${p.composants.length} produits réunis`;
  if (p.nbJeux && p.categorie !== 'cahiers') return `${p.nbJeux} ${p.categorie === 'nonogrammes' ? 'grilles' : p.categorie === 'labyrinthes' ? 'labyrinthes' : 'activités'}`;
  if (p.nbPages) return `${p.nbPages} pages`;
  return p.objectif;
}

export function BoutonAjouter({ produit, taille = 'normal', className = '' }: { produit: ProduitPublic; taille?: 'normal' | 'grand' | 'rond'; className?: string }) {
  const { ajouter, contient } = usePanier();
  const navigate = useNavigate();
  if (!produit.disponible) {
    return (
      <span className={`pastille bg-surface-container-high text-on-surface-variant ${className}`}>
        <Icone nom="schedule" className="text-[16px]" /> Bientôt disponible
      </span>
    );
  }
  const dedans = contient(produit.id);
  if (taille === 'rond') {
    return (
      <button type="button" aria-label={dedans ? `${produit.titre} est dans le panier` : `Ajouter ${produit.titre} au panier`}
        onClick={() => (dedans ? navigate('/panier') : ajouter(produit.id))}
        className={`flex h-9 w-9 items-center justify-center rounded-full shadow-sm transition-transform active:scale-95 ${dedans ? 'bg-secondary-container text-on-secondary-container' : 'bg-primary-container text-on-primary-container'} ${className}`}>
        <Icone nom={dedans ? 'check' : 'add'} className="text-[20px]" />
      </button>
    );
  }
  return (
    <button type="button" onClick={() => (dedans ? navigate('/panier') : ajouter(produit.id))}
      className={`btn ${taille === 'grand' ? 'px-5 py-3.5' : 'h-10 px-3.5'} shadow-sm ${dedans ? 'bg-secondary-container text-on-secondary-container' : 'bg-primary-container text-on-primary-container hover:bg-primary-fixed-dim'} ${className}`}>
      <Icone nom={dedans ? 'check' : 'add_shopping_cart'} className="text-[18px]" />
      <span>{dedans ? 'Dans le panier' : taille === 'grand' ? `Ajouter au panier — ${formatPrix(produit.prixCentimes)}` : 'Ajouter'}</span>
    </button>
  );
}

/** Carte du catalogue (style des maquettes Stitch « Boutique »). */
export function CarteProduit({ produit }: { produit: ProduitPublic }) {
  const cat = CATEGORIES.find((c) => c.id === produit.categorie)!;
  return (
    <article className="group flex flex-col rounded-2xl bg-surface-container-lowest p-4 shadow-doux transition-all duration-300 hover:shadow-carte">
      <Link to={`/produit/${produit.slug}`} className="relative mb-space-sm block overflow-hidden rounded-xl bg-surface-container-low p-3" tabIndex={-1} aria-hidden>
        <img src={produit.couverture} alt="" loading="lazy" className="mx-auto aspect-[1/1.18] w-[86%] rounded-lg object-cover shadow-carte transition-transform duration-500 group-hover:scale-[1.03]" />
        {!produit.disponible && <span className="pastille absolute bottom-4 left-1/2 -translate-x-1/2 bg-inverse-surface text-inverse-on-surface shadow-carte">En préparation</span>}
      </Link>
      <div className="mb-2 flex flex-wrap gap-1.5">
        <span className="pastille bg-secondary-container text-on-secondary-container">{produit.age}</span>
        <span className="pastille bg-surface-container text-on-surface-variant">{infoContenu(produit)}</span>
      </div>
      <div className="flex flex-1 flex-col">
        <p className="mb-1 flex items-center gap-1.5 font-texte text-caption font-bold uppercase tracking-wider text-on-tertiary-container">
          <Icone nom={cat.icone} className="text-[15px]" /> {cat.court} • {produit.themes.map(libelleTheme).join(', ')}
        </p>
        <h3 className="mb-1 font-titre text-headline-sm leading-tight text-on-surface">
          <Link to={`/produit/${produit.slug}`} className="hover:text-primary">{produit.titre}</Link>
        </h3>
        <p className="mb-space-sm line-clamp-2 font-texte text-body-sm text-on-surface-variant">{produit.description}</p>
        <div className="mt-auto flex items-center justify-between gap-2 pt-2">
          <div>
            <span className="block font-texte text-caption text-on-surface-variant">{produit.disponible ? 'Format PDF' : 'Prix prévu'}</span>
            <span className="font-titre text-headline-md font-extrabold text-on-surface">{formatPrix(produit.prixCentimes)}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Link to={`/produit/${produit.slug}`} title="Voir la fiche et les aperçus" aria-label={`Voir la fiche de ${produit.titre}`}
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-surface-container-low text-on-surface transition-colors hover:bg-surface-container">
              <Icone nom="visibility" className="text-[20px]" />
            </Link>
            <BoutonAjouter produit={produit} />
          </div>
        </div>
      </div>
    </article>
  );
}

function Feuille({ src, legende, rotation }: { src: string; legende: string; rotation: string }) {
  return (
    <figure className={`w-[34%] shrink-0 rounded-md bg-white p-1 shadow-carte ${rotation}`}>
      <img src={src} alt={legende} loading="lazy" className="aspect-[1/1.414] w-full rounded-sm object-cover object-top" />
    </figure>
  );
}

/** Grande carte pastel reprenant la planche produits (couverture + vrais aperçus du PDF). */
export function CartePlanche({ produit, index }: { produit: ProduitPublic; index: number }) {
  const amb = AMBIANCES[index % AMBIANCES.length];
  const { parId } = useCatalogue();
  const apercus = produit.apercus.slice(0, 2);
  const estCoffret = produit.composants.length > 0;
  return (
    <article className={`flex flex-col rounded-3xl p-space-md shadow-doux md:p-space-lg ${amb.fond}`}>
      <h3 className="mb-space-md font-titre text-headline-sm font-bold leading-snug text-marine md:text-headline-md">
        <Link to={`/produit/${produit.slug}`} className="hover:underline">{produit.titre}</Link>
      </h3>
      <Link to={`/produit/${produit.slug}`} className="mb-space-md flex items-center gap-3" aria-label={`Voir ${produit.titre}`}>
        <img src={produit.couverture} alt={`Couverture : ${produit.titre}`} loading="lazy" className={`${estCoffret ? 'w-[55%]' : 'w-[38%]'} shrink-0 rounded-lg shadow-carte`} />
        {estCoffret ? (
          <ul className="flex-1 space-y-1.5">
            {produit.composants.map((c, i) => (
              <li key={c} className="flex items-center gap-2 font-texte text-caption text-on-surface">
                <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-md ${AMBIANCES[i].prix}`}>
                  <Icone nom={CATEGORIES.find((x) => x.id === parId(c)?.categorie)?.icone ?? 'description'} className="text-[14px]" />
                </span>
                <span className="line-clamp-2">{parId(c)?.titre ?? c}</span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="flex flex-1 items-start gap-2">
            {apercus.length > 0
              ? apercus.map((a, i) => (
                  <Feuille key={a.src} src={a.src} legende={a.legende} rotation={i === 0 ? '-rotate-1' : 'rotate-1'} />
                ))
              : [0, 1].map((i) => (
                  // Produit pas encore généré : pages vierges en attendant les vrais aperçus du PDF.
                  <figure key={i} aria-hidden className={`flex aspect-[1/1.414] w-[34%] shrink-0 flex-col items-center justify-center gap-1 rounded-md border-2 border-dashed border-on-surface-variant/25 bg-white/70 p-1 text-center ${i === 0 ? '-rotate-1' : 'rotate-1'}`}>
                    <Icone nom="schedule" className="text-[20px] text-on-surface-variant/60" />
                    <span className="font-texte text-[10px] leading-tight text-on-surface-variant/80">Aperçu à venir</span>
                  </figure>
                ))}
          </div>
        )}
      </Link>
      <ul className="mb-space-md space-y-1 font-texte text-body-sm text-on-surface">
        {produit.pointsCles.slice(0, 2).map((pc) => (
          <li key={pc} className="flex items-start gap-2">
            <span className={`mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full ${amb.point}`} />
            {pc}
          </li>
        ))}
      </ul>
      <div className="mt-auto flex items-center justify-between gap-3">
        <span className="font-texte text-caption text-on-surface-variant">{estCoffret ? 'Offre groupée numérique' : `${produit.age} • ${infoContenu(produit)}`}</span>
        {produit.disponible ? (
          <Link to={`/produit/${produit.slug}`} className={`rounded-full px-5 py-2 font-titre text-headline-sm font-bold shadow-sm ${amb.prix}`}>
            {formatPrix(produit.prixCentimes)}
          </Link>
        ) : (
          <span className="pastille bg-white/80 text-on-surface-variant">
            <Icone nom="schedule" className="text-[16px]" /> Bientôt disponible
          </span>
        )}
      </div>
    </article>
  );
}
