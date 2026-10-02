export interface User {
  id: number;
  username: string;
  email: string;
  passwordHash: string;
  accountRole: string;
  profilePictureUrl: string | null;
  createdAt: Date | null;
}

export interface Movie {
  id: number;
  title: string;
  releaseDate: Date | null;
  durationMins: number | null;
  description: string | null;
  imdbRating: number | null;
  calculatedRating: number | null;
  posterUrl: string | null;
}

export interface Review {
  id: number;
  movieId: number | null;
  userId: number | null;
  rating: number | null;
  comment: string | null;
  likesCount: number | null;
  reviewDate: Date | null;
  updatedAt: Date | null;
  user?: User; // Optional populated property
  replies?: Reply[]; // Optional populated property
}

export interface Person {
  id: number;
  name: string;
  birthdate: Date | null;
  bio: string | null;
}

export interface Reply {
  id: number;
  reviewId: number | null;
  userId: number | null;
  replyText: string;
  replyDate: Date | null;
  updatedAt: Date | null;
  user?: User; // Optional populated property
}

export interface Genre {
  id: number;
  genreName: string;
}

export interface MovieCrew {
  movieId: number;
  personId: number;
  roleName: string;
  person?: Person; // Optional populated property
}

export interface MovieGenre {
  movieId: number;
  genreId: number;
  genre?: Genre; // Optional populated property
}
