import React, { useEffect, useState } from 'react';
import {
  Users,
  BookOpen,
  Trophy,
  Search,
  BarChart3,
  ArrowRight,
  AlertCircle,
} from 'lucide-react';
import { apiService } from '../../services/api';
import { TabType, TopStudent } from '../../types';

interface MetricsOverviewProps {
  onNavigateTab: (tab: TabType) => void;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ onNavigateTab }) => {
  const [subjectCount, setSubjectCount] = useState<number | null>(null);
  const [top1Student, setTop1Student] = useState<TopStudent | null>(null);
  const [totalStudentCount, setTotalStudentCount] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadOverviewData = async () => {
      setIsLoading(true);
      setErrorMsg(null);
      try {
        const [subs, topStudents, totalStudents] = await Promise.all([
          apiService.getSubjects(),
          apiService.getTopAStudents(),
          apiService.getTotalStudents(),
        ]);
        if (isMounted) {
          setSubjectCount(subs.length);
          if (topStudents.length > 0) {
            setTop1Student(topStudents[0]);
          }
          setTotalStudentCount(totalStudents);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setErrorMsg(
            err instanceof Error
              ? err.message
              : 'Không thể tải đầy đủ số liệu tổng quan từ máy chủ.'
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadOverviewData();
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 sm:p-8 shadow-xs">
        <span className="inline-block px-3 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-semibold tracking-wide uppercase mb-3 border border-blue-200/60">
          Kỳ thi THPT Quốc gia 2024
        </span>
        <h2 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight mb-2">
          Hệ thống Tra cứu và Phân tích Điểm thi G-Scores
        </h2>
        <p className="text-slate-600 text-sm leading-relaxed max-w-3xl">
          Nền tảng hỗ trợ tra cứu kết quả thi tốt nghiệp THPT năm 2024, phân tích trực quan phổ điểm các môn học theo 4 khoảng chuẩn và vinh danh danh sách thí sinh có điểm cao nhất khối A trên toàn quốc.
        </p>
      </div>

      {/* Error notification if API fails */}
      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Lỗi tải dữ liệu tổng quan</h4>
            <p className="text-sm mt-0.5">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* 3 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {/* Card 1: Thí sinh dự thi môn Toán */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Tổng thí sinh dự thi
            </span>
            <div className="mt-1">
              {isLoading ? (
                <div className="h-8 w-28 bg-slate-200 animate-pulse rounded my-1" />
              ) : (
                <h3 className="text-2xl font-bold font-mono text-slate-900">
                  {totalStudentCount !== null ? totalStudentCount.toLocaleString() : '-'}
                </h3>
              )}
            </div>
            <span className="text-xs text-slate-500 block mt-1">
              Tổng số thí sinh dự thi THPT quốc gia năm 2024
            </span>
          </div>
          <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Users className="w-6 h-6" />
          </div>
        </div>

        {/* Card 2: Số lượng môn thi */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Môn thi được hỗ trợ
            </span>
            <div className="mt-1">
              {isLoading ? (
                <div className="h-8 w-20 bg-slate-200 animate-pulse rounded my-1" />
              ) : (
                <h3 className="text-2xl font-bold font-mono text-slate-900">
                  {subjectCount !== null ? `${subjectCount} môn` : '-'}
                </h3>
              )}
            </div>
            <span className="text-xs text-slate-500 block mt-1">
              Đầy đủ 9 môn thi tốt nghiệp THPT
            </span>
          </div>
          <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <BookOpen className="w-6 h-6" />
          </div>
        </div>

        {/* Card 3: Điểm cao nhất Khối A */}
        <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Thủ khoa Khối A
            </span>
            <div className="mt-1">
              {isLoading ? (
                <div className="h-8 w-28 bg-slate-200 animate-pulse rounded my-1" />
              ) : (
                <h3 className="text-2xl font-bold font-mono text-slate-900">
                  {top1Student ? `${top1Student.total.toFixed(2)} điểm` : '-'}
                </h3>
              )}
            </div>
            <span className="text-xs text-slate-500 font-mono block mt-1">
              {top1Student ? `SBD: ${top1Student.registrationNumber}` : 'Đang cập nhật'}
            </span>
          </div>
          <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Trophy className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Feature Quick Launch Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div
          onClick={() => onNavigateTab('lookup')}
          className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs hover:border-blue-500 hover:shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <Search className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-slate-800 text-base mb-1.5 group-hover:text-blue-600 transition-colors">
              Tra cứu điểm thi cá nhân
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Nhập số báo danh 8 chữ số để tra cứu kết quả thi và phân loại mức điểm từng môn dự thi.
            </p>
          </div>
          <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-xs font-semibold text-blue-600 group-hover:translate-x-1 transition-transform">
            <span>Truy cập tra cứu</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>

        <div
          onClick={() => onNavigateTab('distribution')}
          className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs hover:border-blue-500 hover:shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-slate-800 text-base mb-1.5 group-hover:text-blue-600 transition-colors">
              Thống kê phổ điểm 4 khoảng
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Trực quan hóa phân bố điểm số theo 4 mức chuẩn với biểu đồ tỷ lệ và bảng số liệu chi tiết.
            </p>
          </div>
          <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-xs font-semibold text-blue-600 group-hover:translate-x-1 transition-transform">
            <span>Xem biểu đồ phổ điểm</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>

        <div
          onClick={() => onNavigateTab('ranking')}
          className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs hover:border-blue-500 hover:shadow-sm transition-all cursor-pointer group flex flex-col justify-between"
        >
          <div>
            <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <Trophy className="w-5 h-5" />
            </div>
            <h4 className="font-bold text-slate-800 text-base mb-1.5 group-hover:text-blue-600 transition-colors">
              Top 10 Thí sinh Khối A
            </h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Bảng xếp hạng 10 thí sinh có tổng điểm 3 môn Toán, Vật lí, Hóa học cao nhất trên toàn quốc.
            </p>
          </div>
          <div className="mt-5 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-xs font-semibold text-blue-600 group-hover:translate-x-1 transition-transform">
            <span>Xem bảng xếp hạng</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </div>
      </div>
    </div>
  );
};
