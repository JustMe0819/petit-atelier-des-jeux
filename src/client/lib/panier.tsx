import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useCatalogue } from './catalogue';
import type { ProduitPublic } from '../../shared/types';

/**
 * Panier : on ne conserve que les identifiants des produits (dans le navigateur).
 * Les prix affichés viennent du catalogue et sont toujours recalculés par le serveur au paiement.
 * Un produit numérique s'achète une seule fois : pas de quantité > 1 (l'impression est illimitée pour le foyer).
 */
const CLE = 'pad-panier-v1';

interface Notification {
  id: number;
  titre: string;
  message: string;
}

interface Etat {
  ids: string[];
  articles: ProduitPublic[];
  retires: string[];
  nombre: number;
  sousTotalCentimes: number;
  ajouter: (id: string) => { ok: boolean; message: string };
  retirer: (id: string) => void;
  vider: () => void;
  contient: (id: string) => boolean;
  notification: Notification | null;
  fermerNotification: () => void;
}

const Ctx = createContext<Etat | null>(null);

function lire(): string[] {
  try {
    const v = JSON.parse(localStorage.getItem(CLE) ?? '[]');
    return Array.isArray(v) ? v.filter((x) => typeof x === 'string').slice(0, 20) : [];
  } catch {
    return [];
  }
}

export function PanierProvider({ children }: { children: ReactNode }) {
  const { parId, chargement, produits } = useCatalogue();
  const [ids, setIds] = useState<string[]>(lire);
  const [retires, setRetires] = useState<string[]>([]);
  const [notification, setNotification] = useState<Notification | null>(null);

  useEffect(() => {
    try {
      localStorage.setItem(CLE, JSON.stringify(ids));
    } catch {
      /* navigation privée : le panier reste en mémoire */
    }
  }, [ids]);

  // Une fois le catalogue chargé, on retire ce qui n'est plus en vente (et on le signale).
  useEffect(() => {
    if (chargement || produits.length === 0) return;
    const invalides = ids.filter((id) => !parId(id)?.disponible);
    if (invalides.length) {
      setRetires(invalides.map((id) => parId(id)?.titre ?? id));
      setIds((a) => a.filter((id) => !invalides.includes(id)));
    }
  }, [chargement, produits, ids, parId]);

  const articles = useMemo(() => ids.map((id) => parId(id)).filter((p): p is ProduitPublic => !!p && p.disponible), [ids, parId]);

  const ajouter = useCallback(
    (id: string) => {
      const p = parId(id);
      if (!p || !p.disponible) return { ok: false, message: "Ce produit n'est pas encore disponible." };
      if (ids.includes(p.id)) return { ok: false, message: 'Déjà dans votre panier.' };
      const coffret = ids.map((x) => parId(x)).find((c) => c?.composants.includes(p.id));
      if (coffret) return { ok: false, message: `Déjà inclus dans « ${coffret.titre} ».` };
      let message = 'Ajouté à votre panier';
      if (p.composants.length) {
        const inclus = ids.filter((x) => p.composants.includes(x));
        if (inclus.length) message = `Ajouté — ${inclus.length} produit(s) déjà inclus dans le coffret ont été retirés du panier`;
        setIds((a) => [...a.filter((x) => !p.composants.includes(x)), p.id]);
      } else {
        setIds((a) => [...a, p.id]);
      }
      setNotification({ id: Date.now(), titre: p.titre, message });
      return { ok: true, message };
    },
    [ids, parId],
  );

  const valeur: Etat = {
    ids,
    articles,
    retires,
    nombre: articles.length,
    sousTotalCentimes: articles.reduce((s, p) => s + p.prixCentimes, 0),
    ajouter,
    retirer: (id) => setIds((a) => a.filter((x) => x !== id)),
    vider: () => setIds([]),
    contient: (id) => ids.includes(id),
    notification,
    fermerNotification: () => setNotification(null),
  };
  return <Ctx.Provider value={valeur}>{children}</Ctx.Provider>;
}

export function usePanier() {
  const c = useContext(Ctx);
  if (!c) throw new Error('usePanier hors PanierProvider');
  return c;
}
