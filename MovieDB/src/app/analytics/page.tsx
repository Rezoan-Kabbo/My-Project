import React from 'react';
import db from '@/lib/db';
import Link from 'next/link';

// --- Database Fetching Functions ---
async function getTopMoviesByGenre() {
  const query = `
    WITH RankedMovies AS (
      SELECT 
        g.genre_name,
        m.movie_id,
        m.title,
        m.calculated_rating,
        m.poster_url,
        ROW_NUMBER() OVER (PARTITION BY g.genre_id ORDER BY m.calculated_rating DESC) as rank
      FROM genres g
      JOIN movie_genres mg ON g.genre_id = mg.genre_id
      JOIN movies m ON mg.movie_id = m.movie_id
      WHERE m.calculated_rating > 0
    )
    SELECT genre_name, movie_id, title, calculated_rating, poster_url
    FROM RankedMovies
    WHERE rank = 1
    ORDER BY genre_name;
  `;
  const res = await db.query(query);
  return res.rows;
}

async function getProlificPeople() {
  const query = `
    SELECT 
      p.name,
      mc.role_name,
      COUNT(mc.movie_id) as movie_count,
      ROUND(AVG(m.calculated_rating), 1) as avg_rating
    FROM people p
    JOIN movie_crew mc ON p.person_id = mc.person_id
    JOIN movies m ON mc.movie_id = m.movie_id
    GROUP BY p.person_id, p.name, mc.role_name
    HAVING COUNT(mc.movie_id) >= 1
    ORDER BY movie_count DESC, avg_rating DESC
    LIMIT 6;
  `;
  const res = await db.query(query);
  return res.rows;
}

async function getActiveMembers() {
  const query = `
    SELECT 
      u.username,
      u.profile_picture_url,
      COUNT(DISTINCT r.review_id) as review_count,
      COUNT(DISTINCT rep.reply_id) as reply_count,
      (COUNT(DISTINCT r.review_id) + COUNT(DISTINCT rep.reply_id)) as total_activity
    FROM users u
    LEFT JOIN reviews r ON u.user_id = r.user_id
    LEFT JOIN replies rep ON u.user_id = rep.user_id
    GROUP BY u.user_id, u.username, u.profile_picture_url
    HAVING (COUNT(DISTINCT r.review_id) + COUNT(DISTINCT rep.reply_id)) > 0
    ORDER BY total_activity DESC
    LIMIT 6;
  `;
  const res = await db.query(query);
  // Ensure types since COUNT returns strings in node-postgres sometimes
  return res.rows.map(row => ({
    ...row,
    review_count: parseInt(row.review_count, 10),
    reply_count: parseInt(row.reply_count, 10),
    total_activity: parseInt(row.total_activity, 10),
  }));
}

export const metadata = {
  title: 'Analytics - MovieDB',
  description: 'Statistics and complex data aggregations for MovieDB',
};

export default async function AnalyticsPage() {
  // Fetch all queries in parallel for better performance
  const [topMovies, prolificPeople, activeMembers] = await Promise.all([
    getTopMoviesByGenre(),
    getProlificPeople(),
    getActiveMembers(),
  ]);

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header Section */}
        <div className="mb-12 text-center pb-8 border-b border-gray-200">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl mb-4">
            Platform Analytics
          </h1>
          <p className="text-xl text-gray-500 max-w-2xl mx-auto">
            Top rated contents and most active members 
          </p>
        </div>

        {/* Top Movies By Genre Grid */}
        <section className="mb-16">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              Top Rated Movies by Genre
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {topMovies.map((movie, idx) => (
              <Link key={idx} href={`/movie/${movie.movie_id}`} className="group relative block bg-white rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100">
                <div className="aspect-[2/3] w-full overflow-hidden bg-gray-200 relative">
                  {movie.poster_url ? (
                    <img 
                      src={movie.poster_url} 
                      alt={movie.title} 
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center text-gray-400 p-4 text-center">
                      <svg className="w-12 h-12 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      No Poster
                    </div>
                  )}
                  <div className="absolute top-3 left-3 flex flex-col gap-2">
                    <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg backdrop-blur-sm border border-blue-500/30">
                      {movie.genre_name}
                    </span>
                  </div>
                  <div className="absolute top-3 right-3 flex items-center gap-1 bg-black/70 text-white rounded-full px-2 py-1 shadow-lg backdrop-blur-sm">
                    <span className="text-yellow-400 text-sm">★</span>
                    <span className="text-sm font-bold">{parseFloat(movie.calculated_rating).toFixed(1)}</span>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-gray-900 line-clamp-1 group-hover:text-blue-600 transition-colors">
                    {movie.title}
                  </h3>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Lower Grid: Prolific People & Active Members */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Prolific People */}
          <section className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <svg className="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    Top Talents
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">Highest movie counts by role.</p>
                </div>
              </div>
            </div>
            
            <ul className="divide-y divide-gray-100">
              {prolificPeople.map((person, idx) => (
                <li key={idx} className="p-4 hover:bg-gray-50 transition-colors flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg">
                      {person.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{person.name}</p>
                      <p className="text-xs text-gray-500 font-medium">{person.role_name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <p className="text-lg font-bold text-gray-900">{person.movie_count}</p>
                      <p className="text-[10px] uppercase tracking-wider text-gray-500 font-bold">Movies</p>
                    </div>
                    <div className="text-center w-12 border-l border-gray-200 pl-4">
                      <p className="text-sm font-bold text-gray-700 flex items-center justify-center gap-1">
                        {parseFloat(person.avg_rating).toFixed(1)} <span className="text-yellow-400 text-[10px]">★</span>
                      </p>
                      <p className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">Avg</p>
                    </div>
                  </div>
                </li>
              ))}
              {prolificPeople.length === 0 && (
                <li className="p-8 text-center text-gray-500">No data found.</li>
              )}
            </ul>
          </section>

          {/* Active Members */}
          <section className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                    Top Contributors
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">Users with the most engagements.</p>
                </div>
              </div>
            </div>
            
            <ul className="divide-y divide-gray-100">
              {activeMembers.map((member, idx) => (
                <li key={idx} className="p-4 hover:bg-gray-50 transition-colors flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {member.profile_picture_url ? (
                      <img src={member.profile_picture_url} alt={member.username} className="w-10 h-10 rounded-full object-cover border border-gray-200"/>
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-lg">
                        {member.username.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <p className="font-semibold text-gray-900">@{member.username}</p>
                      <div className="flex gap-2 text-xs text-gray-500 mt-0.5">
                        <span className="flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                          {member.review_count} Reviews
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" /></svg>
                          {member.reply_count} Replies
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="inline-flex items-center bg-gray-100 text-gray-800 text-xs font-bold px-2.5 py-0.5 rounded-full">
                      {member.total_activity} Total
                    </span>
                    {idx === 0 && <span className="text-[10px] text-yellow-600 font-bold mt-1 uppercase">#1 Contributor</span>}
                  </div>
                </li>
              ))}
              {activeMembers.length === 0 && (
                <li className="p-8 text-center text-gray-500">No data found.</li>
              )}
            </ul>
          </section>

        </div>
      </div>
    </div>
  );
}
