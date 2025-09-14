import React, { useState } from 'react';
import Header from './Header';
import Sidebar from './Sidebar';
import AICompanion from '../ai/AICompanion';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isAICompanionOpen, setIsAICompanionOpen] = useState(false);

  const handleToggleAICompanion = () => {
    setIsAICompanionOpen(!isAICompanionOpen);
  };

  const handleCloseAICompanion = () => {
    setIsAICompanionOpen(false);
  };

  return (
    <div className="min-h-screen bg-reddit-light">
      <Header
        onToggleAICompanion={handleToggleAICompanion}
        isAICompanionOpen={isAICompanionOpen}
      />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-6">
          {children}
        </main>
      </div>

      {/* AI Companion Side Window */}
      <AICompanion
        isOpen={isAICompanionOpen}
        onClose={handleCloseAICompanion}
      />
    </div>
  );
};

export default Layout;
