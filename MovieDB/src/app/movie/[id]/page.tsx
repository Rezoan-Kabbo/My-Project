import db, { mapRowToCamelCase } from '@/lib/db';
import { Movie, Review, Reply } from '@/lib/types';
import { notFound } from 'next/navigation';
import { submitReview } from '@/app/actions';

export default async function MovieDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const movieId = parseInt(id, 10);
  
  if (isNaN(movieId)) return notFound();

  // Fetch the movie
  const movieRes = await db.query('SELECT movie_id AS id, title, release_date, duration_mins, description, imdb_rating, calculated_rating, poster_url FROM movies WHERE movie_id = $1', [movieId]);
  if (movieRes.rows.length === 0) return notFound();
  
  const movie = mapRowToCamelCase<Movie>(movieRes.rows[0]);

  // Use the get_movie_review_count() database function to get the total review count
  const reviewCountRes = await db.query('SELECT get_movie_review_count($1) AS review_count', [movieId]);
  const totalReviewCount: number = reviewCountRes.rows[0].review_count;

  // Fetch Genres
  const genresRes = await db.query(`
    SELECT g.genre_id as id, g.genre_name as "genreName" 
    FROM genres g 
    JOIN movie_genres mg ON g.genre_id = mg.genre_id 
    WHERE mg.movie_id = $1
  `, [movieId]);
  
  const movieGenres = genresRes.rows.map(row => ({
    genre: { id: row.id, genreName: row.genreName }
  }));

  // Fetch Crew
  const crewRes = await db.query(`
    SELECT p.person_id as id, p.name, mc.role_name as "roleName" 
    FROM people p 
    JOIN movie_crew mc ON p.person_id = mc.person_id 
    WHERE mc.movie_id = $1
  `, [movieId]);

  const movieCrew = crewRes.rows.map(row => ({
    roleName: row.roleName,
    person: { id: row.id, name: row.name }
  }));

  // Fetch Reviews
  const reviewsRes = await db.query(`
    SELECT r.review_id AS id, r.movie_id, r.user_id, r.rating, r.comment, r.likes_count, r.review_date, r.updated_at, u.username as review_username 
    FROM reviews r 
    LEFT JOIN users u ON r.user_id = u.user_id 
    WHERE r.movie_id = $1 
    ORDER BY r.review_date DESC
  `, [movieId]);
  
  const rawReviews = reviewsRes.rows.map(row => mapRowToCamelCase<Review & { reviewUsername: string }>(row));
  const reviewIds = rawReviews.length > 0 ? rawReviews.map(r => r.id) : [];

  // Fetch Replies
  let rawReplies: any[] = [];
  if (reviewIds.length > 0) {
    const repliesRes = await db.query(`
      SELECT re.reply_id AS id, re.review_id, re.user_id, re.reply_text, re.reply_date, re.updated_at, u.username as reply_username 
      FROM replies re 
      LEFT JOIN users u ON re.user_id = u.user_id 
      WHERE re.review_id = ANY($1) 
      ORDER BY re.reply_date ASC
    `, [reviewIds]);
    rawReplies = repliesRes.rows.map(row => mapRowToCamelCase<Reply & { replyUsername: string }>(row));
  }

  const movieReviews = rawReviews.map(r => ({
    ...r,
    user: { username: r.reviewUsername },
    replies: rawReplies.filter(re => re.reviewId === r.id).map(re => ({
      ...re,
      user: { username: re.replyUsername }
    }))
  }));

  return (
    <div className="max-w-4xl mx-auto p-4 mt-8 bg-white border rounded shadow">
      {/* Movie Header */}
      <h1 className="text-4xl font-bold mb-2">{movie.title}</h1>
      <div className="text-sm text-gray-500 mb-6 flex gap-4">
        <span>Released: {movie.releaseDate?.toLocaleDateString()}</span>
        <span>Duration: {movie.durationMins} mins</span>
        <span>IMDB: {movie.imdbRating ? movie.imdbRating.toString() : 'N/A'}/10</span>
        <span>User Rating: {movie.calculatedRating ? movie.calculatedRating.toString() : '0.0'}/10</span>
        <span>Reviews: {totalReviewCount}</span>
      </div>

      <div className="flex flex-col md:flex-row gap-8 mb-8">
        {movie.posterUrl && (
          <img 
            src={movie.posterUrl} 
            alt={movie.title} 
            className="w-full md:w-64 rounded shadow-md object-cover"
          />
        )}
        <div>
          <h2 className="text-2xl font-semibold mb-2">Description</h2>
          <p className="mb-4">{movie.description}</p>
          
          <h2 className="text-xl font-semibold mb-2">Genres</h2>
          <div className="flex gap-2 mb-4">
            {movieGenres.map(mg => (
              <span key={mg.genre.id} className="bg-gray-200 px-2 py-1 rounded text-sm">
                {mg.genre.genreName}
              </span>
            ))}
          </div>
        </div>
      </div>

      <hr className="my-8" />

      {/* Cast & Crew */}
      <h2 className="text-2xl font-semibold mb-4">Cast & Crew</h2>
      <ul className="mb-8 list-disc list-inside">
        {movieCrew.map((c, idx) => (
          <li key={idx}>
            <span className="font-semibold">{c.person.name}</span> - {c.roleName}
          </li>
        ))}
      </ul>

      <hr className="my-8" />

      {/* Reviews Section */}
      <h2 className="text-2xl font-semibold mb-4">Reviews</h2>
      
      {/* Add a Review Form */}
      <div className="bg-gray-100 p-4 mb-6 rounded border">
        <h3 className="font-bold mb-2">Leave a Review</h3>
        <form action={submitReview} className="flex flex-col gap-2">
          {/* Hidden input to pass the movie ID to the server */}
          <input type="hidden" name="movieId" value={movie.id} />
          
          <label className="text-sm font-semibold">Rating (1-10)</label>
          <input 
            type="number" 
            name="rating" 
            min="1" 
            max="10" 
            required 
            className="p-2 border rounded w-24" 
            placeholder="10"
          />
          
          <label className="text-sm font-semibold">Comment</label>
          <textarea 
            name="comment" 
            required 
            className="p-2 border rounded w-full h-20" 
            placeholder="What did you think of the movie?"
          />
          
          <button 
            type="submit" 
            className="bg-blue-600 text-white font-bold py-2 px-4 rounded w-32 hover:bg-blue-700"
          >
            Submit
          </button>
        </form>
      </div>

      {movieReviews.length === 0 ? (
        <p className="text-gray-500">No reviews yet.</p>
      ) : (
        <div className="space-y-4">
          {movieReviews.map(review => (
            <div key={review.id} className="border p-4 rounded bg-gray-50 mb-4">
              <div className="flex justify-between mb-2">
                <span className="font-bold">{review.user?.username || 'Anonymous'} - Rating: {review.rating}/10</span>
                <span className="text-sm text-gray-500">{review.reviewDate?.toLocaleDateString()}</span>
              </div>
              <p className="mb-4">{review.comment}</p>

              {review.replies && review.replies.length > 0 && (
                <div className="ml-8 mt-4 border-l-2 border-gray-300 pl-4 space-y-3">
                  <h4 className="text-sm font-semibold text-gray-600">Replies:</h4>
                  {review.replies.map(reply => (
                    <div key={reply.id} className="bg-white p-3 rounded shadow-sm border text-sm">
                      <div className="flex justify-between mb-1">
                        <span className="font-bold text-gray-800">{reply.user?.username || 'Anonymous'}</span>
                        <span className="text-xs text-gray-400">{reply.replyDate?.toLocaleDateString()}</span>
                      </div>
                      <p>{reply.replyText}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
