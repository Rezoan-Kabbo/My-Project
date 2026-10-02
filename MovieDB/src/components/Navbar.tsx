import Link from 'next/link';
import { verifySession } from '@/lib/auth';
import { logoutUser } from '@/app/actions';

export default async function Navbar() {
  const session = await verifySession();

  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <Link href="/" className="text-2xl font-bold">
          MovieDB
        </Link>

        {/* Links */}
        <div className="flex space-x-4 items-center">
          <Link href="/" className="hover:underline">Home</Link>
          <Link href="/movies" className="hover:underline">Movies</Link>
          <Link href="/analytics" className="hover:underline">Analytics</Link>
          {session ? (
            <form action={logoutUser} className="inline-block m-0 p-0">
              <button type="submit" className="hover:underline cursor-pointer bg-transparent border-none">
                Logout
              </button>
            </form>
          ) : (
            <Link href="/login" className="hover:underline">Login</Link>
          )}
        </div>
      </div>
    </nav>
  );
}
