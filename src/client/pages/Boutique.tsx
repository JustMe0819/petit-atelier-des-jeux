import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Icone } from '../components/Icone';
import { CarteProduit } from '../components/Cartes';
import { Alerte, Chargement, EtatVide } from '../components/Divers';
import { useCatalogue } from '../lib/catalogue';
import { useTitre } from '../lib/useTitre';
import { CATEGORIES, DIFFICULTES, THEMES, TRANCHES_PRIX, libelleCategorie, libelleTheme } from '../../shared/libelles';
import type { Categorie, Difficulte, ProduitPublic, Theme } from '../../shared/types';

const TRIS = [
  { id: 'pertinence', libelle: 'Pertinence' },
  { id: 'prix-croissant', libelle: 'Prix croissant' },
  { id: 'prix-decroissant', libelle: 'Prix décroissant' },
];

const sansAccents = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

interface Filtres {
  q: string;
  type: Categorie | null;
  theme: Theme | null;
  niveaux: Difficulte[];
  prix: string[];
  corriges: boolean;
  tri: string;
}

function lireFiltres(sp: URLSearchParams): Filtres {
  const liste = (k: string) => (sp.get(k) ?? '').split(',').filter(Boolean);
  const type = sp.get('type') as Categorie | null;
  const theme = sp.get('theme') as Theme | null;
  return {
    q: sp.get('q') ?? '',
    type: CATEGORIES.some((c) => c.id === type) ? type : null,
    theme: THEMES.some((t) => t.id === theme) ? theme : null,
    niveaux: liste('niveau').filter((n): n is Difficulte => DIFFICULTES.some((d) => d.id === n)),
    prix: liste('prix').filter((p) => TRANCHES_PRIX.some((t) => t.id === p)),
    corriges: sp.get('corriges') === '1',
    tri: TRIS.some((t) => t.id === sp.get('tri')) ? sp.get('tri')! : 'pertinence',
  };
}

export function filtrer(produits: ProduitPublic[], f: Filtres, sansType = false): ProduitPublic[] {
  const mots = sansAccents(f.q).split(/\s+/).filter(Boolean);
  const r = produits.filter((p) => {
    if (!sansType && f.type && p.categorie !== f.type) return false;
    if (f.theme && !p.themes.includes(f.theme)) return false;
    if (f.niveaux.length && !p.difficultes.some((d) => f.niveaux.includes(d))) return false;
    if (f.prix.length && !f.prix.some((id) => {
      const t = TRANCHES_PRIX.find((x) => x.id === id)!;
      return p.prixCentimes >= t.min && p.prixCentimes <= t.max;
    })) return false;
    if (f.corriges && !p.corriges.inclus) return false;
    if (mots.length) {
      const texte = sansAccents([p.titre, p.sousTitre, p.description, p.objectif, ...p.pointsCles, libelleCategorie(p.categorie), ...p.themes.map(libelleTheme)].join(' '));
      if (!mots.every((m) => texte.includes(m))) return false;
    }
    return true;
  });
  if (f.tri === 'prix-croissant') r.sort((a, b) => a.prixCentimes - b.prixCentimes);
  if (f.tri === 'prix-decroissant') r.sort((a, b) => b.prixCentimes - a.prixCentimes);
  return r;
}

