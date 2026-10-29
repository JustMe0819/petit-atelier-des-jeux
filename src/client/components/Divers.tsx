import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Icone } from './Icone';
import { aCompleter } from '../lib/boutique';

export function Chargement({ texte = 'Chargement…' }: { texte?: string }) {
  return (
    <div role="status" className="flex items-center justify-center gap-2 py-16 font-texte text-body-md text-on-surface-variant">
      <Icone nom="progress_activity" className="animate-spin text-primary" /> {texte}
    </div>
  );
}

export function EtatVide({ icone, titre, texte, action }: { icone: string; titre: string; texte: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-space-sm px-gutter-mobile py-space-xl text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-surface-container-high text-primary">
        <Icone nom={icone} className="text-[32px]" />
      </div>
      <h2 className="font-titre text-title-md">{titre}</h2>
      <div className="max-w-md font-texte text-body-sm text-on-surface-variant">{texte}</div>
      {action}
    </div>
  );
}

export function Alerte({ type = 'info', children }: { type?: 'info' | 'erreur' | 'succes' | 'attention'; children: ReactNode }) {
  const styles = {
    info: ['bg-tertiary-container/50 text-on-tertiary-container', 'info'],
    erreur: ['bg-error-container text-on-error-container', 'error'],
    succes: ['bg-secondary-container text-on-secondary-container', 'check_circle'],
    attention: ['bg-primary-container/60 text-on-primary-container', 'warning'],
  }[type];
  return (
    <div role={type === 'erreur' ? 'alert' : 'status'} className={`flex items-start gap-2 rounded-xl p-space-md font-texte text-body-sm ${styles[0]}`}>
      <Icone nom={styles[1]} className="shrink-0 text-[20px]" />
      <div>{children}</div>
    </div>
  );
}

/** Affiche une valeur de configuration ; si elle n'est pas encore renseignée, elle apparaît surlignée. */
export function Champ({ valeur }: { valeur: string }) {
  if (aCompleter(valeur)) {
    return <mark className="rounded bg-rose px-1 font-bold text-on-rose">[{valeur}]</mark>;
  }
  return <>{valeur}</>;
}

export function FilAriane({ etapes }: { etapes: { a?: string; libelle: string }[] }) {
  return (
    <nav aria-label="Fil d'Ariane" className="py-space-sm">
      <ol className="flex items-center gap-space-xs overflow-x-auto whitespace-nowrap font-texte text-caption text-on-surface-variant sans-barre">
        {etapes.map((e, i) => (
          <li key={i} className="flex shrink-0 items-center gap-space-xs">
            {i > 0 && <span className="text-outline-variant">/</span>}
            {e.a ? (
              <Link to={e.a} className="flex items-center gap-0.5 hover:text-on-surface">
                {i === 0 && <Icone nom="home" className="text-[15px]" />} {e.libelle}
              </Link>
            ) : (
              <span aria-current="page" className="max-w-[220px] truncate font-bold text-on-surface">{e.libelle}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function EnTeteSection({ surtitre, titre, texte, couleur = 'text-secondary', centre = false, action }: { surtitre: string; titre: string; texte?: string; couleur?: string; centre?: boolean; action?: ReactNode }) {
  return (
    <div className={`mb-space-lg flex flex-col gap-3 ${centre ? 'items-center text-center' : 'md:flex-row md:items-end md:justify-between'}`}>
      <div className={centre ? 'max-w-2xl' : ''}>
        <p className={`surtitre font-bold ${couleur}`}>{surtitre}</p>
        <h2 className="mt-1 font-titre text-headline-lg-mobile text-marine md:text-headline-lg">{titre}</h2>
        {texte && centre && <p className="mt-2 font-texte text-body-md text-on-surface-variant">{texte}</p>}
      </div>
      {texte && !centre && <p className="max-w-md font-texte text-body-md text-on-surface-variant">{texte}</p>}
      {action}
    </div>
  );
}
