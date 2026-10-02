import { Pool } from 'pg';

// Using a connection string from environment variables
const connectionString = process.env.DATABASE_URL;

// Make sure to reuse the connection pool across hot reloads in development
declare global {
  var pgPool: Pool | undefined;
}

const pool = globalThis.pgPool || new Pool({ connectionString });

if (process.env.NODE_ENV !== 'production') {
  globalThis.pgPool = pool;
}

/**
 * Executes a query with proper parameter binding against the pg Pool.
 * Example uses:
 *   const result = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
 *   const users = result.rows;
 */
export const db = {
  query: (text: string, params?: any[]) => pool.query(text, params),
  getPool: () => pool,
  /** Returns a dedicated client from the pool for explicit transaction control (BEGIN/COMMIT/ROLLBACK). */
  getClient: () => pool.connect(),
};

// Convenience wrapper map functions (maps snake_case to camelCase)
export function toCamelCase(str: string): string {
  return str.replace(/([-_][a-z])/ig, ($1) => {
    return $1.toUpperCase()
      .replace('-', '')
      .replace('_', '');
  });
}

// Convert DB returned snake_case row to camelCase properties deeply
export function mapRowToCamelCase<T>(row: any): T {
  if (!row || typeof row !== 'object') return row as T;
  const result: any = {};
  for (const [key, value] of Object.entries(row)) {
    result[toCamelCase(key)] = value;
  }
  return result as T;
}

export default db;
