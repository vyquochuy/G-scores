import React, { useEffect, useState } from 'react';
import { Trophy, AlertCircle, RefreshCw } from 'lucide-react';
import { apiService } from '../../services/api';
import { TopStudent } from '../../types';

export const TopStudentsGroupA: React.FC = () => {
  const [students, setStudents] = useState<TopStudent[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadData = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await apiService.getTopAStudents();
      setStudents(data);
    } catch (err: unknown) {
      setErrorMsg(
        err instanceof Error ? err.message : 'Không thể tải danh sách bảng xếp hạng Top 10 Khối A.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const top3 = students.slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="bg-white rounded-xl border border-slate-200/80 p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-blue-600 text-xs font-semibold uppercase tracking-wider mb-1">
            <Trophy className="w-4 h-4 text-blue-600" />
            Bảng xếp hạng khối A
          </div>
          <h3 className="text-lg font-bold tracking-tight text-slate-800">
            Top 10 Thí Sinh Có Điểm Cao Nhất Khối A
          </h3>
          <p className="text-sm text-slate-500 mt-1">
            Tổ hợp xét tuyển Toán — Vật lí — Hóa học (chỉ xét thí sinh có đầy đủ điểm của cả 3 môn)
          </p>
        </div>

        <button
          type="button"
          onClick={loadData}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition-all shadow-sm cursor-pointer self-start md:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Cập nhật bảng xếp hạng</span>
        </button>
      </div>

      {/* Error Notice */}
      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Không thể tải dữ liệu</h4>
            <p className="text-sm mt-0.5">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-8 text-center">
          <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-500 font-medium">Đang truy vấn bảng xếp hạng từ CSDL...</p>
        </div>
      )}

      {/* Top 3 Highlights - Standard TailAdmin Cards with subtle accent for Rank 1 */}
      {!isLoading && top3.length >= 3 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Top 1 */}
          <div className="bg-white rounded-xl border border-blue-200 p-5 shadow-xs bg-blue-50/10">
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                Hạng 1 (Thủ khoa)
              </span>
              <span className="text-xs text-blue-600 font-medium">Điểm cao nhất</span>
            </div>
            <h4 className="text-lg font-bold font-mono text-slate-900 mt-2">
              SBD: {top3[0].registrationNumber}
            </h4>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold font-mono text-blue-600">
                {top3[0].total.toFixed(2)}
              </span>
              <span className="text-xs text-slate-500">tổng điểm</span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100 text-center text-xs">
              <div>
                <span className="text-slate-500 block">Toán</span>
                <span className="font-bold font-mono text-slate-800">{top3[0].math.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Vật lí</span>
                <span className="font-bold font-mono text-slate-800">{top3[0].physics.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Hóa học</span>
                <span className="font-bold font-mono text-slate-800">{top3[0].chemistry.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Top 2 */}
          <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                Hạng 2 (Á khoa)
              </span>
            </div>
            <h4 className="text-lg font-bold font-mono text-slate-900 mt-2">
              SBD: {top3[1].registrationNumber}
            </h4>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold font-mono text-slate-800">
                {top3[1].total.toFixed(2)}
              </span>
              <span className="text-xs text-slate-500">tổng điểm</span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100 text-center text-xs">
              <div>
                <span className="text-slate-500 block">Toán</span>
                <span className="font-bold font-mono text-slate-800">{top3[1].math.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Vật lí</span>
                <span className="font-bold font-mono text-slate-800">{top3[1].physics.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Hóa học</span>
                <span className="font-bold font-mono text-slate-800">{top3[1].chemistry.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Top 3 */}
          <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                Hạng 3
              </span>
            </div>
            <h4 className="text-lg font-bold font-mono text-slate-900 mt-2">
              SBD: {top3[2].registrationNumber}
            </h4>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className="text-3xl font-extrabold font-mono text-slate-800">
                {top3[2].total.toFixed(2)}
              </span>
              <span className="text-xs text-slate-500">tổng điểm</span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100 text-center text-xs">
              <div>
                <span className="text-slate-500 block">Toán</span>
                <span className="font-bold font-mono text-slate-800">{top3[2].math.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Vật lí</span>
                <span className="font-bold font-mono text-slate-800">{top3[2].physics.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Hóa học</span>
                <span className="font-bold font-mono text-slate-800">{top3[2].chemistry.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full 10 Students Table */}
      {!isLoading && students.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <h4 className="font-bold text-slate-800 text-sm">
              Danh sách chi tiết Top 10 thí sinh Khối A
            </h4>
            <span className="text-xs text-slate-500">
              Quy tắc phụ: Sắp xếp theo số báo danh tăng dần khi bằng điểm
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 uppercase text-xs font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3.5 text-center w-20">Thứ hạng</th>
                  <th className="px-6 py-3.5">Số báo danh</th>
                  <th className="px-6 py-3.5 text-right">Điểm Toán</th>
                  <th className="px-6 py-3.5 text-right">Điểm Vật lí</th>
                  <th className="px-6 py-3.5 text-right">Điểm Hóa học</th>
                  <th className="px-6 py-3.5 text-right">Tổng điểm Khối A</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/70">
                {students.map((student) => {
                  const isTop1 = student.rank === 1;

                  return (
                    <tr
                      key={student.registrationNumber}
                      className={`hover:bg-slate-50/80 transition-colors ${
                        isTop1 ? 'bg-blue-50/20' : ''
                      }`}
                    >
                      <td className="px-6 py-4 text-center">
                        <span
                          className={`inline-flex items-center justify-center w-6 h-6 rounded-md text-xs ${
                            isTop1
                              ? 'bg-blue-600 text-white font-bold'
                              : 'bg-slate-100 text-slate-700 font-semibold'
                          }`}
                        >
                          {student.rank}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono font-semibold text-slate-900">
                        {student.registrationNumber}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-slate-700">
                        {student.math.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-slate-700">
                        {student.physics.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right font-mono text-slate-700">
                        {student.chemistry.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 text-right font-mono font-bold text-blue-600 text-base">
                        {student.total.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
