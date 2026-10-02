import Link from 'next/link';
import { loginUser } from '@/app/actions';

export default function Login() {
  return (
    <div className="max-w-md mx-auto mt-20 p-6 bg-white border rounded shadow">
      <h1 className="text-2xl font-bold mb-6 text-center">Login to MovieDB</h1>
      <form action={loginUser} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input 
            type="email" 
            name="email"
            required
            className="mt-1 block w-full p-2 border rounded" 
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Password</label>
          <input 
            type="password" 
            name="password"
            required
            className="mt-1 block w-full p-2 border rounded" 
            placeholder="********"
          />
        </div>
        <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 font-bold">
          Sign In
        </button>
      </form>
      <p className="mt-4 text-center text-sm">
        Don't have an account? <Link href="/register" className="text-blue-600 hover:underline">Register here</Link>
      </p>
    </div>
  );
}