export default function Boutique() {
  const [sp, setSp] = useSearchParams();
  const f = lireFiltres(sp);
  const { enVente, aVenir, chargement, erreur } = useCatalogue();
  const [panneau, setPanneau] = useState(false);
  const titre = f.type ? libelleCategorie(f.type) : f.theme ? `Univers ${libelleTheme(f.theme)}` : 'Tous nos jeux & cahiers à imprimer';
  useTitre(titre, 'Catalogue de jeux et cahiers d’activités à imprimer pour les 6-8 ans : labyrinthes, logique, nonogrammes.');

  const resultats = useMemo(() => filtrer(enVente, f), [enVente, sp]); // eslint-disable-line react-hooks/exhaustive-deps
  const prochains = useMemo(() => filtrer(aVenir, { ...f, prix: [], q: f.q }), [aVenir, sp]); // eslint-disable-line react-hooks/exhaustive-deps

  const maj = (modifs: Record<string, string | null>) => {
    const n = new URLSearchParams(sp);
    for (const [k, v] of Object.entries(modifs)) (v ? n.set(k, v) : n.delete(k));
    setSp(n, { replace: true });
  };
  const basculer = (cle: 'niveau' | 'prix', valeur: string) => {
    const actuels = cle === 'niveau' ? f.niveaux : f.prix;
    const n = actuels.includes(valeur as never) ? actuels.filter((x) => x !== valeur) : [...actuels, valeur];
    maj({ [cle]: n.join(',') || null });
  };
  const toutEffacer = () => setSp(new URLSearchParams(), { replace: true });

  const actifs: { libelle: string; retirer: () => void }[] = [
    ...(f.q ? [{ libelle: `« ${f.q} »`, retirer: () => maj({ q: null }) }] : []),
    ...(f.type ? [{ libelle: libelleCategorie(f.type), retirer: () => maj({ type: null }) }] : []),
    ...(f.theme ? [{ libelle: libelleTheme(f.theme), retirer: () => maj({ theme: null }) }] : []),
    ...f.niveaux.map((n) => ({ libelle: DIFFICULTES.find((d) => d.id === n)!.libelle, retirer: () => basculer('niveau', n) })),
    ...f.prix.map((p) => ({ libelle: TRANCHES_PRIX.find((t) => t.id === p)!.libelle, retirer: () => basculer('prix', p) })),
    ...(f.corriges ? [{ libelle: 'Corrigés inclus', retirer: () => maj({ corriges: null }) }] : []),
  ];

  const compteType = (c: Categorie | null) => filtrer(enVente, { ...f, type: c }, false).length;

  const filtresSecondaires = (
    <>
      <fieldset>
        <legend className="mb-2 font-titre text-title-md">Niveau de difficulté</legend>
        <div className="space-y-1.5 font-texte text-body-sm">
          {DIFFICULTES.map((d) => (
            <label key={d.id} className="flex cursor-pointer items-center gap-2 text-on-surface-variant">
              <input type="checkbox" className="h-4 w-4 accent-primary" checked={f.niveaux.includes(d.id)} onChange={() => basculer('niveau', d.id)} /> {d.libelle}
            </label>
          ))}
        </div>
      </fieldset>
      <fieldset>
        <legend className="mb-2 font-titre text-title-md">Prix</legend>
        <div className="space-y-1.5 font-texte text-body-sm">
          {TRANCHES_PRIX.map((t) => (
            <label key={t.id} className="flex cursor-pointer items-center gap-2 text-on-surface-variant">
              <input type="checkbox" className="h-4 w-4 accent-primary" checked={f.prix.includes(t.id)} onChange={() => basculer('prix', t.id)} /> {t.libelle}
            </label>
          ))}
        </div>
      </fieldset>
      <label className="flex cursor-pointer items-center gap-2 rounded-xl bg-surface-container-low p-3 font-texte text-body-sm font-bold">
        <input type="checkbox" className="h-4 w-4 accent-secondary" checked={f.corriges} onChange={() => maj({ corriges: f.corriges ? null : '1' })} /> Corrigés inclus
      </label>
    </>
  );

  return (
    <div className="conteneur pb-space-xl pt-space-lg">
      <div className="mb-space-lg flex flex-col justify-between gap-space-md md:flex-row md:items-end">
        <div>
          <span className="pastille mb-space-xs bg-secondary-container text-on-secondary-container">
            <Icone nom="auto_stories" className="text-[14px]" /> PDF A4 à imprimer • 6-8 ans
          </span>
          <h1 className="font-titre text-headline-lg-mobile text-marine md:text-headline-lg">{titre}</h1>
          <p className="mt-1 font-texte text-body-md text-on-surface-variant">Des PDF à télécharger après paiement, conçus pour les imprimantes de maison.</p>
        </div>
        <div className="flex items-center gap-space-sm rounded-xl bg-surface-container-low px-4 py-2.5 shadow-sm">
          <Icone nom="verified" className="text-[22px] text-secondary" />
          <div className="flex flex-col">
            <span className="font-texte text-label-md">Téléchargement après paiement</span>
            <span className="font-texte text-caption text-on-surface-variant">Liens à l’écran et par e-mail</span>
          </div>
        </div>
      </div>

      {erreur && <Alerte type="erreur">Le catalogue n’a pas pu être chargé : {erreur}</Alerte>}

      {/* Mobile / tablette : puces + panneau */}
      <div className="mb-space-md space-y-space-sm lg:hidden">
        <div className="relative flex items-center rounded-full bg-surface-container-lowest px-space-md py-1.5 shadow-sm">
          <Icone nom="search" className="mr-space-xs text-[22px] text-primary" />
          <input type="search" aria-label="Rechercher dans le catalogue" value={f.q} onChange={(e) => maj({ q: e.target.value || null })} placeholder="Rechercher un jeu, un thème..." className="h-9 w-full bg-transparent font-texte text-body-sm focus:outline-none" />
        </div>
        <div className="flex items-center justify-between gap-space-xs">
          <button type="button" aria-expanded={panneau} onClick={() => setPanneau(!panneau)} className="btn bg-surface-container-high px-3 py-2 text-label-md shadow-sm">
            <Icone nom="tune" className="text-[18px]" /> Filtres
            {actifs.length > 0 && <span className="flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-on-primary">{actifs.length}</span>}
          </button>
          <label className="relative max-w-[210px] flex-1">
            <span className="sr-only">Trier par</span>
            <select value={f.tri} onChange={(e) => maj({ tri: e.target.value === 'pertinence' ? null : e.target.value })} className="w-full cursor-pointer appearance-none rounded-lg bg-surface-container py-2 pl-3 pr-8 font-texte text-label-md shadow-sm focus:outline-none">
              {TRIS.map((t) => <option key={t.id} value={t.id}>Trier : {t.libelle}</option>)}
            </select>
            <Icone nom="expand_more" className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-[18px]" />
          </label>
        </div>
        <div className="-mx-gutter-mobile flex gap-space-xs overflow-x-auto px-gutter-mobile py-0.5 sans-barre md:-mx-margin md:px-margin">
          {[{ id: null, libelle: 'Tous les formats', emoji: '' }, ...CATEGORIES.map((c) => ({ id: c.id, libelle: c.court, emoji: c.emoji }))].map((c) => (
            <button key={c.id ?? 'tous'} type="button" aria-pressed={f.type === c.id} onClick={() => maj({ type: c.id })}
              className={`whitespace-nowrap rounded-full px-3.5 py-1.5 font-texte text-label-md shadow-sm ${f.type === c.id ? 'bg-primary text-on-primary' : 'bg-surface-container-lowest text-on-surface'}`}>
              {c.emoji} {c.libelle}
            </button>
          ))}
        </div>
        <div className="-mx-gutter-mobile flex items-center gap-1.5 overflow-x-auto px-gutter-mobile py-0.5 sans-barre md:-mx-margin md:px-margin">
          <span className="mr-1 flex shrink-0 items-center gap-1 font-texte text-caption text-on-surface-variant"><Icone nom="interests" className="text-[14px]" /> Thème :</span>
          {[{ id: null, libelle: 'Tous' }, ...THEMES.map((t) => ({ id: t.id, libelle: t.libelle }))].map((t) => (
            <button key={t.id ?? 'tous'} type="button" aria-pressed={f.theme === t.id} onClick={() => maj({ theme: t.id })}
              className={`whitespace-nowrap rounded-full px-2.5 py-1 font-texte text-label-md ${f.theme === t.id ? 'bg-surface-container-highest text-on-surface' : 'bg-surface-container-lowest text-on-surface-variant'}`}>
              {t.libelle}
            </button>
          ))}
        </div>
        {panneau && <div className="space-y-space-md rounded-xl bg-surface-container-lowest p-space-md shadow-sm">{filtresSecondaires}</div>}
      </div>

      <div className="grid grid-cols-12 items-start gap-gutter">
        {/* Bureau : barre latérale */}
        <aside className="sticky top-48 col-span-3 hidden flex-col gap-space-lg rounded-2xl bg-surface-container-lowest p-space-md shadow-doux lg:flex" aria-label="Filtres">
          <div>
            <label htmlFor="recherche-boutique" className="mb-2 block font-titre text-title-md">Rechercher</label>
            <div className="relative flex items-center">
              <Icone nom="search" className="pointer-events-none absolute left-3 text-[20px] text-outline" />
              <input id="recherche-boutique" type="search" value={f.q} onChange={(e) => maj({ q: e.target.value || null })} placeholder="Labyrinthe, dino, logique..." className="champ h-11 pl-10" />
            </div>
          </div>
          <fieldset>
            <legend className="mb-2.5 font-titre text-title-md">Type d'activité</legend>
            <div className="space-y-1 font-texte text-body-sm">
              {[{ id: null as Categorie | null, libelle: 'Tous les formats' }, ...CATEGORIES.map((c) => ({ id: c.id as Categorie | null, libelle: c.libelle }))].map((c) => (
                <label key={c.id ?? 'tous'} className={`flex cursor-pointer items-center justify-between rounded-lg p-2 transition-colors ${f.type === c.id ? 'bg-surface-container font-bold text-on-surface' : 'text-on-surface-variant hover:bg-surface-container-low'}`}>
                  <span className="flex items-center gap-2">
                    <input type="radio" name="type" className="accent-primary" checked={f.type === c.id} onChange={() => maj({ type: c.id })} /> {c.libelle}
                  </span>
                  <span className="rounded-full bg-surface-container-highest px-2 py-0.5 font-texte text-caption">{compteType(c.id)}</span>
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="mb-2.5 font-titre text-title-md">Univers</legend>
            <div className="flex flex-wrap gap-1.5">
              {[{ id: null as Theme | null, libelle: 'Tous' }, ...THEMES.map((t) => ({ id: t.id as Theme | null, libelle: t.libelle }))].map((t) => (
                <button key={t.id ?? 'tous'} type="button" aria-pressed={f.theme === t.id} onClick={() => maj({ theme: t.id })}
                  className={`rounded-full px-2.5 py-1 font-texte text-caption ${f.theme === t.id ? 'bg-primary-container font-bold text-on-primary-container shadow-sm' : 'bg-surface-container-low text-on-surface-variant hover:bg-secondary-container'}`}>
                  {t.libelle}
                </button>
              ))}
            </div>
          </fieldset>
          {filtresSecondaires}
          <button type="button" onClick={toutEffacer} className="btn bg-surface-container py-2.5 text-on-surface hover:bg-surface-container-high">
            <Icone nom="restart_alt" className="text-[18px]" /> Réinitialiser les filtres
          </button>
        </aside>

        <section className="col-span-12 flex flex-col gap-space-md lg:col-span-9" aria-label="Résultats">
          <div className="flex flex-col items-start justify-between gap-space-sm rounded-2xl bg-surface-container-lowest p-space-md shadow-doux md:flex-row md:items-center">
            <p className="flex items-center gap-space-sm font-titre text-headline-sm" aria-live="polite">
              <span className="h-2.5 w-2.5 rounded-full bg-secondary" />
              {chargement ? 'Chargement…' : `${resultats.length} produit${resultats.length > 1 ? 's' : ''} disponible${resultats.length > 1 ? 's' : ''}`}
            </p>
            <label className="relative hidden items-center gap-3 lg:flex">
              <span className="font-texte text-caption text-on-surface-variant">Trier par :</span>
              <select value={f.tri} onChange={(e) => maj({ tri: e.target.value === 'pertinence' ? null : e.target.value })} className="h-10 cursor-pointer appearance-none rounded-lg bg-surface-container pl-3 pr-8 font-texte text-label-lg focus:outline-none focus:ring-1 focus:ring-primary">
                {TRIS.map((t) => <option key={t.id} value={t.id}>{t.libelle}</option>)}
              </select>
              <Icone nom="expand_more" className="pointer-events-none absolute right-2 text-[18px]" />
            </label>
          </div>
          {actifs.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 px-1">
              <span className="font-texte text-caption text-on-surface-variant">Filtres actifs :</span>
              {actifs.map((a) => (
                <button key={a.libelle} type="button" onClick={a.retirer} className="pastille bg-surface-container-highest text-on-surface hover:bg-error-container" aria-label={`Retirer le filtre ${a.libelle}`}>
                  {a.libelle} <Icone nom="close" className="text-[14px]" />
                </button>
              ))}
              <button type="button" onClick={toutEffacer} className="ml-1 font-texte text-caption text-primary hover:underline">Effacer tout</button>
            </div>
          )}

          {chargement ? (
            <Chargement />
          ) : resultats.length > 0 ? (
            <div className="grid grid-cols-1 gap-gutter sm:grid-cols-2 xl:grid-cols-3">
              {resultats.map((p) => <CarteProduit key={p.id} produit={p} />)}
            </div>
          ) : (
            <div className="rounded-2xl bg-surface-container-lowest shadow-doux">
              <EtatVide
                icone="search_off"
                titre={enVente.length === 0 ? 'Les premiers jeux arrivent bientôt' : 'Aucun jeu ne correspond'}
                texte={enVente.length === 0 ? 'Nos PDF sont en cours de relecture avant leur mise en vente. En attendant, les activités gratuites sont déjà disponibles.' : 'Essayez d’autres mots-clés ou retirez un filtre pour découvrir nos activités.'}
                action={enVente.length === 0
                  ? <Link to="/activites-gratuites" className="btn-primaire">Voir les activités gratuites</Link>
                  : <button type="button" onClick={toutEffacer} className="btn-primaire">Voir tout le catalogue</button>}
              />
            </div>
          )}

          {prochains.length > 0 && (
            <div className="mt-space-lg">
              <h2 className="mb-1 font-titre text-headline-sm">Bientôt disponibles</h2>
              <p className="mb-space-md font-texte text-body-sm text-on-surface-variant">Ces produits sont en cours de création ou de relecture. Ils ne sont pas encore en vente.</p>
              <div className="grid grid-cols-1 gap-gutter opacity-90 sm:grid-cols-2 xl:grid-cols-3">
                {prochains.map((p) => <CarteProduit key={p.id} produit={p} />)}
              </div>
            </div>
          )}
        </section>
      </div>

      <div className="mt-space-xl grid grid-cols-1 gap-gutter rounded-2xl bg-surface-container-lowest p-space-lg shadow-doux md:grid-cols-3">
        {[
          { i: 'eco', f: 'bg-secondary-container text-on-secondary-container', t: 'Papier standard 80 g', x: 'Les pages de jeu sont pensées pour le papier de maison : traits nets, sans grands aplats noirs.' },
          { i: 'task_alt', f: 'bg-primary-container text-on-primary-container', t: 'Solutions vérifiées', x: 'Chaque labyrinthe, grille et suite logique est vérifié par un programme, puis le PDF est relu avant sa mise en vente.' },
          { i: 'support_agent', f: 'bg-tertiary-container text-on-tertiary-container', t: 'Un souci avec un fichier ?', x: 'Lien perdu ou problème d’impression : demandez de nouveaux liens ou écrivez-nous via la page Contact.' },
        ].map((c) => (
          <div key={c.t} className="flex items-start gap-space-sm">
            <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${c.f}`}><Icone nom={c.i} className="text-[26px]" /></span>
            <div>
              <h3 className="mb-0.5 font-titre text-title-md">{c.t}</h3>
              <p className="font-texte text-body-sm text-on-surface-variant">{c.x}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
