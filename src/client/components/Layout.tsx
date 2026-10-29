import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Icone } from './Icone';
import { useCatalogue } from '../lib/catalogue';
import { usePanier } from '../lib/panier';
import { BOUTIQUE } from '../lib/boutique';
import { THEMES } from '../../shared/libelles';

const NAV = [
  { a: '/', libelle: 'Accueil', exact: true },
  { a: '/boutique', libelle: 'Tous les jeux' },
  { a: '/boutique?type=packs', libelle: 'Packs de jeux' },
  { a: '/boutique?type=cahiers', libelle: "Cahiers d'activités" },
  { a: '/activites-gratuites', libelle: 'Coin gratuit', badge: 'Offert' },
  { a: '/a-propos', libelle: 'À propos' },
  { a: '/faq', libelle: 'FAQ & Contact' },
];

function estActif(lien: string, pathname: string, search: string, exact?: boolean) {
  const [chemin, requete] = lien.split('?');
  if (exact) return pathname === chemin;
  if (requete) return pathname === chemin && search.includes(requete);
  if (chemin === '/boutique') return pathname === '/boutique' && !/type=(packs|cahiers)/.test(search);
  return pathname.startsWith(chemin);
}

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/" className="group flex items-center gap-space-sm" aria-label="Petit Atelier des Jeux — accueil">
      <span className="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-primary-container/60 shadow-doux">
        <img src="/images/decor/renard-logo.webp" alt="" className="h-11 w-11 object-cover" width={44} height={44} />
      </span>
      <span className="flex flex-col">
        <span className="font-titre text-headline-sm font-extrabold leading-tight tracking-tight text-marine">Petit Atelier des Jeux</span>
        {!compact && <span className="font-texte text-caption text-on-surface-variant">Jeux &amp; cahiers d'activités à imprimer (6-8 ans)</span>}
      </span>
    </Link>
  );
}

function BandeauMode() {
  const { statut } = useCatalogue();
  if (!statut || statut.paiement === 'stripe_live') return null;
  const textes = {
    simulation: 'Mode démonstration : les paiements sont simulés, aucun argent réel n’est débité.',
    stripe_test: 'Mode test Stripe : aucun paiement réel. Carte de test : 4242 4242 4242 4242.',
    non_configure: 'Boutique en préparation : le paiement en ligne n’est pas encore activé.',
  } as const;
  return (
    <div role="status" className="bg-inverse-surface px-4 py-1.5 text-center font-texte text-caption font-bold text-inverse-on-surface">
      <Icone nom="science" className="mr-1 align-[-3px] text-[16px]" />
      {textes[statut.paiement]}
    </div>
  );
}

function Recherche({ className = '' }: { className?: string }) {
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const envoyer = (e: FormEvent) => {
    e.preventDefault();
    navigate(q.trim() ? `/boutique?q=${encodeURIComponent(q.trim())}` : '/boutique');
  };
  return (
    <form role="search" onSubmit={envoyer} className={`relative flex items-center ${className}`}>
      <Icone nom="search" className="pointer-events-none absolute left-3 text-[20px] text-outline" />
      <label htmlFor="recherche-entete" className="sr-only">Rechercher un jeu</label>
      <input
        id="recherche-entete"
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Rechercher un jeu, un thème..."
        className="h-11 w-full rounded-full bg-surface-container-lowest pl-10 pr-4 font-texte text-body-sm text-on-surface shadow-doux placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary-container"
      />
    </form>
  );
}

