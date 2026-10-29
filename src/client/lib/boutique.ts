import infos from '../../../config/boutique.json';

export const BOUTIQUE = infos;

/** Une valeur de config/boutique.json est-elle encore un champ à compléter ? */
export const aCompleter = (v: string) => v.startsWith('À COMPLÉTER');
