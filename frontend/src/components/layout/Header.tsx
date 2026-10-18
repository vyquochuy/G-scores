import React, { useEffect, useState } from 'react';
import { Menu, Activity, CheckCircle2, AlertCircle } from 'lucide-react';
import { apiService } from '../../services/api';

interface HeaderProps {
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    const checkBackend = async () => {
      try {
        const res = await apiService.getHealth();
        if (isMounted) {
          setIsHealthy(res.status === 'ok');
        }
      } catch {
        if (isMounted) {
          setIsHealthy(false);
        }
      }
    };
    checkBackend();
    const interval = setInterval(checkBackend, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8 bg-white border-b border-slate-200/80 shadow-xs">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 lg:hidden"
          aria-label="Mở thanh điều hướng"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-800 tracking-tight">
            Cổng Thông Tin Điểm Thi THPT Quốc Gia 2024
          </h2>
          <p className="text-xs text-slate-500 hidden sm:block">
            Hệ thống phân tích số liệu học thuật chuẩn hóa
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        {/* Backend status indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-xs font-medium">
          {isHealthy === null ? (
            <>
              <Activity className="w-3.5 h-3.5 text-slate-400 animate-spin" />
              <span className="text-slate-500">Đang kiểm tra CSDL...</span>
            </>
          ) : isHealthy ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span className="text-emerald-700 font-semibold">Kết nối CSDL ổn định</span>
            </>
          ) : (
            <>
              <AlertCircle className="w-3.5 h-3.5 text-rose-500" />
              <span className="text-rose-600 font-semibold">Mất kết nối API</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
