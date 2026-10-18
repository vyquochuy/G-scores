import { useEffect, useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { MetricsOverview } from './components/overview/MetricsOverview';
import { ScoreLookup } from './components/lookup/ScoreLookup';
import { ScoreDistribution } from './components/report/ScoreDistribution';
import { TopStudentsGroupA } from './components/ranking/TopStudentsGroupA';
import { TabType } from './types';

const tabToPath: Record<TabType, string> = {
  overview: '/Tong-quan',
  lookup: '/tra-cuu',
  distribution: '/Thong-ke',
  ranking: '/top-10',
};

function getTabFromPath(pathname: string): TabType {
  const normalized = pathname.toLowerCase().replace(/\/+$/, '') || '/';
  if (normalized === '/tong-quan') return 'overview';
  if (normalized === '/tra-cuu') return 'lookup';
  if (normalized === '/thong-ke') return 'distribution';
  if (normalized === '/top-10') return 'ranking';
  return 'overview';
}

export function App() {
  const [currentTab, setCurrentTab] = useState<TabType>(() =>
    getTabFromPath(window.location.pathname)
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  useEffect(() => {
    const handlePopState = () => {
      setCurrentTab(getTabFromPath(window.location.pathname));
    };

    const normalized = window.location.pathname.toLowerCase().replace(/\/+$/, '') || '/';
    if (normalized === '/' || normalized === '') {
      window.history.replaceState(null, '', '/Tong-quan');
    }

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleSelectTab = (tab: TabType) => {
    setCurrentTab(tab);
    const targetPath = tabToPath[tab];
    if (window.location.pathname.toLowerCase() !== targetPath.toLowerCase()) {
      window.history.pushState(null, '', targetPath);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={handleSelectTab}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-72 transition-all">
        {/* Top Header */}
        <Header onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)} />

        {/* Dynamic View Body */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {currentTab === 'overview' && (
            <MetricsOverview onNavigateTab={handleSelectTab} />
          )}
          {currentTab === 'lookup' && <ScoreLookup />}
          {currentTab === 'distribution' && <ScoreDistribution />}
          {currentTab === 'ranking' && <TopStudentsGroupA />}
        </main>

        {/* Global Footer */}
        <footer className="py-6 px-4 sm:px-6 lg:px-8 border-t border-slate-200/80 text-center text-xs text-slate-500 bg-white">
          <p>
            Hệ thống G-Scores 2024 — Cổng tra cứu và thống kê dữ liệu điểm thi tốt nghiệp THPT Quốc gia
          </p>
          <p className="mt-1 text-slate-400">
            Dữ liệu nguồn chính thức từ Bộ Giáo dục và Đào tạo Việt Nam
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
