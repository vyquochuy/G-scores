export interface Subject {
  code: string;
  name: string;
}

export interface SubjectScore {
  subjectCode: string;
  subjectName: string;
  score: number;
}

export interface StudentScores {
  registrationNumber: string;
  scores: SubjectScore[];
}

export interface ScoreBand {
  key: string;
  label: string;
  count: number;
}

export interface ScoreDistribution {
  subjectCode: string;
  subjectName: string;
  validScoreCount: number;
  bands: ScoreBand[];
}

export interface TopStudent {
  rank: number;
  registrationNumber: string;
  math: number;
  physics: number;
  chemistry: number;
  total: number;
}

export interface ApiResponse<T> {
  data: T;
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export type TabType = 'overview' | 'lookup' | 'distribution' | 'ranking';
