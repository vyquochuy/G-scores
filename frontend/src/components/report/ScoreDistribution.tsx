import React, { useEffect, useState } from 'react';
import { BarChart3, BookOpen, AlertCircle, Users, CheckCircle, PieChart } from 'lucide-react';
import { apiService } from '../../services/api';
import { ScoreDistribution as ScoreDistributionType, Subject } from '../../types';

export const ScoreDistribution: React.FC = () => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubject, setSelectedSubject] = useState<string>('toan');
  const [distribution, setDistribution] = useState<ScoreDistributionType | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load subject list on mount
  useEffect(() => {
    let isMounted = true;
    const loadSubjects = async () => {
      try {
        const subs = await apiService.getSubjects();
        if (isMounted) {
          setSubjects(subs);
          if (subs.length > 0 && !subs.some((s) => s.code === selectedSubject)) {
            setSelectedSubject(subs[0].code);
          }
        }
      } catch (err: unknown) {
        if (isMounted) {
          setErrorMsg(err instanceof Error ? err.message : 'Không thể tải danh mục môn học.');
        }
      }
    };
    loadSubjects();
    return () => {
      isMounted = false;
    };
  }, []);

  // Load distribution when subject changes
  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      if (!selectedSubject) return;
      setIsLoading(true);
      setErrorMsg(null);
      try {
        const dist = await apiService.getScoreDistribution(selectedSubject);
        if (isMounted) {
          setDistribution(dist);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setErrorMsg(
            err instanceof Error ? err.message : 'Không thể tải dữ liệu thống kê phổ điểm.'
          );
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };
    loadData();
    return () => {
      isMounted = false;
    };
  }, [selectedSubject]);

  // Color mapping for the 4 bands
  const bandColors: Record<string, { bar: string; badge: string; text: string }> = {
    GE_8: { bar: 'bg-emerald-500', badge: 'bg-emerald-50 text-emerald-700 border-emerald-200', text: 'text-emerald-600' },
    GE_6_LT_8: { bar: 'bg-blue-500', badge: 'bg-blue-50 text-blue-700 border-blue-200', text: 'text-blue-600' },
    GE_4_LT_6: { bar: 'bg-amber-500', badge: 'bg-amber-50 text-amber-700 border-amber-200', text: 'text-amber-600' },
    LT_4: { bar: 'bg-rose-500', badge: 'bg-rose-50 text-rose-700 border-rose-200', text: 'text-rose-600' },
  };

  const maxBandCount = distribution
    ? Math.max(...distribution.bands.map((b) => b.count), 1)
    : 1;

  return (
    <div className="space-y-6">
      {/* Subject Filter Bar */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              Thống kê phân bố phổ điểm môn học
            </h3>
            <p className="text-sm text-slate-500">
              Biểu đồ trực quan hóa số lượng thí sinh theo 4 khoảng điểm chuẩn quy định
            </p>
          </div>

          <div className="flex items-center gap-3">
            <label htmlFor="subject-select" className="text-sm font-semibold text-slate-700 whitespace-nowrap">
              Chọn môn thi:
            </label>
            <div className="relative">
              <select
                id="subject-select"
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="px-4 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-800 font-medium text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all pr-10 cursor-pointer shadow-xs"
              >
                {subjects.map((sub) => (
                  <option key={sub.code} value={sub.code}>
                    {sub.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Lỗi tải dữ liệu</h4>
            <p className="text-sm mt-0.5">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-8 text-center">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500 font-medium">Đang truy vấn phổ điểm từ cơ sở dữ liệu...</p>
        </div>
      )}

      {/* Distribution Content */}
      {!isLoading && distribution && (
        <div className="space-y-6">
          {/* Key Metric Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Tổng thí sinh có điểm
                </span>
                <Users className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-2xl font-bold font-mono text-slate-900 mt-2">
                {distribution.validScoreCount.toLocaleString()}
              </p>
              <span className="text-xs text-slate-500 mt-1 block">
                Môn: {distribution.subjectName}
              </span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Đạt điểm giỏi {'(>= 8.0)'}
                </span>

                <CheckCircle className="w-5 h-5 text-emerald-600" />
              </div>
              <p className="text-2xl font-bold font-mono text-emerald-600 mt-2">
                {(
                  (distribution.bands.find((b) => b.key === 'GE_8')?.count || 0)
                ).toLocaleString()}
              </p>
              <span className="text-xs text-slate-500 mt-1 block">
                Chiếm{' '}
                {(
                  ((distribution.bands.find((b) => b.key === 'GE_8')?.count || 0) /
                    distribution.validScoreCount) *
                  100
                ).toFixed(1)}
                % tổng thí sinh
              </span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Khoảng điểm phổ biến nhất
                </span>
                <PieChart className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-lg font-bold text-slate-900 mt-2">
                {[...distribution.bands].sort((a, b) => b.count - a.count)[0]?.label}
              </p>
              <span className="text-xs text-slate-500 mt-1 block">
                Có{' '}
                {[...distribution.bands]
                  .sort((a, b) => b.count - a.count)[0]
                  ?.count.toLocaleString()}{' '}
                thí sinh
              </span>
            </div>
          </div>

          {/* Bar Chart Visualization Card */}
          <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs">
            <h4 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              Biểu đồ trực quan hóa 4 khoảng phổ điểm môn {distribution.subjectName}
            </h4>

            {/* Custom SVG / HTML Bar Chart */}
            <div className="space-y-5">
              {distribution.bands.map((band) => {
                const percentage =
                  distribution.validScoreCount > 0
                    ? (band.count / distribution.validScoreCount) * 100
                    : 0;
                const barWidth = Math.max(
                  (band.count / maxBandCount) * 100,
                  2
                );
                const colors = bandColors[band.key] || bandColors.GE_8;

                return (
                  <div key={band.key} className="space-y-1.5">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-semibold text-slate-800 flex items-center gap-2">
                        <span className={`w-3 h-3 rounded-sm ${colors.bar}`} />
                        {band.label}
                      </span>
                      <div className="text-right">
                        <span className="font-bold font-mono text-slate-900">
                          {band.count.toLocaleString()}
                        </span>{' '}
                        <span className="text-xs text-slate-500 font-mono">
                          ({percentage.toFixed(2)}%)
                        </span>
                      </div>
                    </div>

                    <div className="w-full bg-slate-100 rounded-lg h-8 p-1 overflow-hidden">
                      <div
                        className={`h-full rounded-md ${colors.bar} transition-all duration-700 ease-out flex items-center justify-end px-3 text-xs font-bold text-white shadow-xs`}
                        style={{ width: `${barWidth}%` }}
                      >
                        {percentage >= 7 && `${percentage.toFixed(1)}%`}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Detailed Statistics Table */}
          <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200/80">
              <h4 className="font-bold text-slate-800 text-sm">
                Bảng số liệu chi tiết các mức điểm
              </h4>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3.5">Mức điểm (Khoảng)</th>
                    <th className="px-6 py-3.5">Mã khoảng</th>
                    <th className="px-6 py-3.5 text-right">Số lượng thí sinh</th>
                    <th className="px-6 py-3.5 text-right">Tỷ lệ phần trăm</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/70">
                  {distribution.bands.map((band) => {
                    const percentage =
                      distribution.validScoreCount > 0
                        ? (band.count / distribution.validScoreCount) * 100
                        : 0;
                    const colors = bandColors[band.key] || bandColors.GE_8;

                    return (
                      <tr key={band.key} className="hover:bg-slate-50/70 transition-colors">
                        <td className="px-6 py-4 font-semibold text-slate-800">
                          <span className={`inline-block px-2.5 py-1 rounded-md text-xs font-medium border ${colors.badge}`}>
                            {band.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-mono text-xs text-slate-500">
                          {band.key}
                        </td>
                        <td className="px-6 py-4 text-right font-mono font-bold text-slate-900">
                          {band.count.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-right font-mono text-slate-600">
                          {percentage.toFixed(2)}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
                <tfoot className="bg-slate-50/80 font-bold border-t border-slate-200 text-slate-900">
                  <tr>
                    <td colSpan={2} className="px-6 py-3.5">
                      Tổng số thí sinh có điểm môn {distribution.subjectName}
                    </td>
                    <td className="px-6 py-3.5 text-right font-mono">
                      {distribution.validScoreCount.toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-right font-mono">100.00%</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
