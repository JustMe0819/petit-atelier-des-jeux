import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { CatalogueReponse, ProduitPublic, StatutServeur } from '../../shared/types';
import { api } from './api';

interface Etat {
  chargement: boolean;
  erreur: string | null;
  produits: ProduitPublic[];
  gratuits: CatalogueReponse['gratuits'];
  statut: StatutServeur | null;
  /** Produits en vente (publiés avec fichiers présents). */
  enVente: ProduitPublic[];
  /** Produits annoncés mais pas encore en vente. */
  aVenir: ProduitPublic[];
  parId: (id: string) => ProduitPublic | undefined;
  recharger: () => void;
}

const Ctx = createContext<Etat | null>(null);

export function CatalogueProvider({ children }: { children: ReactNode }) {
  const [donnees, setDonnees] = useState<CatalogueReponse>({ produits: [], gratuits: [] });
  const [statut, setStatut] = useState<StatutServeur | null>(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState<string | null>(null);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let actif = true;
    setChargement(true);
    Promise.all([api<CatalogueReponse>('/api/catalogue'), api<StatutServeur>('/api/statut')])
      .then(([c, s]) => {
        if (!actif) return;
        setDonnees(c);
        setStatut(s);
        setErreur(null);
      })
      .catch((e) => actif && setErreur(e.message))
      .finally(() => actif && setChargement(false));
    return () => {
      actif = false;
    };
  }, [version]);

  const valeur: Etat = {
    chargement,
    erreur,
    produits: donnees.produits,
    gratuits: donnees.gratuits,
    statut,
    enVente: donnees.produits.filter((p) => p.disponible),
    aVenir: donnees.produits.filter((p) => !p.disponible),
    parId: (id) => donnees.produits.find((p) => p.id === id || p.slug === id),
    recharger: () => setVersion((v) => v + 1),
  };
  return <Ctx.Provider value={valeur}>{children}</Ctx.Provider>;
}

export function useCatalogue() {
  const c = useContext(Ctx);
  if (!c) throw new Error('useCatalogue hors CatalogueProvider');
  return c;
}
