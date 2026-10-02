import Link from 'next/link';
import { registerUser } from '@/app/actions';

export default function Register() {
  return (
    <div className="max-w-md mx-auto mt-20 p-6 bg-white border rounded shadow">
      <h1 className="text-2xl font-bold mb-6 text-center">Create an Account</h1>
      <form action={registerUser} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Username</label>
          <input 
            type="text" 
            name="username"
            required
            className="mt-1 block w-full p-2 border rounded" 
            placeholder="cinemafan99"
          />
        </div>
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
          Register
        </button>
      </form>
      <p className="mt-4 text-center text-sm">
        Already have an account? <Link href="/login" className="text-blue-600 hover:underline">Login here</Link>
      </p>
    </div>
  );
}
