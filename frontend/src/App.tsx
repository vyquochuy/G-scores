import { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { MetricsOverview } from './components/overview/MetricsOverview';
import { ScoreLookup } from './components/lookup/ScoreLookup';
import { ScoreDistribution } from './components/report/ScoreDistribution';
import { TopStudentsGroupA } from './components/ranking/TopStudentsGroupA';
import { TabType } from './types';

export function App() {
  const [currentTab, setCurrentTab] = useState<TabType>('overview');
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
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
            <MetricsOverview onNavigateTab={(tab) => setCurrentTab(tab)} />
          )}
          {currentTab === 'lookup' && <ScoreLookup />}
          {currentTab === 'distribution' && <ScoreDistribution />}
          {currentTab === 'ranking' && <TopStudentsGroupA />}
        </main>

        {/* Global Footer */}
        <footer className="py-6 px-4 sm:px-6 lg:px-8 border-t border-slate-200/80 text-center text-xs text-slate-500 bg-white">
          <p>
            Hệ thống G-Scores 2024 — Bản quyền phục vụ mục đích kiểm tra và đánh giá học thuật
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