function EnteteBureau() {
  const { nombre } = usePanier();
  const { pathname, search } = useLocation();
  return (
    <div className="hidden lg:block">
      <div className="bg-secondary-container text-on-secondary-container">
        <div className="conteneur flex h-8 items-center justify-center gap-space-sm">
          <Icone nom="bolt" className="text-[16px]" />
          <p className="text-center font-texte text-caption font-bold tracking-wide">
            100 % numérique • Téléchargement après paiement • Prêt à imprimer chez soi en format A4
          </p>
        </div>
      </div>
      <div className="conteneur">
        <div className="flex h-20 items-center justify-between gap-space-md">
          <Logo />
          <Recherche className="mx-space-lg max-w-sm flex-1" />
          <div className="flex items-center gap-space-sm">
            <Link to="/mes-telechargements" className="flex items-center gap-space-xs rounded-lg px-3 py-2 text-on-surface-variant transition-colors hover:bg-surface-container hover:text-on-surface">
              <Icone nom="download" className="text-[20px]" />
              <span className="font-texte text-label-lg">Téléchargements</span>
            </Link>
            <Link to="/panier" className="flex items-center gap-space-xs rounded-lg bg-primary-container px-4 py-2 text-on-primary-container shadow-doux transition-colors hover:bg-primary-fixed-dim">
              <Icone nom="shopping_bag" className="text-[20px]" />
              <span className="font-texte text-label-lg">Panier</span>
              <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-surface-container-lowest px-1 font-texte text-caption font-bold text-on-surface" aria-label={`${nombre} article(s)`}>
                {nombre}
              </span>
            </Link>
          </div>
        </div>
        <div className="flex h-12 items-center justify-between">
          <nav aria-label="Navigation principale" className="flex items-center gap-space-xs">
            {NAV.map((l) => {
              const actif = estActif(l.a, pathname, search, l.exact);
              return (
                <Link
                  key={l.a}
                  to={l.a}
                  aria-current={actif ? 'page' : undefined}
                  className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-texte text-body-sm transition-colors ${
                    actif ? 'bg-surface-container font-bold text-on-surface' : 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface'
                  }`}
                >
                  {l.libelle}
                  {l.badge && <span className="rounded-full bg-secondary-container px-1.5 py-0.5 font-texte text-caption font-bold leading-none text-on-secondary-container">{l.badge}</span>}
                </Link>
              );
            })}
          </nav>
          <div className="flex items-center gap-space-xs text-on-surface-variant">
            <Icone nom="print" className="text-[18px] text-secondary" />
            <span className="font-texte text-caption font-medium">Pensé pour les imprimantes de maison</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function EnteteMobile({ ouvrirMenu }: { ouvrirMenu: () => void }) {
  const { nombre } = usePanier();
  return (
    <div className="flex h-16 items-center justify-between px-gutter-mobile md:px-margin lg:hidden">
      <Link to="/" className="flex items-center gap-space-sm" aria-label="Petit Atelier des Jeux — accueil">
        <img src="/images/decor/renard-logo.webp" alt="" className="h-10 w-10 rounded-xl bg-primary-container/60 object-cover" width={40} height={40} />
        <span className="font-titre text-title-md font-extrabold tracking-tight text-marine">Petit Atelier des Jeux</span>
      </Link>
      <div className="flex items-center gap-space-xs">
        <Link to="/panier" aria-label={`Panier, ${nombre} article(s)`} className="relative flex h-11 w-11 items-center justify-center rounded-full text-on-surface hover:bg-surface-container-high">
          <Icone nom="shopping_bag" className="text-[24px]" />
          {nombre > 0 && (
            <span className="absolute right-1 top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-container px-1 font-texte text-label-md text-on-primary-container shadow-sm">{nombre}</span>
          )}
        </Link>
        <button type="button" onClick={ouvrirMenu} aria-label="Ouvrir le menu" className="flex h-11 w-11 items-center justify-center rounded-full text-on-surface hover:bg-surface-container-high">
          <Icone nom="menu" className="text-[24px]" />
        </button>
      </div>
    </div>
  );
}

function Tiroir({ ouvert, fermer }: { ouvert: boolean; fermer: () => void }) {
  useEffect(() => {
    if (!ouvert) return;
    const touche = (e: KeyboardEvent) => e.key === 'Escape' && fermer();
    document.addEventListener('keydown', touche);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', touche);
      document.body.style.overflow = '';
    };
  }, [ouvert, fermer]);

  const lien = 'flex items-center gap-space-sm rounded-lg px-space-sm py-space-sm font-titre text-title-md text-on-surface hover:bg-surface-container';
  return (
    <>
      <div className={`fixed inset-0 z-[60] bg-inverse-surface/40 backdrop-blur-sm transition-opacity lg:hidden ${ouvert ? 'opacity-100' : 'pointer-events-none opacity-0'}`} onClick={fermer} />
      <aside
        aria-label="Menu"
        aria-hidden={!ouvert}
        inert={!ouvert}
        className={`fixed right-0 top-0 z-[70] flex h-full w-[85%] max-w-sm flex-col bg-surface-container-lowest shadow-fort transition-transform duration-300 lg:hidden ${ouvert ? 'translate-x-0' : 'translate-x-full'}`}
      >
        <div className="flex h-16 items-center justify-between bg-surface-container-low px-gutter-mobile">
          <span className="flex items-center gap-space-xs font-titre text-headline-sm">
            <Icone nom="auto_stories" className="text-[22px] text-primary" /> Navigation
          </span>
          <button type="button" onClick={fermer} aria-label="Fermer le menu" className="flex h-11 w-11 items-center justify-center rounded-full text-on-surface-variant hover:bg-surface-container-high">
            <Icone nom="close" />
          </button>
        </div>
        <div className="flex-1 space-y-space-md overflow-y-auto px-gutter-mobile py-space-md" onClick={(e) => (e.target as HTMLElement).closest('a') && fermer()}>
          <div className="space-y-space-xs">
            <p className="surtitre px-space-xs text-on-surface-variant">Explorer</p>
            <Link to="/" className={lien}><Icone nom="home" className="text-primary" /> Accueil</Link>
            <Link to="/boutique" className={lien}><Icone nom="grid_view" className="text-primary" /> Tous les jeux</Link>
            <Link to="/boutique?type=packs" className={lien}><Icone nom="inventory_2" className="text-primary" /> Packs de jeux</Link>
            <Link to="/boutique?type=cahiers" className={lien}><Icone nom="menu_book" className="text-primary" /> Cahiers d'activités</Link>
            <Link to="/activites-gratuites" className={`${lien} justify-between`}>
              <span className="flex items-center gap-space-sm"><Icone nom="featured_seasonal_and_gifts" className="text-secondary" /> Coin gratuit</span>
              <span className="pastille bg-secondary-container text-on-secondary-container">Offert</span>
            </Link>
            <Link to="/mes-telechargements" className={lien}><Icone nom="download" className="text-primary" /> Mes téléchargements</Link>
          </div>
          <div className="space-y-space-xs">
            <p className="surtitre px-space-xs text-on-surface-variant">Par thème (6-8 ans)</p>
            <div className="grid grid-cols-2 gap-space-xs">
              {THEMES.map((t) => (
                <Link key={t.id} to={`/boutique?theme=${t.id}`} className="flex items-center justify-center gap-1 rounded-full bg-surface-container-low px-space-sm py-2 text-center font-texte text-body-sm text-on-surface hover:bg-secondary-container">
                  <Icone nom={t.icone} className="text-[18px]" /> {t.libelle.split(' &')[0]}
                </Link>
              ))}
            </div>
          </div>
          <div className="space-y-space-xs">
            <p className="surtitre px-space-xs text-on-surface-variant">Aide &amp; atelier</p>
            {[
              ['/a-propos', 'info', 'À propos'],
              ['/faq', 'help_outline', 'Questions fréquentes'],
              ['/contact', 'mail', 'Nous écrire'],
              ['/cgv', 'gavel', 'Conditions générales de vente'],
            ].map(([a, i, t]) => (
              <Link key={a} to={a} className="flex items-center gap-space-sm rounded-lg px-space-sm py-2 font-texte text-body-md text-on-surface-variant hover:bg-surface-container">
                <Icone nom={i} className="text-[20px]" /> {t}
              </Link>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
}

function NavBas({ ouvrirMenu }: { ouvrirMenu: () => void }) {
  const { nombre } = usePanier();
  const { pathname } = useLocation();
  const items = [
    { a: '/', i: 'home', t: 'Accueil', actif: pathname === '/' },
    { a: '/boutique', i: 'grid_view', t: 'Catalogue', actif: pathname.startsWith('/boutique') || pathname.startsWith('/produit') },
    { a: '/activites-gratuites', i: 'featured_seasonal_and_gifts', t: 'Gratuit', actif: pathname.startsWith('/activites-gratuites') },
    { a: '/panier', i: 'shopping_bag', t: 'Panier', actif: pathname.startsWith('/panier') },
  ];
  return (
    <nav aria-label="Navigation rapide" className="pb-safe fixed inset-x-0 bottom-0 z-50 bg-surface/90 shadow-[0_-4px_16px_rgba(52,52,58,0.06)] backdrop-blur-xl md:hidden">
      <div className="flex h-16 items-center justify-around px-space-xs">
        {items.map((x) => (
          <Link key={x.a} to={x.a} aria-current={x.actif ? 'page' : undefined} className={`relative flex h-14 w-16 flex-col items-center justify-center gap-0.5 ${x.actif ? 'font-bold text-primary' : 'text-on-surface-variant'}`}>
            <Icone nom={x.i} className="text-[24px]" pleine={x.actif} />
            {x.i === 'shopping_bag' && nombre > 0 && (
              <span className="absolute right-2 top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary-container px-1 font-texte text-[10px] font-bold text-on-primary-container">{nombre}</span>
            )}
            <span className="font-texte text-label-md">{x.t}</span>
          </Link>
        ))}
        <button type="button" onClick={ouvrirMenu} className="flex h-14 w-16 flex-col items-center justify-center gap-0.5 text-on-surface-variant">
          <Icone nom="menu" className="text-[24px]" />
          <span className="font-texte text-label-md">Menu</span>
        </button>
      </div>
    </nav>
  );
}

function Notification() {
  const { notification, fermerNotification } = usePanier();
  useEffect(() => {
    if (!notification) return;
    const t = setTimeout(fermerNotification, 4000);
    return () => clearTimeout(t);
  }, [notification, fermerNotification]);
  return (
    <div aria-live="polite" className="pointer-events-none fixed inset-x-4 bottom-20 z-[55] flex justify-center md:bottom-6 md:left-auto md:right-6 md:justify-end">
      {notification && (
        <div key={notification.id} className="pointer-events-auto flex w-full max-w-sm items-center justify-between gap-3 rounded-xl bg-inverse-surface p-space-sm text-inverse-on-surface shadow-fort">
          <div className="flex min-w-0 items-center gap-space-sm">
            <Icone nom="check_circle" className="shrink-0 text-[22px] text-primary-container" />
            <div className="min-w-0">
              <p className="truncate font-texte text-label-lg">{notification.titre}</p>
              <p className="font-texte text-caption opacity-80">{notification.message}</p>
            </div>
          </div>
          <Link to="/panier" onClick={fermerNotification} className="shrink-0 rounded-lg bg-primary-container px-3 py-1.5 font-texte text-label-md text-on-primary-container">
            Voir le panier
          </Link>
        </div>
      )}
    </div>
  );
}

function PiedDePage() {
  const annee = new Date().getFullYear();
  return (
    <footer className="mt-space-xl">
      {/* Bandeau illustré repris de la planche (dino à gauche, renard à droite). */}
      <div className="relative overflow-hidden bg-surface">
        <div className="conteneur flex min-h-[120px] items-end justify-between gap-4">
          <img src="/images/decor/dino-paysage.webp" alt="" className="hidden h-[110px] w-auto mix-blend-multiply sm:block" loading="lazy" width={300} height={166} />
          <p className="flex-1 py-8 text-center font-titre text-headline-sm font-bold text-marine md:text-headline-md">
            Des jeux pour explorer, réfléchir, créer et s'amuser !
            <span className="mt-1 block text-[18px] text-rose" aria-hidden>♥</span>
          </p>
          <img src="/images/decor/renard-carte.webp" alt="" className="hidden h-[110px] w-auto mix-blend-multiply sm:block" loading="lazy" width={225} height={174} />
        </div>
      </div>
      <div className="bg-surface-container-low">
        <div className="conteneur pb-28 pt-space-xl md:pb-space-lg">
          <div className="mb-space-xl grid grid-cols-1 gap-gutter md:grid-cols-2 lg:grid-cols-4">
            <div>
              <Logo compact />
              <p className="mt-space-sm font-texte text-body-sm text-on-surface-variant">
                Des jeux d'observation, de logique et de réflexion pour offrir aux 6-8 ans des moments calmes et créatifs, loin des écrans.
              </p>
              <p className="mt-space-sm flex items-center gap-space-xs font-texte text-caption font-bold text-secondary">
                <Icone nom="eco" className="text-[20px]" /> Imprimez seulement les pages dont vous avez besoin
              </p>
            </div>
            <div>
              <h2 className="mb-space-sm font-titre text-title-md">Jeux &amp; activités</h2>
              <ul className="space-y-2 font-texte text-body-sm">
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/boutique">Tous les jeux PDF</Link></li>
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/boutique?type=packs">Packs &amp; coffrets</Link></li>
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/boutique?type=cahiers">Cahiers d'activités</Link></li>
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/activites-gratuites">Activités gratuites</Link></li>
              </ul>
            </div>
            <div>
              <h2 className="mb-space-sm font-titre text-title-md">Aide &amp; impression</h2>
              <ul className="space-y-2 font-texte text-body-sm">
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/faq#impression">Conseils d'impression</Link></li>
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/mes-telechargements">Retrouver mes PDF achetés</Link></li>
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/faq">Questions fréquentes</Link></li>
                <li><Link className="text-on-surface-variant hover:text-on-surface" to="/contact">Nous écrire</Link></li>
              </ul>
            </div>
            <div>
              <h2 className="mb-space-xs font-titre text-title-md">Une question ?</h2>
              <p className="mb-space-sm font-texte text-body-sm text-on-surface-variant">L'assistant de la page Contact répond tout de suite aux questions fréquentes. Pour le reste, l'atelier lit chaque message.</p>
              <Link to="/contact" className="btn-secondaire py-2"><Icone nom="mail" className="text-[18px]" /> Nous écrire</Link>
            </div>
          </div>
          <div className="flex flex-col items-center justify-between gap-space-md md:flex-row">
            <div className="flex flex-wrap items-center justify-center gap-x-space-md gap-y-1 font-texte text-caption text-on-surface-variant">
              <span>© {annee} {BOUTIQUE.nom}</span>
              <Link className="hover:text-on-surface hover:underline" to="/mentions-legales">Mentions légales</Link>
              <Link className="hover:text-on-surface hover:underline" to="/cgv">CGV</Link>
              <Link className="hover:text-on-surface hover:underline" to="/confidentialite">Confidentialité</Link>
              <Link className="hover:text-on-surface hover:underline" to="/cookies">Cookies</Link>
              <Link className="hover:text-on-surface hover:underline" to="/contact">Contact</Link>
            </div>
            <div className="flex items-center gap-space-sm rounded-full bg-surface-container px-3 py-1.5">
              <Icone nom="lock" className="text-[18px] text-secondary" />
              <span className="font-texte text-caption font-bold text-on-surface-variant">Paiement sécurisé par Stripe • Aucune donnée bancaire sur notre site</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  const [menu, setMenu] = useState(false);
  const { pathname } = useLocation();
  useEffect(() => {
    setMenu(false);
    window.scrollTo(0, 0);
  }, [pathname]);
  return (
    <div className="flex min-h-screen flex-col">
      <a href="#contenu" className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-[80] focus:rounded-lg focus:bg-primary-container focus:px-4 focus:py-2">
        Aller au contenu
      </a>
      <header className="sticky top-0 z-50 bg-surface/90 shadow-[0_1px_8px_rgba(0,0,0,0.04)] backdrop-blur-xl">
        <BandeauMode />
        <EnteteBureau />
        <EnteteMobile ouvrirMenu={() => setMenu(true)} />
      </header>
      <Tiroir ouvert={menu} fermer={() => setMenu(false)} />
      <main id="contenu" className="flex-1">
        {children}
      </main>
      <PiedDePage />
      <NavBas ouvrirMenu={() => setMenu(true)} />
      <Notification />
    </div>
  );
}


