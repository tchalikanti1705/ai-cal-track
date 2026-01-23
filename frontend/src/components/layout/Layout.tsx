import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import { useAuthStore } from '@/stores';
import {
  HomeIcon,
  FireIcon,
  BeakerIcon,
  HeartIcon,
  ChartBarIcon,
  CameraIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Nutrition', href: '/nutrition', icon: FireIcon },
  { name: 'Water', href: '/water', icon: BeakerIcon },
  { name: 'Exercise', href: '/exercise', icon: HeartIcon },
  { name: 'Walking', href: '/walking', icon: ChartBarIcon },
  { name: 'Scan Food', href: '/scan', icon: CameraIcon },
  { name: 'Insights', href: '/insights', icon: ChartBarIcon },
];

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, profile, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-secondary-200 transform transition-transform duration-200 lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-secondary-200">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">🥗</span>
            </div>
            <span className="font-bold text-lg text-secondary-900">FoodTracker</span>
          </Link>
          <button
            className="lg:hidden p-2 rounded-lg hover:bg-secondary-100"
            onClick={() => setSidebarOpen(false)}
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-secondary-600 hover:bg-secondary-100'
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* User section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-secondary-200">
          <Link
            to="/profile"
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-secondary-100 transition-colors"
          >
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <UserCircleIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-secondary-900 truncate">
                {profile?.first_name || user?.email}
              </p>
              <p className="text-xs text-secondary-500 truncate">{user?.email}</p>
            </div>
          </Link>
          <button
            onClick={handleLogout}
            className="mt-2 w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-secondary-600 hover:bg-secondary-100 transition-colors"
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <header className="sticky top-0 z-30 h-16 bg-white border-b border-secondary-200 lg:hidden">
          <div className="flex items-center justify-between h-full px-4">
            <button
              className="p-2 rounded-lg hover:bg-secondary-100"
              onClick={() => setSidebarOpen(true)}
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🥗</span>
              </div>
            </Link>
            <Link to="/profile" className="p-2 rounded-lg hover:bg-secondary-100">
              <UserCircleIcon className="w-6 h-6 text-secondary-600" />
            </Link>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
