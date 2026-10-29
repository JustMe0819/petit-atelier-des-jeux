interface Props {
  nom: string;
  className?: string;
  pleine?: boolean;
}

/** Icône Material Symbols (police hébergée sur le site, pas de requête vers Google). */
export function Icone({ nom, className = '', pleine = false }: Props) {
  return (
    <span aria-hidden="true" className={`icone ${pleine ? 'icone-pleine' : ''} ${className}`}>
      {nom}
    </span>
  );
}
