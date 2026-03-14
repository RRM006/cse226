import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, Trash2, AlertCircle, ClipboardList } from 'lucide-react';
import { getHistory, deleteScan } from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatDate, getProgramLabel, getAuditLevelLabel } from '../lib/utils';

export default function History() {
  const navigate = useNavigate();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteId, setDeleteId] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    try {
      const data = await getHistory(50, 0);
      setScans(data.scans || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(scanId) {
    if (!window.confirm('Are you sure you want to delete this scan?')) {
      return;
    }

    setDeleteId(scanId);
    try {
      await deleteScan(scanId);
      setScans(scans.filter(s => s.scan_id !== scanId));
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    } finally {
      setDeleteId(null);
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-500">Loading history...</p>
          </div>
        </div>
      </DashboardLayout>
    );
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
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-slate-800">Scan History</h1>
              <p className="text-slate-500 mt-1">View your previous audit results</p>
            </div>
          </div>

          {error && (
            <Card className="mb-6 bg-red-50 border-red-200">
              <div className="flex items-center gap-3 text-red-700">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            </Card>
          )}

          {scans.length === 0 ? (
            <Card className="text-center py-12">
              <div className="flex justify-center mb-4">
                <div className="p-4 rounded-full bg-slate-100">
                  <ClipboardList className="w-8 h-8 text-slate-400" />
                </div>
              </div>
              <h3 className="text-lg font-medium text-slate-700 mb-2">No audit history yet</h3>
              <p className="text-slate-500 mb-6">Run your first audit to see results here</p>
              <Button onClick={() => navigate('/upload')}>
                Run Your First Audit
              </Button>
            </Card>
          ) : (
            <Card className="overflow-hidden p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200">
                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Date</th>
                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Type</th>
                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Program</th>
                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Level</th>
                      <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Status</th>
                      <th className="text-right px-6 py-4 text-sm font-semibold text-slate-600">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {scans.map((scan) => (
                      <tr 
                        key={scan.scan_id} 
                        className="hover:bg-slate-50 cursor-pointer transition-colors"
                        onClick={() => navigate(`/result/${scan.scan_id}`)}
                      >
                        <td className="px-6 py-4 text-sm text-slate-600">
                          {formatDate(scan.created_at)}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
                            {scan.input_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-700">
                          {getProgramLabel(scan.program)}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">
                          Level {scan.audit_level}
                        </td>
                        <td className="px-6 py-4">
                          {scan.summary?.eligible === true && (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                              Eligible
                            </span>
                          )}
                          {scan.summary?.eligible === false && (
                            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                              Not Eligible
                            </span>
                          )}
                          {scan.summary?.eligible === undefined && (
                            <span className="text-slate-400 text-sm">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/result/${scan.scan_id}`)}
                            >
                              View
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(scan.scan_id)}
                              disabled={deleteId === scan.scan_id}
                              className="text-red-600 hover:bg-red-50"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
