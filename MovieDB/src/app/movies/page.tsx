import db, { mapRowToCamelCase } from '@/lib/db';
import { Movie } from '@/lib/types';
import Link from 'next/link';

export default async function MoviesPage() {
  const result = await db.query('SELECT movie_id AS id, title, release_date, duration_mins, description, imdb_rating, calculated_rating, poster_url FROM movies ORDER BY release_date DESC');
  const movies = result.rows.map(row => mapRowToCamelCase<Movie>(row));

  return (
    <div className="max-w-7xl mx-auto p-4 mt-8">
      <h1 className="text-3xl font-bold mb-6">All Movies</h1>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
        {movies.map((movie) => (
          <div key={movie.id} className="border rounded shadow p-4 bg-white flex flex-col">
            {movie.posterUrl && (
              <img 
                src={movie.posterUrl} 
                alt={movie.title} 
                className="w-full h-48 object-cover rounded mb-4"
              />
            )}
            <h3 className="text-lg font-bold">{movie.title}</h3>
            <p className="text-sm text-gray-500 mb-2">
              Released: {movie.releaseDate?.toLocaleDateString()}
            </p>
            <p className="text-sm text-gray-500 mb-4 flex-grow font-semibold">
              User Rating: {movie.calculatedRating ? movie.calculatedRating.toString() : '0.0'}/10
            </p>
            
            <Link 
              href={`/movie/${movie.id}`} 
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-center text-sm font-semibold"
            >
              View Details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
