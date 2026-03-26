import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FileText, Send, CheckCircle, XCircle, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getStudentProfile, getStudentAuditResults, getStudentRequests, submitStudentRequest } from '../lib/api';
import { getStudentToken } from '../lib/supabase';
import StudentLayout from '../components/StudentLayout';

export default function StudentDashboard() {
  const navigate = useNavigate();
  const [results, setResults] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [requestMessage, setRequestMessage] = useState('');
  const [requestAuditId, setRequestAuditId] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!getStudentToken()) {
      navigate('/student/login');
      return;
    }
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [resultsRes, requestsRes] = await Promise.all([
        getStudentAuditResults(),
        getStudentRequests(),
      ]);
      setResults(resultsRes.results || []);
      setRequests(requestsRes.requests || []);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitRequest = async () => {
    if (!requestMessage.trim()) return;
    setSubmitting(true);
    try {
      await submitStudentRequest(requestMessage, requestAuditId);
      setShowRequestForm(false);
      setRequestMessage('');
      setRequestAuditId(null);
      loadData();
    } catch (err) {
      alert('Failed to submit request: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const eligibleCount = results.filter(r => r.eligible).length;
  const failedCount = results.filter(r => !r.eligible).length;
  const pendingCount = requests.filter(r => r.status === 'pending').length;

  return (
    <StudentLayout>
      <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '24px' }}>
        Dashboard
      </h2>

      {/* Stats */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px', marginBottom: '28px',
      }}>
        {[
          { label: 'Total Audits', value: results.length, icon: <FileText size={20} />, color: '#3b82f6' },
          { label: 'Eligible', value: eligibleCount, icon: <CheckCircle size={20} />, color: '#22c55e' },
          { label: 'Not Eligible', value: failedCount, icon: <XCircle size={20} />, color: '#ef4444' },
          { label: 'Pending Requests', value: pendingCount, icon: <Clock size={20} />, color: '#f59e0b' },
        ].map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '14px',
              padding: '20px',
              display: 'flex', alignItems: 'center', gap: '14px',
            }}
          >
            <div style={{
              width: '44px', height: '44px', borderRadius: '10px',
              background: `${stat.color}20`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: stat.color,
            }}>
              {stat.icon}
            </div>
            <div>
              <div style={{ fontSize: '22px', fontWeight: '700' }}>{stat.value}</div>
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>{stat.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Latest Results */}
      <div style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
          Latest Audit Results
        </h3>
        {loading ? (
          <div style={{ color: 'rgba(255,255,255,0.5)' }}>Loading...</div>
        ) : results.length === 0 ? (
          <div style={{
            background: 'rgba(255,255,255,0.05)', borderRadius: '12px',
            padding: '32px', textAlign: 'center', color: 'rgba(255,255,255,0.5)',
          }}>
            No audit results yet. Your admin will upload them.
          </div>
        ) : (
          <div style={{
            display: 'grid', gap: '10px',
          }}>
            {results.slice(0, 3).map((result) => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  padding: '16px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  cursor: 'pointer',
                }}
                onClick={() => navigate(`/student/audit-results`)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '36px', height: '36px', borderRadius: '8px',
                    background: result.eligible ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    {result.eligible
                      ? <CheckCircle size={18} color="#22c55e" />
                      : <XCircle size={18} color="#ef4444" />
                    }
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '600' }}>
                      {result.program} - Level {result.audit_level}
                    </div>
                    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
                      {new Date(result.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: '600',
                  background: result.eligible ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                  color: result.eligible ? '#86efac' : '#fca5a5',
                }}>
                  {result.eligible ? 'Eligible' : 'Not Eligible'}
                </span>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Request Button - Only show if there are failed results */}
      {failedCount > 0 && (
        <div style={{ marginBottom: '24px' }}>
          {!showRequestForm ? (
            <button
              onClick={() => setShowRequestForm(true)}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '12px 20px', borderRadius: '10px',
                background: 'rgba(245, 158, 11, 0.15)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                color: '#fcd34d', cursor: 'pointer',
                fontSize: '14px', fontWeight: '600',
              }}
            >
              <Send size={16} />
              Submit Review Request
            </button>
          ) : (
            <div style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '14px',
              padding: '20px',
            }}>
              <h4 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px' }}>
                Submit Review Request
              </h4>
              <textarea
                value={requestMessage}
                onChange={(e) => setRequestMessage(e.target.value)}
                placeholder="Describe why you need a review of your audit result..."
                style={{
                  width: '100%', minHeight: '100px', padding: '12px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '10px',
                  color: 'white', fontSize: '14px',
                  resize: 'vertical', outline: 'none',
                }}
              />
              <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
                <button
                  onClick={handleSubmitRequest}
                  disabled={submitting || !requestMessage.trim()}
                  style={{
                    padding: '10px 20px', borderRadius: '8px',
                    background: submitting ? 'rgba(59, 130, 246, 0.5)' : '#3b82f6',
                    color: 'white', border: 'none',
                    fontSize: '14px', fontWeight: '600',
                    cursor: submitting ? 'not-allowed' : 'pointer',
                  }}
                >
                  {submitting ? 'Submitting...' : 'Submit'}
                </button>
                <button
                  onClick={() => { setShowRequestForm(false); setRequestMessage(''); }}
                  style={{
                    padding: '10px 20px', borderRadius: '8px',
                    background: 'rgba(255,255,255,0.1)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    color: 'white', fontSize: '14px',
                    cursor: 'pointer',
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Requests */}
      <div>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
          Recent Requests
        </h3>
        {requests.length === 0 ? (
          <div style={{
            background: 'rgba(255,255,255,0.05)', borderRadius: '12px',
            padding: '24px', textAlign: 'center', color: 'rgba(255,255,255,0.5)',
            fontSize: '13px',
          }}>
            No requests submitted yet.
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '8px' }}>
            {requests.slice(0, 5).map((req) => (
              <div
                key={req.id}
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '10px',
                  padding: '14px',
                }}
              >
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'center', marginBottom: '6px',
                }}>
                  <span style={{
                    fontSize: '12px', color: 'rgba(255,255,255,0.5)',
                  }}>
                    {new Date(req.created_at).toLocaleString()}
                  </span>
                  <span style={{
                    padding: '3px 10px',
                    borderRadius: '12px',
                    fontSize: '11px',
                    fontWeight: '600',
                    background:
                      req.status === 'pending' ? 'rgba(245, 158, 11, 0.2)' :
                      req.status === 'approved' ? 'rgba(34, 197, 94, 0.2)' :
                      req.status === 'rejected' ? 'rgba(239, 68, 68, 0.2)' :
                      'rgba(59, 130, 246, 0.2)',
                    color:
                      req.status === 'pending' ? '#fcd34d' :
                      req.status === 'approved' ? '#86efac' :
                      req.status === 'rejected' ? '#fca5a5' :
                      '#93c5fd',
                  }}>
                    {req.status}
                  </span>
                </div>
                <p style={{ fontSize: '13px', margin: 0, color: 'rgba(255,255,255,0.8)' }}>
                  {req.message}
                </p>
                {req.admin_notes && (
                  <div style={{
                    marginTop: '8px', padding: '8px 12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '8px', fontSize: '12px',
                    color: '#93c5fd',
                  }}>
                    <strong>Admin Response:</strong> {req.admin_notes}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </StudentLayout>
  );
}
