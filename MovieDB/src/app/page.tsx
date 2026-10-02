import db, { mapRowToCamelCase } from '@/lib/db';
import { Movie } from '@/lib/types';
import Link from 'next/link';
import MovieDetail from './movie/[id]/page';

export default async function Home() {
  // Fetch movies
  const result = await db.query('SELECT movie_id AS id, title, release_date, duration_mins, description, imdb_rating, calculated_rating, poster_url FROM movies ORDER BY release_date DESC LIMIT 10');
  const movies = result.rows.map(row => mapRowToCamelCase<Movie>(row));

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-4xl font-bold mt-8 mb-4">Welcome to MovieDB</h1>
      <p className="mb-8 text-gray-600">A movie review application built with next.js and postgres.</p>
      
      <h2 className="text-2xl font-semibold mb-4">Latest Movies</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {movies.map((movie) => (
          <div key={movie.id} className="border rounded shadow p-4 bg-white">
            {movie.posterUrl && (
              <img 
                src={movie.posterUrl} 
                alt={movie.title} 
                className="w-full h-64 object-cover rounded mb-4"
              />
              
            )}
            <h3 className="text-xl font-bold">{movie.title}</h3>
            <p className="text-sm text-gray-500 mb-1">
              Released: {movie.releaseDate?.toLocaleDateString()}
            </p>
            <p className="text-sm font-semibold text-gray-700 mb-2">
              User Rating: {movie.calculatedRating ? movie.calculatedRating.toString() : '0.0'}/10
            </p>
            <p className="mb-4 truncate">{movie.description}</p>
            
            <Link 
              href={`/movie/${movie.id}`} 
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 block text-center"
            >
              View Details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
