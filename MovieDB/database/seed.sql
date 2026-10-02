-- Seed data for MovieDB
-- Run this after schema.sql to populate the database with sample data.

-- 1. Users (passwords are bcrypt hashes of 'admin123' and 'password123')
-- Note: Run seed_admin.ts instead for proper bcrypt hashing, or use these pre-hashed values.

-- 2. Genres
INSERT INTO genres (genre_name) VALUES 
  ('Action'), ('Sci-Fi'), ('Drama'), ('Thriller'), 
  ('Romance'), ('Comedy'), ('Horror'), ('Adventure')
ON CONFLICT DO NOTHING;

-- 3. Production Companies
INSERT INTO production_companies (company_name) VALUES 
  ('Warner Bros. Pictures'), ('Paramount Pictures')
ON CONFLICT DO NOTHING;

-- 4. Awards
INSERT INTO awards (award_name, year) VALUES 
  ('Academy Award for Best Picture', 2023),
  ('Academy Award for Best Director', 2023)
ON CONFLICT DO NOTHING;

-- 5. People
INSERT INTO people (name, birthdate, bio) VALUES 
  ('Christopher Nolan', '1970-07-30', 'Cinematic visual style.'),
  ('Keanu Reeves', '1964-09-02', 'Actor in The Matrix.'),
  ('Cillian Murphy', '1976-05-25', 'Irish actor.'),
  ('Leonardo DiCaprio', '1974-11-11', 'American actor.')
ON CONFLICT DO NOTHING;

-- 6. Movies
INSERT INTO movies (title, release_date, duration_mins, description, imdb_rating, calculated_rating, poster_url) VALUES 
  ('The Matrix', '1999-03-31', 136, 'A computer hacker learns from mysterious rebels about the true nature of his reality.', 8.7, 9.0, 'https://cdn.posteritati.com/posters/000/000/049/973/the-matrix-md-web.jpg'),
  ('Oppenheimer', '2023-07-21', 180, 'The story of J. Robert Oppenheimer''s role in the development of the atomic bomb.', 8.6, 8.8, 'https://cdn.dribbble.com/userupload/45274008/file/fb11b05b26bb15da646e0878b8d3ce38.jpeg?resize=752x&vertical=center'),
  ('Inception', '2010-07-16', 148, 'A thief who steals corporate secrets through the use of dream-sharing technology.', 8.8, 8.5, 'https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg')
ON CONFLICT DO NOTHING;

-- 7. Movie Genres (using subqueries to look up IDs)
INSERT INTO movie_genres (movie_id, genre_id) VALUES
  ((SELECT movie_id FROM movies WHERE title='The Matrix'), (SELECT genre_id FROM genres WHERE genre_name='Action')),
  ((SELECT movie_id FROM movies WHERE title='The Matrix'), (SELECT genre_id FROM genres WHERE genre_name='Sci-Fi')),
  ((SELECT movie_id FROM movies WHERE title='Oppenheimer'), (SELECT genre_id FROM genres WHERE genre_name='Drama')),
  ((SELECT movie_id FROM movies WHERE title='Inception'), (SELECT genre_id FROM genres WHERE genre_name='Sci-Fi')),
  ((SELECT movie_id FROM movies WHERE title='Inception'), (SELECT genre_id FROM genres WHERE genre_name='Action'))
ON CONFLICT DO NOTHING;

-- 8. Movie Crew
INSERT INTO movie_crew (movie_id, person_id, role_name) VALUES
  ((SELECT movie_id FROM movies WHERE title='The Matrix'), (SELECT person_id FROM people WHERE name='Keanu Reeves'), 'Lead Actor'),
  ((SELECT movie_id FROM movies WHERE title='Oppenheimer'), (SELECT person_id FROM people WHERE name='Christopher Nolan'), 'Director'),
  ((SELECT movie_id FROM movies WHERE title='Oppenheimer'), (SELECT person_id FROM people WHERE name='Cillian Murphy'), 'Lead Actor'),
  ((SELECT movie_id FROM movies WHERE title='Inception'), (SELECT person_id FROM people WHERE name='Christopher Nolan'), 'Director'),
  ((SELECT movie_id FROM movies WHERE title='Inception'), (SELECT person_id FROM people WHERE name='Leonardo DiCaprio'), 'Lead Actor')
ON CONFLICT DO NOTHING;

-- 9. Movie Companies
INSERT INTO movie_companies (movie_id, company_id) VALUES
  ((SELECT movie_id FROM movies WHERE title='The Matrix'), (SELECT company_id FROM production_companies WHERE company_name='Warner Bros. Pictures')),
  ((SELECT movie_id FROM movies WHERE title='Oppenheimer'), (SELECT company_id FROM production_companies WHERE company_name='Paramount Pictures')),
  ((SELECT movie_id FROM movies WHERE title='Inception'), (SELECT company_id FROM production_companies WHERE company_name='Warner Bros. Pictures'))
ON CONFLICT DO NOTHING;

-- 10. Movie Awards
INSERT INTO movie_awards (award_id, movie_id, person_id) VALUES
  ((SELECT award_id FROM awards WHERE award_name='Academy Award for Best Picture'), (SELECT movie_id FROM movies WHERE title='Oppenheimer'), NULL),
  ((SELECT award_id FROM awards WHERE award_name='Academy Award for Best Director'), (SELECT movie_id FROM movies WHERE title='Oppenheimer'), (SELECT person_id FROM people WHERE name='Christopher Nolan'))
ON CONFLICT DO NOTHING;
