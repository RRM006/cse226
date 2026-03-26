import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  GraduationCap,
  History,
  Settings,
  LogOut,
  ChevronDown,
  User,
  LayoutDashboard,
  Users,
  FileText,
  AlertCircle,
} from 'lucide-react';
import { signOut } from '../../lib/supabase';
import { getInitials } from '../../lib/utils';

export function Navbar({ user }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleLogout = async () => {
    await signOut();
    navigate('/login');
  };

  const navItems = [
    { label: 'Run Audit', path: '/upload', icon: LayoutDashboard },
    { label: 'History', path: '/history', icon: History },
  ];

  const adminNavItems = [
    { label: 'Admin Panel', path: '/admin', icon: Settings },
    { label: 'Manage Students', path: '/admin/manage-students', icon: Users },
    { label: 'Audit Results', path: '/admin/audit-results', icon: FileText },
    { label: 'Requests', path: '/admin/requests', icon: AlertCircle },
  ];

  const isAdmin = user?.role === 'admin';

  return (
    <nav className="sticky top-0 z-50 glass border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => navigate('/upload')}
          >
            <div className="p-2 rounded-lg gradient-bg">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-slate-800">NSU Audit Core</span>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150
                    ${isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
            {isAdmin && adminNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150
                    ${isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </button>
              );
            })}
          </div>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-sm font-medium text-primary-700">
                  {getInitials(user?.email)}
                </span>
              </div>
              <span className="hidden sm:block text-sm text-slate-600 max-w-[150px] truncate">
                {user?.email}
              </span>
              <ChevronDown className="w-4 h-4 text-slate-400" />
            </button>

            {isDropdownOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setIsDropdownOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 rounded-xl bg-white shadow-lg border border-slate-200 py-1 z-20">
                  <div className="px-4 py-3 border-b border-slate-100">
                    <p className="text-sm font-medium text-slate-800 truncate">{user?.email}</p>
                    <p className="text-xs text-slate-500 capitalize">{user?.role || 'Student'}</p>
                  </div>
                  <button
                    onClick={() => {
                      setIsDropdownOpen(false);
                      navigate('/history');
                    }}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50"
                  >
                    <History className="w-4 h-4" />
                    History
                  </button>
                  {isAdmin && (
                    <button
                      onClick={() => {
                        setIsDropdownOpen(false);
                        navigate('/admin/manage-students');
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50"
                    >
                      <Users className="w-4 h-4" />
                      Manage Students
                    </button>
                  )}
                  {isAdmin && (
                    <button
                      onClick={() => {
                        setIsDropdownOpen(false);
                        navigate('/admin');
                      }}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-slate-600 hover:bg-slate-50"
                    >
                      <Settings className="w-4 h-4" />
                      Admin Panel
                    </button>
                  )}
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
