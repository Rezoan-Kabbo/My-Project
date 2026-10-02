'use server';

import db, { mapRowToCamelCase } from '@/lib/db';
import { User } from '@/lib/types';
import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import bcrypt from 'bcryptjs';
import { createSession, deleteSession, verifySession } from '@/lib/auth';

export async function submitReview(formData: FormData) {
  // Validate authentication before taking action
  const session = await verifySession();
  if (!session) {
    throw new Error('Not authenticated');
  }

  const movieId = parseInt(formData.get('movieId') as string, 10);
  const rating = parseInt(formData.get('rating') as string, 10);
  const comment = formData.get('comment') as string;

  // --- Explicit Transaction Control ---
  // Uses a dedicated client and the add_review stored procedure.
  // The procedure inserts the review AND updates the movie's calculated_rating.
  // If any step fails, the transaction is rolled back.
  const client = await db.getClient();
  try {
    await client.query('BEGIN');
    await client.query('CALL add_review($1, $2, $3, $4)', [movieId, session.userId, rating, comment]);
    await client.query('COMMIT');
  } catch (e) {
    await client.query('ROLLBACK');
    throw e;
  } finally {
    client.release();
  }

  revalidatePath(`/movie/${movieId}`);
}

export async function registerUser(formData: FormData) {
  const username = formData.get('username') as string;
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  // Simple validation
  if (!username || !email || !password) {
    throw new Error('Missing fields');
  }

  // Hash password with bcrypt
  const salt = await bcrypt.genSalt(10);
  const passwordHash = await bcrypt.hash(password, salt);

  // --- Explicit Transaction Control ---
  // Step 1: Insert the new user
  // Step 2: Create a default watchlist for the user
  // If any step fails, everything is rolled back.
  const client = await db.getClient();
  let newUser: User;
  try {
    await client.query('BEGIN');

    // Step 1: Insert user
    const res = await client.query(
      'INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3) RETURNING user_id AS id, username, email, password_hash, account_role, profile_picture_url, created_at',
      [username, email, passwordHash]
    );
    newUser = mapRowToCamelCase<User>(res.rows[0]);

    // Step 2: Create default watchlist for the new user
    await client.query(
      "INSERT INTO watchlists (user_id, list_name) VALUES ($1, 'My Watchlist')",
      [newUser.id]
    );

    await client.query('COMMIT');
  } catch (e) {
    await client.query('ROLLBACK');
    throw e;
  } finally {
    client.release();
  }

  // Create JWT session token
  await createSession(newUser.id, newUser.accountRole);
  redirect('/');
}

export async function loginUser(formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  const res = await db.query('SELECT user_id AS id, username, email, password_hash, account_role, profile_picture_url, created_at FROM users WHERE email = $1', [email]);
  const user = res.rows.length > 0 ? mapRowToCamelCase<User>(res.rows[0]) : null;

  if (!user) {
    throw new Error('User not found'); // Normally handled gracefully in UI
  }

  // Compare hashed passwords
  const passwordMatch = await bcrypt.compare(password, user.passwordHash);
  if (!passwordMatch) {
    throw new Error('Invalid credentials');
  }

  // Set the JWT cookie token
  await createSession(user.id, user.accountRole);
  redirect('/'); // Redirect back to home
}

export async function logoutUser() {
  await deleteSession();
  redirect('/login');
}
