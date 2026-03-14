import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Users, Eye, Shield, X, ClipboardList } from 'lucide-react';
import { getAllUsers, updateUserRole, getCurrentUser, getUserHistory } from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatDate, getProgramLabel } from '../lib/utils';

export default function AdminPanel() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userHistory, setUserHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    checkAdminAndLoad();
  }, []);

  async function checkAdminAndLoad() {
    try {
      const user = await getCurrentUser();
      if (user.role !== 'admin') {
        navigate('/upload');
        return;
      }
      setIsAdmin(true);
      loadUsers();
    } catch (err) {
      navigate('/login');
    } finally {
      setLoading(false);
    }
  }

  async function loadUsers() {
    try {
      const data = await getAllUsers();
      setUsers(data.users || []);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleRoleChange(userId, newRole) {
    try {
      await updateUserRole(userId, newRole);
      setUsers(users.map(u => 
        u.id === userId ? { ...u, role: newRole } : u
      ));
    } catch (err) {
      alert('Failed to update role: ' + err.message);
    }
  }

  async function handleViewHistory(userId) {
    setSelectedUser(userId);
    setLoadingHistory(true);
    try {
      const data = await getUserHistory(userId, 20, 0);
      setUserHistory(data.scans || []);
    } catch (err) {
      alert('Failed to load history: ' + err.message);
    } finally {
      setLoadingHistory(false);
    }
  }

  function closeHistoryModal() {
    setSelectedUser(null);
    setUserHistory([]);
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-500">Loading...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg gradient-bg">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-800">Admin Panel</h1>
                <p className="text-slate-500">Manage users and view system statistics</p>
              </div>
            </div>
          </div>

          {error && (
            <Card className="mb-6 bg-red-50 border-red-200">
              <p className="text-red-600">{error}</p>
            </Card>
          )}

          {/* Users Table */}
          <Card className="overflow-hidden p-0 shadow-xl">
            <div className="px-6 py-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Users className="w-5 h-5" />
                All Users ({users.length})
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">User</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Role</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Scans</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Joined</th>
                    <th className="text-right px-6 py-4 text-sm font-semibold text-slate-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                            <span className="text-sm font-medium text-primary-700">
                              {user.email?.charAt(0).toUpperCase()}
                            </span>
                          </div>
                          <span className="text-sm text-slate-700 truncate max-w-[200px]">
                            {user.email}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {user.role === 'admin' ? (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                            <Shield className="w-3 h-3 mr-1" />
                            Admin
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                            Student
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {user.scan_count || 0}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewHistory(user.id)}
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            View
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRoleChange(user.id, user.role === 'admin' ? 'student' : 'admin')}
                            className={user.role === 'admin' ? 'text-amber-600 hover:bg-amber-50' : 'text-blue-600 hover:bg-blue-50'}
                          >
                            {user.role === 'admin' ? 'Remove Admin' : 'Make Admin'}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>

        {/* User History Modal */}
        <AnimatePresence>
          {selectedUser && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
              onClick={closeHistoryModal}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                    <ClipboardList className="w-5 h-5" />
                    User Scan History
                  </h3>
                  <button
                    onClick={closeHistoryModal}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-slate-500" />
                  </button>
                </div>
                
                <div className="p-6 overflow-y-auto max-h-[60vh]">
                  {loadingHistory ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                  ) : userHistory.length === 0 ? (
                    <p className="text-center text-slate-500 py-8">No scans found</p>
                  ) : (
                    <table className="w-full">
                      <thead>
                        <tr className="text-left text-sm font-semibold text-slate-600 border-b border-slate-200">
                          <th className="pb-3">Date</th>
                          <th className="pb-3">Program</th>
                          <th className="pb-3">Level</th>
                          <th className="pb-3">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {userHistory.map((scan) => (
                          <tr key={scan.scan_id}>
                            <td className="py-3 text-sm text-slate-600">
                              {formatDate(scan.created_at)}
                            </td>
                            <td className="py-3 text-sm text-slate-700">
                              {getProgramLabel(scan.program)}
                            </td>
                            <td className="py-3 text-sm text-slate-600">
                              Level {scan.audit_level}
                            </td>
                            <td className="py-3">
                              {scan.summary?.eligible === true && (
                                <span className="text-green-600 text-sm font-medium">Eligible</span>
                              )}
                              {scan.summary?.eligible === false && (
                                <span className="text-red-600 text-sm font-medium">Not Eligible</span>
                              )}
                              {scan.summary?.eligible === undefined && (
                                <span className="text-slate-400 text-sm">-</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </DashboardLayout>
  );
}
