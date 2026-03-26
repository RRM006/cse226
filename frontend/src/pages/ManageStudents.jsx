import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users, Plus, Trash2, Key, Edit2, X, Check
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  createStudent, getAllStudents, updateStudent,
  adminResetPassword, deleteStudent, getCurrentUser
} from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export default function ManageStudents() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editId, setEditId] = useState(null);
  const [resetId, setResetId] = useState(null);
  const [message, setMessage] = useState({ text: '', type: '' });

  const [createForm, setCreateForm] = useState({ student_id: '', name: '', email: '' });
  const [editForm, setEditForm] = useState({ name: '', email: '' });
  const [resetForm, setResetForm] = useState({ password: '' });

  useEffect(() => {
    checkAuth();
    loadStudents();
  }, []);

  const checkAuth = async () => {
    try {
      const me = await getCurrentUser();
      if (me.role !== 'admin') {
        navigate('/upload');
      }
    } catch {
      navigate('/login');
    }
  };

  const loadStudents = async () => {
    setLoading(true);
    try {
      const data = await getAllStudents();
      setStudents(data.students || []);
      setTotal(data.total || 0);
    } catch (err) {
      showMsg(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showMsg = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 4000);
  };

  const handleCreate = async () => {
    if (!/^\d{10}$/.test(createForm.student_id)) {
      showMsg('Student ID must be exactly 10 digits', 'error');
      return;
    }
    try {
      const result = await createStudent(createForm.student_id, createForm.name, createForm.email);
      showMsg(`Student created! Default password: ${result.default_password}`);
      setShowCreateForm(false);
      setCreateForm({ student_id: '', name: '', email: '' });
      loadStudents();
    } catch (err) {
      showMsg(err.message, 'error');
    }
  };

  const handleUpdate = async (studentId) => {
    try {
      await updateStudent(studentId, editForm);
      showMsg('Student updated');
      setEditId(null);
      loadStudents();
    } catch (err) {
      showMsg(err.message, 'error');
    }
  };

  const handleResetPassword = async (studentId) => {
    if (resetForm.password.length < 6) {
      showMsg('Password must be at least 6 characters', 'error');
      return;
    }
    try {
      await adminResetPassword(studentId, resetForm.password);
      showMsg('Password reset. Student must change it on next login.');
      setResetId(null);
      setResetForm({ password: '' });
    } catch (err) {
      showMsg(err.message, 'error');
    }
  };

  const handleDelete = async (studentId) => {
    if (!window.confirm(`Delete student ${studentId}? This cannot be undone.`)) return;
    try {
      await deleteStudent(studentId);
      showMsg('Student deleted');
      loadStudents();
    } catch (err) {
      showMsg(err.message, 'error');
    }
  };

  return (
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg gradient-bg">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-800">Manage Students</h1>
                <p className="text-slate-500">{total} student{total !== 1 ? 's' : ''} registered</p>
              </div>
            </div>
            <Button
              onClick={() => setShowCreateForm(!showCreateForm)}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Add Student
            </Button>
          </div>

          {/* Message */}
          {message.text && (
            <div className={`mb-4 px-4 py-3 rounded-xl text-sm font-medium ${
              message.type === 'error'
                ? 'bg-red-50 text-red-700 border border-red-200'
                : 'bg-green-50 text-green-700 border border-green-200'
            }`}>
              {message.text}
            </div>
          )}

          {/* Create Form */}
          {showCreateForm && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
              <Card className="mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Create Student Account</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Student ID (10 digits) *
                    </label>
                    <input
                      value={createForm.student_id}
                      onChange={(e) => setCreateForm({ ...createForm, student_id: e.target.value.replace(/\D/g, '').slice(0, 10) })}
                      placeholder="2221971042"
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Name
                    </label>
                    <input
                      value={createForm.name}
                      onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                      placeholder="Student name"
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Email
                    </label>
                    <input
                      value={createForm.email}
                      onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                      placeholder="email@example.com"
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div className="flex gap-3">
                  <Button onClick={handleCreate}>Create Account</Button>
                  <Button variant="secondary" onClick={() => setShowCreateForm(false)}>Cancel</Button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Students Table */}
          <Card className="overflow-hidden p-0 shadow-xl">
            <div className="px-6 py-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Users className="w-5 h-5" />
                All Students ({total})
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Student ID</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Name</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Email</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Status</th>
                    <th className="text-right px-6 py-4 text-sm font-semibold text-slate-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-slate-500">Loading...</td>
                    </tr>
                  ) : students.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                        No students yet. Click "Add Student" to create one.
                      </td>
                    </tr>
                  ) : (
                    students.map((s) => (
                      <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <span className="font-mono font-semibold text-slate-800">{s.student_id}</span>
                        </td>
                        <td className="px-6 py-4">
                          {editId === s.id ? (
                            <input
                              value={editForm.name}
                              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                              className="w-36 px-2 py-1 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                            />
                          ) : (
                            <span className="text-sm text-slate-700">{s.name || '—'}</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {editId === s.id ? (
                            <input
                              value={editForm.email}
                              onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                              className="w-48 px-2 py-1 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                            />
                          ) : (
                            <span className="text-sm text-slate-600">{s.email || '—'}</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {s.is_first_login ? (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                              First Login
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                              Active
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-1">
                            {editId === s.id ? (
                              <>
                                <button
                                  onClick={() => handleUpdate(s.student_id)}
                                  className="p-1.5 rounded-md bg-green-50 text-green-600 hover:bg-green-100"
                                  title="Save"
                                >
                                  <Check className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => setEditId(null)}
                                  className="p-1.5 rounded-md bg-slate-100 text-slate-500 hover:bg-slate-200"
                                  title="Cancel"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  onClick={() => { setEditId(s.id); setEditForm({ name: s.name || '', email: s.email || '' }); }}
                                  className="p-1.5 rounded-md text-blue-600 hover:bg-blue-50"
                                  title="Edit"
                                >
                                  <Edit2 className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => setResetId(s.student_id)}
                                  className="p-1.5 rounded-md text-amber-600 hover:bg-amber-50"
                                  title="Reset Password"
                                >
                                  <Key className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDelete(s.student_id)}
                                  className="p-1.5 rounded-md text-red-600 hover:bg-red-50"
                                  title="Delete"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Reset Password Modal */}
          {resetId && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm"
              >
                <h3 className="text-lg font-semibold text-slate-800 mb-1">Reset Password</h3>
                <p className="text-sm text-slate-500 mb-4">Student ID: {resetId}</p>
                <input
                  type="password"
                  value={resetForm.password}
                  onChange={(e) => setResetForm({ password: e.target.value })}
                  placeholder="New password (min 6 chars)"
                  className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
                <div className="flex gap-3">
                  <Button
                    onClick={() => handleResetPassword(resetId)}
                    className="flex-1"
                    style={{ background: '#f59e0b' }}
                  >
                    Reset
                  </Button>
                  <Button
                    variant="secondary"
                    className="flex-1"
                    onClick={() => { setResetId(null); setResetForm({ password: '' }); }}
                  >
                    Cancel
                  </Button>
                </div>
              </motion.div>
            </div>
          )}
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
