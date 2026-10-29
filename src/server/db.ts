import { createClient, type Client, type InArgs, type InStatement } from '@libsql/client';

/**
 * Base de données des commandes (libSQL / SQLite).
 * - En ligne (Vercel) : base Turso, via TURSO_DATABASE_URL et TURSO_AUTH_TOKEN.
 * - En local : simple fichier data/boutique.sqlite (aucun compte nécessaire).
 * Toutes les opérations sont asynchrones.
 */
export type Ligne = Record<string, any>;
export type Instruction = { sql: string; args?: unknown[] };

export class Db {
  /** `pret` : promesse des migrations, attendue automatiquement avant chaque requête. */
  constructor(readonly client: Client, private pret: Promise<void> = Promise.resolve()) {}

  private static ligne(colonnes: string[], row: ArrayLike<unknown>): Ligne {
    const o: Ligne = {};
    colonnes.forEach((c, i) => (o[c] = row[i]));
    return o;
  }

  async all<T = Ligne>(sql: string, ...args: unknown[]): Promise<T[]> {
    await this.pret;
    const rs = await this.client.execute({ sql, args: args as InArgs });
    return rs.rows.map((r) => Db.ligne(rs.columns, r) as T);
  }

  async get<T = Ligne>(sql: string, ...args: unknown[]): Promise<T | undefined> {
    return (await this.all<T>(sql, ...args))[0];
  }

  /** Exécute une écriture ; renvoie le nombre de lignes modifiées. */
  async run(sql: string, ...args: unknown[]): Promise<{ changes: number }> {
    await this.pret;
    const rs = await this.client.execute({ sql, args: args as InArgs });
    return { changes: rs.rowsAffected };
  }

  /** Plusieurs écritures en une seule transaction (tout ou rien). */
  async transaction(instructions: Instruction[]): Promise<void> {
    await this.pret;
    await this.client.batch(instructions.map((i) => ({ sql: i.sql, args: (i.args ?? []) as InArgs }) as InStatement), 'write');
  }

  /** Attend la fin des migrations (utile au démarrage pour signaler une base injoignable). */
  prete(): Promise<void> {
    return this.pret;
  }

  close() {
    this.client.close();
  }
}

/** Chaque migration est une liste d'instructions ; elles ne sont jouées qu'une fois. */
const MIGRATIONS: string[][] = [
  [
    `CREATE TABLE IF NOT EXISTS commandes (
       id TEXT PRIMARY KEY,
       email TEXT NOT NULL,
       statut TEXT NOT NULL CHECK (statut IN ('en_attente','payee','echouee','expiree','anomalie')),
       total_centimes INTEGER NOT NULL,
       devise TEXT NOT NULL DEFAULT 'eur',
       mode_paiement TEXT NOT NULL,
       cle_idempotence TEXT NOT NULL UNIQUE,
       empreinte_panier TEXT NOT NULL,
       session_paiement TEXT UNIQUE,
       url_paiement TEXT,
       reference_paiement TEXT,
       montant_paye_centimes INTEGER,
       consentement_cgv_le TEXT NOT NULL,
       consentement_execution_le TEXT NOT NULL,
       texte_consentement TEXT NOT NULL,
       cree_le TEXT NOT NULL,
       payee_le TEXT,
       email_confirmation_le TEXT,
       note TEXT
     )`,
    `CREATE INDEX IF NOT EXISTS idx_commandes_email ON commandes(email)`,
    `CREATE TABLE IF NOT EXISTS lignes_commande (
       commande_id TEXT NOT NULL REFERENCES commandes(id),
       produit_id TEXT NOT NULL,
       titre TEXT NOT NULL,
       prix_centimes INTEGER NOT NULL,
       quantite INTEGER NOT NULL DEFAULT 1 CHECK (quantite = 1),
       PRIMARY KEY (commande_id, produit_id)
     )`,
    `CREATE TABLE IF NOT EXISTS liens_acces (
       empreinte_jeton TEXT PRIMARY KEY,
       commande_id TEXT NOT NULL REFERENCES commandes(id),
       expire_le TEXT NOT NULL,
       cree_le TEXT NOT NULL
     )`,
    `CREATE TABLE IF NOT EXISTS evenements_paiement (
       id TEXT PRIMARY KEY,
       type TEXT NOT NULL,
       recu_le TEXT NOT NULL
     )`,
    `CREATE TABLE IF NOT EXISTS telechargements (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       commande_id TEXT NOT NULL,
       produit_id TEXT NOT NULL,
       type_fichier TEXT NOT NULL,
       le TEXT NOT NULL
     )`,
  ],
  // v2 : la newsletter a été retirée du site.
  [`DROP TABLE IF EXISTS newsletter`],
];

export interface OptionsDb {
  /** URL libSQL : « libsql://…turso.io » en ligne, « file:… » en local, « :memory: » pour les tests. */
  url: string;
  authToken?: string;
}

export function ouvrirDb(o: OptionsDb): Db {
  const client = createClient({ url: o.url, authToken: o.authToken });
  const pret = migrer(new Db(client));
  pret.catch((e) => console.error('[base de données] migration impossible :', e));
  return new Db(client, pret);
}

async function migrer(db: Db): Promise<void> {
  await db.run('PRAGMA foreign_keys = ON');
  await db.run('CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)');
  let ligne = await db.get<{ version: number }>('SELECT version FROM schema_version');
  if (!ligne) {
    await db.run('INSERT INTO schema_version (version) VALUES (0)');
    ligne = { version: 0 };
  }
  let version = Number(ligne.version);
  while (version < MIGRATIONS.length) {
    // La mise à jour du numéro de version est conditionnelle : si deux instances démarrent
    // en même temps, la seconde ne fait rien de plus (toutes les instructions sont idempotentes).
    await db.transaction([
      ...MIGRATIONS[version].map((sql) => ({ sql })),
      { sql: 'UPDATE schema_version SET version = ? WHERE version = ?', args: [version + 1, version] },
    ]);
    version++;
  }
}
