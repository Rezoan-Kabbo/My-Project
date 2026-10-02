import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifySession } from '@/lib/auth';

// Add the routes that do not require authentication
const publicRoutes = ['/login', '/register', '/testing'];

export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  const isPublicRoute = publicRoutes.includes(path);

  // Read the session cookie
  const sessionValue = req.cookies.get('session')?.value;
  
  // Need to manually verify JWT in middleware since it runs in the Edge runtime
  let isAuthenticated = false;
  if (sessionValue) {
    try {
      const { jwtVerify } = await import('jose');
      const secretKey = process.env.JWT_SECRET || 'super-secret-key-12345';
      const encodedKey = new TextEncoder().encode(secretKey);
      await jwtVerify(sessionValue, encodedKey);
      isAuthenticated = true;
    } catch (e) {
      isAuthenticated = false;
    }
  }

  if (!isPublicRoute && !isAuthenticated) {
    // If user is trying to access ANY page without being logged in, redirect to login!
    return NextResponse.redirect(new URL('/login', req.nextUrl));
  }

  if (isPublicRoute && isAuthenticated) {
    // If logged in user tries to visit login/register, send them to home
    return NextResponse.redirect(new URL('/', req.nextUrl));
  }

  return NextResponse.next();
}

// Ensure middleware runs on every page (except static files/images/api)
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
