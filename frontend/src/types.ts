export interface LoginCredentials {
  username?: string;
  password?: string;
}

export interface User {
  id?: number;
  username?: string;
  email?: string;
  password?: string;
  role?: 'student' | 'teacher' | 'admin';
}
