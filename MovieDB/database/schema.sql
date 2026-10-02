-- MovieDB Schema
-- This file creates all tables, indexes, and foreign keys for the movie database.

-- Users
CREATE TABLE "users" (
    "user_id" SERIAL NOT NULL,
    "username" VARCHAR(50) NOT NULL,
    "email" VARCHAR(100) NOT NULL,
    "password_hash" VARCHAR(255) NOT NULL,
    "account_role" VARCHAR(20) NOT NULL DEFAULT 'user',
    "profile_picture_url" VARCHAR(255),
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "users_pkey" PRIMARY KEY ("user_id")
);

-- Movies
CREATE TABLE "movies" (
    "movie_id" SERIAL NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "release_date" DATE,
    "duration_mins" INTEGER,
    "description" TEXT,
    "imdb_rating" DECIMAL(3,1),
    "calculated_rating" DECIMAL(3,1) DEFAULT 0.0,
    "poster_url" VARCHAR(255),
    CONSTRAINT "movies_pkey" PRIMARY KEY ("movie_id")
);

-- People (actors, directors, etc.)
CREATE TABLE "people" (
    "person_id" SERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "birthdate" DATE,
    "bio" TEXT,
    CONSTRAINT "people_pkey" PRIMARY KEY ("person_id")
);

-- Movie Crew (join table: movies <-> people with role)
CREATE TABLE "movie_crew" (
    "movie_id" INTEGER NOT NULL,
    "person_id" INTEGER NOT NULL,
    "role_name" VARCHAR(50) NOT NULL,
    CONSTRAINT "movie_crew_pkey" PRIMARY KEY ("movie_id","person_id","role_name")
);

-- Genres
CREATE TABLE "genres" (
    "genre_id" SERIAL NOT NULL,
    "genre_name" VARCHAR(50) NOT NULL,
    CONSTRAINT "genres_pkey" PRIMARY KEY ("genre_id")
);

-- Movie Genres (join table)
CREATE TABLE "movie_genres" (
    "movie_id" INTEGER NOT NULL,
    "genre_id" INTEGER NOT NULL,
    CONSTRAINT "movie_genres_pkey" PRIMARY KEY ("movie_id","genre_id")
);

-- Production Companies
CREATE TABLE "production_companies" (
    "company_id" SERIAL NOT NULL,
    "company_name" VARCHAR(255) NOT NULL,
    CONSTRAINT "production_companies_pkey" PRIMARY KEY ("company_id")
);

-- Movie Companies (join table)
CREATE TABLE "movie_companies" (
    "movie_id" INTEGER NOT NULL,
    "company_id" INTEGER NOT NULL,
    CONSTRAINT "movie_companies_pkey" PRIMARY KEY ("movie_id","company_id")
);

-- Reviews
CREATE TABLE "reviews" (
    "review_id" SERIAL NOT NULL,
    "movie_id" INTEGER,
    "user_id" INTEGER,
    "rating" INTEGER,
    "comment" TEXT,
    "likes_count" INTEGER DEFAULT 0,
    "review_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "reviews_pkey" PRIMARY KEY ("review_id")
);

-- Replies
CREATE TABLE "replies" (
    "reply_id" SERIAL NOT NULL,
    "review_id" INTEGER,
    "user_id" INTEGER,
    "reply_text" TEXT NOT NULL,
    "reply_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "replies_pkey" PRIMARY KEY ("reply_id")
);

-- Watchlists
CREATE TABLE "watchlists" (
    "watchlist_id" SERIAL NOT NULL,
    "user_id" INTEGER,
    "list_name" VARCHAR(100) DEFAULT 'My Watchlist',
    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "watchlists_pkey" PRIMARY KEY ("watchlist_id")
);

-- Watchlist Items (join table)
CREATE TABLE "watchlist_items" (
    "watchlist_id" INTEGER NOT NULL,
    "movie_id" INTEGER NOT NULL,
    "added_date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "watchlist_items_pkey" PRIMARY KEY ("watchlist_id","movie_id")
);

-- Awards
CREATE TABLE "awards" (
    "award_id" SERIAL NOT NULL,
    "award_name" VARCHAR(255) NOT NULL,
    "year" INTEGER NOT NULL,
    CONSTRAINT "awards_pkey" PRIMARY KEY ("award_id")
);

-- Movie Awards (join table)
CREATE TABLE "movie_awards" (
    "award_id" INTEGER NOT NULL,
    "movie_id" INTEGER NOT NULL,
    "person_id" INTEGER,
    CONSTRAINT "movie_awards_pkey" PRIMARY KEY ("award_id","movie_id")
);

-- Unique Indexes
CREATE UNIQUE INDEX "users_username_key" ON "users"("username");
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");
CREATE UNIQUE INDEX "genres_genre_name_key" ON "genres"("genre_name");

-- Foreign Keys
ALTER TABLE "movie_crew" ADD CONSTRAINT "movie_crew_movie_id_fkey" FOREIGN KEY ("movie_id") REFERENCES "movies"("movie_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_crew" ADD CONSTRAINT "movie_crew_person_id_fkey" FOREIGN KEY ("person_id") REFERENCES "people"("person_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_genres" ADD CONSTRAINT "movie_genres_movie_id_fkey" FOREIGN KEY ("movie_id") REFERENCES "movies"("movie_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_genres" ADD CONSTRAINT "movie_genres_genre_id_fkey" FOREIGN KEY ("genre_id") REFERENCES "genres"("genre_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_companies" ADD CONSTRAINT "movie_companies_movie_id_fkey" FOREIGN KEY ("movie_id") REFERENCES "movies"("movie_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_companies" ADD CONSTRAINT "movie_companies_company_id_fkey" FOREIGN KEY ("company_id") REFERENCES "production_companies"("company_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "reviews" ADD CONSTRAINT "reviews_movie_id_fkey" FOREIGN KEY ("movie_id") REFERENCES "movies"("movie_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "reviews" ADD CONSTRAINT "reviews_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "replies" ADD CONSTRAINT "replies_review_id_fkey" FOREIGN KEY ("review_id") REFERENCES "reviews"("review_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "replies" ADD CONSTRAINT "replies_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "watchlists" ADD CONSTRAINT "watchlists_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("user_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "watchlist_items" ADD CONSTRAINT "watchlist_items_watchlist_id_fkey" FOREIGN KEY ("watchlist_id") REFERENCES "watchlists"("watchlist_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "watchlist_items" ADD CONSTRAINT "watchlist_items_movie_id_fkey" FOREIGN KEY ("movie_id") REFERENCES "movies"("movie_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_awards" ADD CONSTRAINT "movie_awards_award_id_fkey" FOREIGN KEY ("award_id") REFERENCES "awards"("award_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_awards" ADD CONSTRAINT "movie_awards_movie_id_fkey" FOREIGN KEY ("movie_id") REFERENCES "movies"("movie_id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "movie_awards" ADD CONSTRAINT "movie_awards_person_id_fkey" FOREIGN KEY ("person_id") REFERENCES "people"("person_id") ON DELETE SET NULL ON UPDATE CASCADE;
