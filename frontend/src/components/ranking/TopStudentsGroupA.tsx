import React, { useEffect, useState } from 'react';
import { Trophy, AlertCircle, Medal, Award, Star, RefreshCw } from 'lucide-react';
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
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-blue-950 rounded-xl p-6 text-white shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider mb-1">
            <Trophy className="w-4 h-4 text-amber-400" />
            Bảng vinh danh học thuật
          </div>
          <h3 className="text-xl font-bold tracking-tight text-white">
            Top 10 Thí Sinh Điểm Cao Nhất Khối A
          </h3>
          <p className="text-sm text-slate-300 mt-1">
            Tổ hợp xét tuyển Toán — Vật lí — Hóa học (chỉ xét thí sinh có đầy đủ điểm của cả 3 môn)
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={isLoading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600/80 hover:bg-blue-600 text-white text-xs font-semibold transition-all border border-blue-400/30 cursor-pointer self-start md:self-auto disabled:opacity-50"
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

      {/* Top 3 Podium Highlights */}
      {!isLoading && top3.length >= 3 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Top 1 - Thu khoa */}
          <div className="bg-white rounded-xl border-2 border-amber-300 p-5 shadow-xs relative overflow-hidden order-1 md:order-2 bg-gradient-to-b from-amber-50/50 to-white">
            <div className="absolute -top-3 -right-3 w-16 h-16 bg-amber-400/20 rounded-full flex items-center justify-center">
              <Medal className="w-8 h-8 text-amber-500" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500 text-white shadow-xs flex items-center gap-1">
                <Star className="w-3.5 h-3.5 fill-current" />
                Thủ khoa toàn quốc (Hạng 1)
              </span>
            </div>
            <h4 className="text-2xl font-bold font-mono text-slate-900 mt-2">
              SBD: {top3[0].registrationNumber}
            </h4>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold font-mono text-amber-600">
                {top3[0].total.toFixed(2)}
              </span>
              <span className="text-xs font-medium text-slate-500">tổng điểm</span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-amber-200/80 text-center text-xs">
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

          {/* Top 2 - A khoa 1 */}
          <div className="bg-white rounded-xl border border-slate-300 p-5 shadow-xs order-2 md:order-1 bg-gradient-to-b from-slate-50/60 to-white">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-slate-600 text-white shadow-xs flex items-center gap-1">
                <Award className="w-3.5 h-3.5" />
                Á khoa (Hạng 2)
              </span>
            </div>
            <h4 className="text-xl font-bold font-mono text-slate-900 mt-2">
              SBD: {top3[1].registrationNumber}
            </h4>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-extrabold font-mono text-slate-700">
                {top3[1].total.toFixed(2)}
              </span>
              <span className="text-xs font-medium text-slate-500">tổng điểm</span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-200 text-center text-xs">
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

          {/* Top 3 - Hang 3 */}
          <div className="bg-white rounded-xl border border-amber-700/30 p-5 shadow-xs order-3 bg-gradient-to-b from-amber-50/30 to-white">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-700 text-white shadow-xs flex items-center gap-1">
                <Award className="w-3.5 h-3.5" />
                Hạng 3 toàn quốc
              </span>
            </div>
            <h4 className="text-xl font-bold font-mono text-slate-900 mt-2">
              SBD: {top3[2].registrationNumber}
            </h4>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-extrabold font-mono text-amber-800">
                {top3[2].total.toFixed(2)}
              </span>
              <span className="text-xs font-medium text-slate-500">tổng điểm</span>
            </div>
            <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-amber-200 text-center text-xs">
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
          <div className="px-6 py-4 border-b border-slate-200/80 flex items-center justify-between">
            <h4 className="font-bold text-slate-800 text-sm">
              Danh sách chi tiết Top 10 thí sinh Khối A
            </h4>
            <span className="text-xs text-slate-500">
              Quy tắc phụ: Sắp xếp theo số báo danh tăng dần khi bằng điểm
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold border-b border-slate-200">
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
                  let rankBadge = 'bg-slate-100 text-slate-700 font-semibold';
                  if (student.rank === 1) rankBadge = 'bg-amber-100 text-amber-800 font-bold border border-amber-300';
                  else if (student.rank === 2) rankBadge = 'bg-slate-200 text-slate-800 font-bold border border-slate-400';
                  else if (student.rank === 3) rankBadge = 'bg-amber-50 text-amber-900 font-bold border border-amber-600/40';

                  return (
                    <tr
                      key={student.registrationNumber}
                      className={`hover:bg-slate-50/80 transition-colors ${
                        student.rank === 1 ? 'bg-amber-50/30' : ''
                      }`}
                    >
                      <td className="px-6 py-4 text-center">
                        <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs ${rankBadge}`}>
                          {student.rank}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono font-bold text-slate-800">
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
