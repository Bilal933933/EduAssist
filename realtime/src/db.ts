import { Pool } from "pg";
import { config } from "./config";

const pool = new Pool({ connectionString: config.databaseUrl });

export async function ensureSchema(): Promise<void> {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS rt_users (
      id BIGSERIAL PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      name TEXT,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMPTZ DEFAULT now()
    )
  `);
}

export async function findUserByEmail(email: string) {
  const res = await pool.query(
    "SELECT id, email, name, password_hash FROM rt_users WHERE email = $1",
    [email],
  );
  return res.rows[0] ?? null;
}

export async function createUser(
  email: string,
  name: string | null,
  passwordHash: string,
) {
  const res = await pool.query(
    "INSERT INTO rt_users (email, name, password_hash) VALUES ($1, $2, $3) RETURNING id, email, name",
    [email, name, passwordHash],
  );
  return res.rows[0];
}
