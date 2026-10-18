import {
  ApiResponse,
  ScoreDistribution,
  StudentScores,
  Subject,
  TopStudent,
} from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  const json = await res.json().catch(() => null);
  if (!res.ok) {
    const errorMsg =
      json?.error?.message ||
      json?.detail ||
      `Yêu cầu thất bại với mã lỗi HTTP ${res.status}`;
    throw new Error(errorMsg);
  }
  return json as T;
}

export const apiService = {
  
  async getHealth(): Promise<{ status: string; service?: string }> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<{ status: string; service?: string }>(res);
  },

  async getTotalStudents(): Promise<number> {
    const res = await fetch(`${API_BASE}/students/total`)
    const result = await handleResponse<ApiResponse<{total: number}>>(res)
    return result.data.total
  },
  
  async getSubjects(): Promise<Subject[]> {
    const res = await fetch(`${API_BASE}/subjects`);
    const result = await handleResponse<ApiResponse<Subject[]>>(res);
    return result.data;
  },

  async getScoresBySbd(sbd: string): Promise<StudentScores> {
    const cleanSbd = sbd.trim();
    const res = await fetch(`${API_BASE}/scores/${encodeURIComponent(cleanSbd)}`);
    const result = await handleResponse<ApiResponse<StudentScores>>(res);
    return result.data;
  },

  async getScoreDistribution(subjectCode: string): Promise<ScoreDistribution> {
    const cleanCode = subjectCode.trim();
    const res = await fetch(
      `${API_BASE}/reports/score-distribution?subjectCode=${encodeURIComponent(cleanCode)}`
    );
    const result = await handleResponse<ApiResponse<ScoreDistribution>>(res);
    return result.data;
  },

  async getTopAStudents(): Promise<TopStudent[]> {
    const res = await fetch(`${API_BASE}/students/top-a`);
    const result = await handleResponse<ApiResponse<TopStudent[]>>(res);
    return result.data;
  },
};
