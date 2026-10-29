import { useEffect } from 'react';

export function useTitre(titre: string, description?: string) {
  useEffect(() => {
    document.title = titre ? `${titre} — Petit Atelier des Jeux` : 'Petit Atelier des Jeux — jeux à imprimer pour les 6-8 ans';
    if (description) document.querySelector('meta[name="description"]')?.setAttribute('content', description);
  }, [titre, description]);
}
