export class ErreurApi extends Error {
  constructor(public code: string, message: string, public statut: number) {
    super(message);
  }
}

export async function api<T>(url: string, init?: RequestInit & { json?: unknown }): Promise<T> {
  const { json, ...reste } = init ?? {};
  let r: Response;
  try {
    r = await fetch(url, {
      ...reste,
      headers: { ...(json !== undefined ? { 'Content-Type': 'application/json' } : {}), ...reste.headers },
      body: json !== undefined ? JSON.stringify(json) : reste.body,
    });
  } catch {
    throw new ErreurApi('RESEAU', 'Connexion impossible. Vérifiez votre connexion internet et réessayez.', 0);
  }
  const corps = await r.json().catch(() => ({}));
  if (!r.ok) throw new ErreurApi(corps.code ?? 'ERREUR', corps.message ?? 'Une erreur est survenue.', r.status);
  return corps as T;
}
