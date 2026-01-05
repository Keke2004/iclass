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
  task_type: 'checkin';
}

export interface RandomQuestion {
  id: number;
  student: User;
  created_at: string;
  task_type: 'random_question';
  is_active: boolean; // Add this to match the Task interface
}

export interface VoteChoice {
  id: number;
  text: string;
  response_count: number;
  voters?: User[];
}

export interface Vote {
  id: number;
  title: string;
  course: number;
  creator: number;
  created_at: string;
  is_active: boolean;
  choices: VoteChoice[];
  user_has_voted: boolean;
  total_votes: number;
  task_type: 'vote';
}

export type Task = Checkin | RandomQuestion | Vote;

export interface DirectPasswordResetPayload {
  username: string;
  new_password1: string;
  new_password2: string;
}
