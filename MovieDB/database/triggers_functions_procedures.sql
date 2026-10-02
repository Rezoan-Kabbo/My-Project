-- ============================================================
-- MovieDB: Triggers, Functions, and Procedures
-- Run this file against your PostgreSQL database to install
-- all database-level features required by the project checklist.
-- ============================================================

-- ============================================================
-- 1. TRIGGER: Auto-update movies.calculated_rating
--    When a review is inserted, updated, or deleted, the
--    movie's calculated_rating is automatically recalculated
--    as the average of all its review ratings.
-- ============================================================

CREATE OR REPLACE FUNCTION update_movie_rating()
RETURNS TRIGGER AS $$
DECLARE
  target_movie_id INTEGER;
BEGIN
  -- Determine the affected movie_id (NEW is NULL on DELETE)
  IF TG_OP = 'DELETE' THEN
    target_movie_id := OLD.movie_id;
  ELSE
    target_movie_id := NEW.movie_id;
  END IF;

  UPDATE movies
  SET calculated_rating = (
    SELECT COALESCE(ROUND(AVG(rating::DECIMAL), 1), 0)
    FROM reviews
    WHERE movie_id = target_movie_id
  )
  WHERE movie_id = target_movie_id;

  IF TG_OP = 'DELETE' THEN
    RETURN OLD;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if it already exists, then create
DROP TRIGGER IF EXISTS trg_update_movie_rating ON reviews;

CREATE TRIGGER trg_update_movie_rating
AFTER INSERT OR UPDATE OR DELETE ON reviews
FOR EACH ROW EXECUTE FUNCTION update_movie_rating();


-- ============================================================
-- 2. FUNCTION: get_movie_review_count(movie_id)
--    Returns the total number of reviews for a given movie.
--    This is a computed/statistical value returned from the DB.
-- ============================================================

CREATE OR REPLACE FUNCTION get_movie_review_count(p_movie_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
  review_count INTEGER;
BEGIN
  SELECT COUNT(*)::INTEGER
  INTO review_count
  FROM reviews
  WHERE movie_id = p_movie_id;

  RETURN review_count;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 3. PROCEDURE: add_review(movie_id, user_id, rating, comment)
--    A multi-step workflow that:
--      Step 1: Inserts the review record
--      Step 2: Updates the movie's calculated_rating
--    If any step fails, the entire operation is rolled back.
-- ============================================================

CREATE OR REPLACE PROCEDURE add_review(
  p_movie_id INTEGER,
  p_user_id INTEGER,
  p_rating INTEGER,
  p_comment TEXT
)
LANGUAGE plpgsql AS $$
BEGIN
  -- Step 1: Insert the review
  INSERT INTO reviews (movie_id, user_id, rating, comment)
  VALUES (p_movie_id, p_user_id, p_rating, p_comment);

  -- Step 2: Update the movie's calculated_rating
  -- (This is also done by the trigger, but the procedure
  --  demonstrates explicit multi-step logic in one call)
  UPDATE movies
  SET calculated_rating = (
    SELECT COALESCE(ROUND(AVG(rating::DECIMAL), 1), 0)
    FROM reviews
    WHERE movie_id = p_movie_id
  )
  WHERE movie_id = p_movie_id;

  -- If we reach here, both steps succeeded.
  -- COMMIT is handled by the caller or implicitly by CALL.
EXCEPTION WHEN OTHERS THEN
  -- Roll back the entire transaction on any error
  RAISE;
END;
$$;
