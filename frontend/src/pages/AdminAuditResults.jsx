import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Plus
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  getAllAuditResults, createAuditResult, getAllStudents,
  getCurrentUser
} from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export default function AdminAuditResults() {
  const navigate = useNavigate();
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [students, setStudents] = useState([]);
  const [form, setForm] = useState({
    student_id: '', program: 'BSCSE', audit_level: 1,
    result_json: '{}', result_text: '', eligible: true,
  });
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    checkAuth();
    loadResults();
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

  const loadResults = async () => {
    setLoading(true);
    try {
      const data = await getAllAuditResults();
      setResults(data.results || []);
      setTotal(data.total || 0);
    } catch (err) {
      showMsg(err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const loadStudents = async () => {
    try {
      const data = await getAllStudents();
      setStudents(data.students || []);
    } catch {}
  };

  const showMsg = (text, type = 'success') => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 4000);
  };

  const handleCreate = async () => {
    if (!form.student_id) {
      showMsg('Please select a student', 'error');
      return;
    }
    if (!form.result_text.trim()) {
      showMsg('Result text is required', 'error');
      return;
    }

    let parsedJson;
    try {
      parsedJson = JSON.parse(form.result_json);
    } catch {
      showMsg('Invalid JSON in result_json', 'error');
      return;
    }

    try {
      await createAuditResult({
        student_id: form.student_id,
        program: form.program,
        audit_level: form.audit_level,
        result_json: parsedJson,
        result_text: form.result_text,
        eligible: form.eligible,
      });
      showMsg('Audit result created successfully');
      setShowForm(false);
      setForm({
        student_id: '', program: 'BSCSE', audit_level: 1,
        result_json: '{}', result_text: '', eligible: true,
      });
      loadResults();
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
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-800">Audit Results</h1>
                <p className="text-slate-500">{total} result{total !== 1 ? 's' : ''} recorded</p>
              </div>
            </div>
            <Button
              onClick={() => setShowForm(!showForm)}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Add Result
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
          {showForm && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
              <Card className="mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Create Audit Result</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Student *
                    </label>
                    <select
                      value={form.student_id}
                      onChange={(e) => setForm({ ...form, student_id: e.target.value })}
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="">Select student...</option>
                      {students.map(s => (
                        <option key={s.student_id} value={s.student_id}>
                          {s.student_id} {s.name ? `- ${s.name}` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Program
                    </label>
                    <select
                      value={form.program}
                      onChange={(e) => setForm({ ...form, program: e.target.value })}
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="BSCSE">BSCSE</option>
                      <option value="BSEEE">BSEEE</option>
                      <option value="LLB">LLB</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Audit Level
                    </label>
                    <select
                      value={form.audit_level}
                      onChange={(e) => setForm({ ...form, audit_level: parseInt(e.target.value) })}
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value={1}>Level 1</option>
                      <option value={2}>Level 2</option>
                      <option value={3}>Level 3</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                      Eligible
                    </label>
                    <select
                      value={form.eligible}
                      onChange={(e) => setForm({ ...form, eligible: e.target.value === 'true' })}
                      className="w-full px-3 py-2.5 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="true">Yes - Eligible</option>
                      <option value="false">No - Not Eligible</option>
                    </select>
                  </div>
                </div>
                <div className="mb-4">
                  <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                    Result Text *
                  </label>
                  <textarea
                    value={form.result_text}
                    onChange={(e) => setForm({ ...form, result_text: e.target.value })}
                    placeholder="Detailed audit result text..."
                    className="w-full min-h-[80px] px-3 py-2.5 rounded-lg border border-slate-200 text-sm resize-y focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                    Result JSON
                  </label>
                  <textarea
                    value={form.result_json}
                    onChange={(e) => setForm({ ...form, result_json: e.target.value })}
                    placeholder='{"total_credits": 130, "cgpa": 3.5}'
                    className="w-full min-h-[60px] px-3 py-2.5 rounded-lg border border-slate-200 text-xs font-mono resize-y focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div className="flex gap-3">
                  <Button onClick={handleCreate}>Create Result</Button>
                  <Button variant="secondary" onClick={() => setShowForm(false)}>Cancel</Button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Results Table */}
          <Card className="overflow-hidden p-0 shadow-xl">
            <div className="px-6 py-4 border-b border-slate-200">
              <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <FileText className="w-5 h-5" />
                All Results ({total})
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Student ID</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Program</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Level</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Eligible</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Student Name</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-slate-600">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loading ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-slate-500">Loading...</td>
                    </tr>
                  ) : results.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                        No audit results. Click "Add Result" to create one.
                      </td>
                    </tr>
                  ) : (
                    results.map((r) => (
                      <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4">
                          <span className="font-mono font-semibold text-slate-800">{r.student_id}</span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-700">{r.program}</td>
                        <td className="px-6 py-4 text-sm text-slate-600">Level {r.audit_level}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                            r.eligible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                          }`}>
                            {r.eligible ? 'Yes' : 'No'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          {r.student_name || '—'}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">
                          {new Date(r.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
