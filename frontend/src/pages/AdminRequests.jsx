import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertCircle, Eye, X
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  getAllRequests, getRequestById, updateRequestStatus,
  getCurrentUser
} from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export default function AdminRequests() {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [updating, setUpdating] = useState(false);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    checkAuth();
    loadRequests();
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

  const loadRequests = async () => {
    setLoading(true);
    try {
      const data = await getAllRequests();
      setRequests(data.requests || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const openDetail = async (reqId) => {
    setSelected(reqId);
    try {
      const data = await getRequestById(reqId);
      setDetail(data);
      setAdminNotes(data.admin_notes || '');
    } catch (err) {
      console.error(err);
    }
  };

  const handleStatusUpdate = async (status) => {
    setUpdating(true);
    try {
      await updateRequestStatus(selected, status, adminNotes || null);
      loadRequests();
      setSelected(null);
      setDetail(null);
    } catch (err) {
      alert('Failed: ' + err.message);
    } finally {
      setUpdating(false);
    }
  };

  const statusColors = {
    pending: 'bg-amber-100 text-amber-700',
    reviewed: 'bg-blue-100 text-blue-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  };

  const filteredRequests = filter === 'all'
    ? requests
    : requests.filter(r => r.status === filter);

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
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg gradient-bg">
                <AlertCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-800">Student Requests</h1>
                <p className="text-slate-500">Review and respond to student appeals</p>
              </div>
            </div>

            {/* Filter tabs */}
            <div className="flex gap-2">
              {['all', 'pending', 'reviewed', 'approved', 'rejected'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-all ${
                    filter === f
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-slate-500 hover:bg-slate-100'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Requests Table */}
          <Card className="overflow-hidden p-0 shadow-xl">
            <div className="px-6 py-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                {filteredRequests.length} Request{filteredRequests.length !== 1 ? 's' : ''}
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Student ID</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Message</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Status</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Date</th>
                    <th className="text-right px-6 py-4 text-sm font-semibold text-slate-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-slate-500">Loading...</td>
                    </tr>
                  ) : filteredRequests.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                        No {filter !== 'all' ? filter : ''} requests.
                      </td>
                    </tr>
                  ) : (
                    filteredRequests.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-mono font-semibold text-slate-800">{r.student_id}</div>
                          {r.student_name && (
                            <div className="text-xs text-slate-500">{r.student_name}</div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-slate-700 truncate max-w-[300px]">{r.message}</p>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColors[r.status] || statusColors.pending}`}>
                            {r.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          {new Date(r.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => openDetail(r.id)}
                            className="p-1.5 rounded-md text-blue-600 hover:bg-blue-50"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Detail Modal */}
          <AnimatePresence>
            {selected && detail && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
                onClick={() => { setSelected(null); setDetail(null); }}
              >
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.95, opacity: 0 }}
                  className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-slate-800">Request Details</h3>
                    <button
                      onClick={() => { setSelected(null); setDetail(null); }}
                      className="p-1.5 rounded-lg hover:bg-slate-100"
                    >
                      <X className="w-5 h-5 text-slate-500" />
                    </button>
                  </div>

                  <div className="p-6">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                          Student ID
                        </div>
                        <div className="font-mono font-semibold text-slate-800">{detail.student_id}</div>
                      </div>
                      <div>
                        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
                          Status
                        </div>
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColors[detail.status] || statusColors.pending}`}>
                          {detail.status}
                        </span>
                      </div>
                    </div>

                    <div className="mb-4">
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                        Student Message
                      </div>
                      <div className="bg-slate-50 rounded-xl p-4 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                        {detail.message}
                      </div>
                    </div>

                    <div className="mb-4">
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                        Admin Notes
                      </div>
                      <textarea
                        value={adminNotes}
                        onChange={(e) => setAdminNotes(e.target.value)}
                        placeholder="Add notes or response for the student..."
                        className="w-full min-h-[80px] px-3 py-2.5 rounded-xl border border-slate-200 text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>

                    <div className="text-xs text-slate-400 mb-4">
                      Submitted: {new Date(detail.created_at).toLocaleString()}
                    </div>

                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleStatusUpdate('reviewed')}
                        disabled={updating}
                        variant="secondary"
                        className="flex-1"
                      >
                        Reviewed
                      </Button>
                      <Button
                        onClick={() => handleStatusUpdate('approved')}
                        disabled={updating}
                        className="flex-1"
                        style={{ background: '#22c55e' }}
                      >
                        Approve
                      </Button>
                      <Button
                        onClick={() => handleStatusUpdate('rejected')}
                        disabled={updating}
                        variant="danger"
                        className="flex-1"
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
