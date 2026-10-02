import 'dotenv/config'
import db from './src/lib/db'
import bcrypt from 'bcryptjs'

async function seedAdmin() {
  const password = 'admin123'
  const salt = await bcrypt.genSalt(10)
  const passwordHash = await bcrypt.hash(password, salt)

  await db.query(
    `INSERT INTO users (username, email, password_hash, account_role)
     VALUES ($1, $2, $3, $4)
     ON CONFLICT (email) DO UPDATE SET password_hash = $3, account_role = $4`,
    ['admin', 'admin@moviedb.com', passwordHash, 'admin']
  )

  console.log('Admin user seeded successfully.')
  db.getPool().end()
}

seedAdmin()
