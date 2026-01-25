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
  course: number;
  student: User;
  created_at: string;
  task_type: 'random_question';
  is_active: boolean; // Add this to match the Task interface
  status: 'pending' | 'ongoing' | 'finished';
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

export interface Questionnaire {
  id: number;
  title: string;
  description: string;
  course: number;
  created_at: string;
  is_active: boolean;
  task_type: 'feedback';
}

export type Task = Checkin | RandomQuestion | Vote | Questionnaire;

export interface DirectPasswordResetPayload {
  username: string;
  new_password1: string;
  new_password2: string;
}

export interface ChatSession {
  id: number;
  topic: string | null;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  content: string;
  is_from_user: boolean;
  created_at: string;
  model?: string;
}

// Types for Assignment
export type QuestionType = 'single_choice' | 'multiple_choice' | 'true_false' | 'fill_in_the_blank' | 'short_answer';

export interface QuestionChoice {
  id: number;
  text: string;
  is_correct: boolean;
}

export interface Question {
  id: number;
  text: string;
  question_type: QuestionType;
  points: number;
  choices: QuestionChoice[];
  correct_answer: string | null;
}

export interface Answer {
  id: number;
  question: number;
  text: string;
  score: number | null;
}

export interface Submission {
  id: number;
  student: string; // student's name
  student_id: number;
  assignment: number;
  answers: Answer[];
  grade: number | null;
  status: 'submitted' | 'graded';
  submitted_at: string;
  feedback: string | null;
}

export interface StudentSubmissionStatus {
  student_id: number;
  student_name: string;
  submission_id: number | null;
  status: 'submitted' | 'graded' | 'not_submitted';
  grade: number | null;
}

export interface Assignment {
  id: number;
  title: string;
  due_date: string;
  questions: Question[];
  student_submissions: StudentSubmissionStatus[];
}

// Types for Exam
export interface Exam {
  id: number;
  title: string;
  course: number;
  end_time: string;
  time_limit: number;
  questions: Question[];
  student_submissions: StudentSubmissionStatus[];
}

export interface ExamSubmission {
  id: number;
  student: string; // student's name
  student_id: number;
  exam: number;
  answers: Answer[];
  grade: number | null;
  status: 'taking' | 'submitted' | 'graded';
  submitted_at: string;
  start_time: string;
  feedback: string | null;
}

// Types for Feedback
export interface FeedbackQuestion {
  id: number;
  text: string;
  question_type: 'text' | 'rating';
}

export interface FeedbackAnswer {
  id: number;
  question: number;
  answer_text: string | null;
  answer_rating: number | null;
}

export interface FeedbackResponse {
  id: number;
  student: User;
  submitted_at: string;
  answers: FeedbackAnswer[];
}

export interface FeedbackStudentStatus {
  student: User;
  status: 'submitted' | 'pending';
  response: FeedbackResponse | null;
}

export interface QuestionnaireDetail {
  id: number;
  title: string;
  questions: FeedbackQuestion[];
  student_statuses: FeedbackStudentStatus[];
}
