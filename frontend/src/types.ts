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

export interface CheckinRecord {
  id: number;
  student: User;
  checkin_time: string;
  is_manual: boolean;
}

export interface Checkin {
  id: number;
  title: string;
  start_time: string;
  end_time: string | null;
  is_active: boolean;
  is_checked_in: boolean;
  records?: CheckinRecord[];
}
