import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-reddit-light">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 max-w-4xl mx-auto px-4 py-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
