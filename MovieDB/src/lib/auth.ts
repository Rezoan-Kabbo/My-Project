import { SignJWT, jwtVerify } from 'jose';
import { cookies } from 'next/headers';

const SevenDaysinMilliSecond = 7 * 24 * 60 * 60 * 1000
const secretKey = process.env.JWT_SECRET || 'super-secret-key-12345';
const encodedKey = new TextEncoder().encode(secretKey);

export async function createSession(userId: number, role: string) {
  const expiresAt = new Date(Date.now() + SevenDaysinMilliSecond); // 7 days
  const session = await new SignJWT({ userId, role })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('7d')
    .sign(encodedKey);

  const cookieStore = await cookies();
  cookieStore.set('session', session, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    expires: expiresAt,
    sameSite: 'lax',
    path: '/',
  });
}

export async function verifySession() {
  const cookieStore = await cookies();
  const session = cookieStore.get('session')?.value;

  if (!session) return null;

  try {
    const { payload } = await jwtVerify(session, encodedKey, {
      algorithms: ['HS256'],
    });
    return payload as { userId: number; role: string };
  } catch (error) {
    console.error('Failed to verify session');
    return null;
  }
}

export async function deleteSession() {
  const cookieStore = await cookies();
  cookieStore.delete('session');
}
