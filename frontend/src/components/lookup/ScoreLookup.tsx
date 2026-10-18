import React, { useEffect, useState } from 'react';
import { Search, AlertCircle, CheckCircle2, User, BookOpen, Calculator } from 'lucide-react';
import { apiService } from '../../services/api';
import { StudentScores, Subject } from '../../types';

export const ScoreLookup: React.FC = () => {
  const [sbd, setSbd] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [studentData, setStudentData] = useState<StudentScores | null>(null);
  const [allSubjects, setAllSubjects] = useState<Subject[]>([]);

  useEffect(() => {
    let isMounted = true;
    apiService
      .getSubjects()
      .then((subs) => {
        if (isMounted) setAllSubjects(subs);
      })
      .catch(() => []);
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSearch = async (targetSbd?: string) => {
    const querySbd = (targetSbd !== undefined ? targetSbd : sbd).trim();
    setErrorMsg(null);
    setStudentData(null);

    // Client-side validation: phai gom dung 8 chu so
    if (!/^\d{8}$/.test(querySbd)) {
      setErrorMsg('Số báo danh không hợp lệ. Vui lòng nhập đúng 8 chữ số (ví dụ: 01000001).');
      return;
    }

    setIsLoading(true);
    try {
      const data = await apiService.getScoresBySbd(querySbd);
      setStudentData(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg('Đã xảy ra lỗi không xác định trong quá trình tra cứu.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const setExampleSbd = (val: string) => {
    setSbd(val);
    handleSearch(val);
  };

  // Tinh tong diem Khoi A neu co du ca 3 mon Toan, Vat li, Hoa hoc
  const getGroupATotal = (data: StudentScores): number | null => {
    const math = data.scores.find((s) => s.subjectCode === 'toan')?.score;
    const phys = data.scores.find((s) => s.subjectCode === 'vat_li')?.score;
    const chem = data.scores.find((s) => s.subjectCode === 'hoa_hoc')?.score;
    if (math !== undefined && phys !== undefined && chem !== undefined) {
      return Number((math + phys + chem).toFixed(2));
    }
    return null;
  };

  const notTakenSubjects = allSubjects.filter(
    (sub) => !studentData?.scores.some((s) => s.subjectCode === sub.code)
  );

  return (
    <div className="space-y-6">
      {/* Search Header Card */}
      <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs p-6">
        <h3 className="text-lg font-bold text-slate-800 mb-1 flex items-center gap-2">
          <Search className="w-5 h-5 text-blue-600" />
          Tra cứu kết quả thi tốt nghiệp THPT 2024
        </h3>
        <p className="text-sm text-slate-500 mb-6">
          Nhập số báo danh 8 chữ số của thí sinh để tra cứu chi tiết điểm thi các môn dự thi.
        </p>

        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <input
              type="text"
              value={sbd}
              onChange={(e) => {
                setSbd(e.target.value);
                if (errorMsg) setErrorMsg(null);
              }}
              onKeyDown={handleKeyDown}
              placeholder="Nhập số báo danh (ví dụ: 01000001)"
              maxLength={8}
              className="w-full px-4 py-3 rounded-lg border border-slate-300 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-base transition-all"
            />
          </div>
          <button
            onClick={() => handleSearch()}
            disabled={isLoading}
            className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Đang tra cứu...</span>
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                <span>Tra cứu điểm</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Click Example - only 01000001 explicitly marked as example */}
        <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
          <span className="font-medium">Số báo danh ví dụ:</span>
          <button
            type="button"
            onClick={() => setExampleSbd('01000001')}
            className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono transition-colors cursor-pointer border border-slate-200"
          >
            01000001 (Thao tác thử)
          </button>
        </div>
      </div>

      {/* Error Notice */}
      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 text-rose-800 flex items-start gap-3 shadow-xs">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-sm">Không tìm thấy hoặc dữ liệu chưa đúng</h4>
            <p className="text-sm mt-0.5">{errorMsg}</p>
          </div>
        </div>
      )}

      {/* Result Display */}
      {studentData && (
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          {/* Result Card Header */}
          <div className="p-6 bg-white border-b border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                <User className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs uppercase tracking-wider text-slate-500 font-semibold">
                  Kết quả tra cứu
                </span>
                <h4 className="text-xl font-bold font-mono tracking-tight text-slate-900">
                  Số báo danh: {studentData.registrationNumber}
                </h4>
              </div>
            </div>

            {/* Group A Total badge if applicable */}
            {getGroupATotal(studentData) !== null && (
              <div className="flex items-center gap-2.5 bg-blue-50 border border-blue-200 px-4 py-2.5 rounded-lg">
                <Calculator className="w-5 h-5 text-blue-600" />
                <div>
                  <span className="text-xs text-blue-700 block font-medium">Tổng điểm Khối A (Toán + Lý + Hóa)</span>
                  <span className="text-lg font-bold text-blue-900 font-mono">
                    {getGroupATotal(studentData)?.toFixed(2)} điểm
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Scores Content */}
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h5 className="font-bold text-slate-800 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-blue-600" />
                Chi tiết điểm thi các môn ({studentData.scores.length} môn có điểm)
              </h5>
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                Dữ liệu chính thức từ CSDL
              </span>
            </div>

            {/* Taken subjects grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {studentData.scores.map((item) => {
                let badgeColor = 'bg-slate-100 text-slate-700 border-slate-200';
                let bandText = 'Dưới 4.0';

                if (item.score >= 8.0) {
                  badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                  bandText = 'Từ 8.0 trở lên';
                } else if (item.score >= 6.0) {
                  badgeColor = 'bg-blue-50 text-blue-700 border-blue-200';
                  bandText = 'Từ 6.0 đến dưới 8.0';
                } else if (item.score >= 4.0) {
                  badgeColor = 'bg-amber-50 text-amber-700 border-amber-200';
                  bandText = 'Từ 4.0 đến dưới 6.0';
                } else {
                  badgeColor = 'bg-rose-50 text-rose-700 border-rose-200';
                  bandText = 'Dưới 4.0';
                }

                return (
                  <div
                    key={item.subjectCode}
                    className="p-4 rounded-xl border border-slate-200/90 hover:border-blue-300 transition-all bg-slate-50/50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-slate-700 text-sm">
                        {item.subjectName}
                      </span>
                      <span className="text-2xl font-bold font-mono text-slate-900">
                        {item.score.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between pt-2 border-t border-slate-200/60 text-xs">
                      <span className="text-slate-500">Phân loại:</span>
                      <span className={`px-2 py-0.5 rounded-full font-medium border ${badgeColor}`}>
                        {bandText}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Subjects not taken / No data */}
            {notTakenSubjects.length > 0 && (
              <div className="mt-6 pt-5 border-t border-slate-200/80">
                <h6 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                  Môn không dự thi / Không có dữ liệu ({notTakenSubjects.length} môn)
                </h6>
                <div className="flex flex-wrap gap-2">
                  {notTakenSubjects.map((sub) => (
                    <span
                      key={sub.code}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 text-slate-600 border border-slate-200 text-xs font-medium"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                      {sub.name}: <span className="text-slate-400">Không có điểm</span>
                    </span>
                  ))}
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  * Thí sinh không đăng ký dự thi các môn này trong kỳ thi (trạng thái khác biệt so với điểm 0.00).
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
