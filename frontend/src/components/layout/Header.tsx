import React from 'react';
import { Menu } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8 bg-white border-b border-slate-200/80 shadow-xs">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 lg:hidden transition-colors"
          aria-label="Mở thanh điều hướng"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-base sm:text-lg font-bold text-slate-800 tracking-tight leading-tight">
            Cổng Thông Tin Điểm Thi THPT Quốc Gia 2024
          </h2>
          <p className="text-xs text-slate-500 hidden sm:block">
            Tra cứu kết quả thi và phân tích phổ điểm các môn
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
          Kỳ thi năm 2024
        </span>
      </div>
    </header>
  );
};
