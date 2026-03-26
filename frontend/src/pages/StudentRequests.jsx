import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Clock, CheckCircle, XCircle, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getStudentRequests, submitStudentRequest } from '../lib/api';
import { getStudentToken } from '../lib/supabase';
import StudentLayout from '../components/StudentLayout';

export default function StudentRequests() {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!getStudentToken()) {
      navigate('/student/login');
      return;
    }
    loadRequests();
  }, []);

  const loadRequests = async () => {
    setLoading(true);
    try {
      const data = await getStudentRequests();
      setRequests(data.requests || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!message.trim()) return;
    setSubmitting(true);
    try {
      await submitStudentRequest(message);
      setShowForm(false);
      setMessage('');
      loadRequests();
    } catch (err) {
      alert('Failed: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const statusConfig = {
    pending: { icon: <Clock size={14} />, color: '#fcd34d', bg: 'rgba(245, 158, 11, 0.2)', label: 'Pending' },
    reviewed: { icon: <Eye size={14} />, color: '#93c5fd', bg: 'rgba(59, 130, 246, 0.2)', label: 'Reviewed' },
    approved: { icon: <CheckCircle size={14} />, color: '#86efac', bg: 'rgba(34, 197, 94, 0.2)', label: 'Approved' },
    rejected: { icon: <XCircle size={14} />, color: '#fca5a5', bg: 'rgba(239, 68, 68, 0.2)', label: 'Rejected' },
  };

  return (
    <StudentLayout>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: '24px',
      }}>
        <h2 style={{ fontSize: '22px', fontWeight: '700', margin: 0 }}>
          My Requests
        </h2>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            display: 'flex', alignItems: 'center', gap: '6px',
            padding: '10px 16px', borderRadius: '8px',
            background: '#3b82f6', border: 'none',
            color: 'white', cursor: 'pointer',
            fontSize: '13px', fontWeight: '600',
          }}
        >
          <Send size={14} />
          New Request
        </button>
      </div>

      {/* New Request Form */}
      {showForm && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '14px',
            padding: '20px',
            marginBottom: '20px',
          }}
        >
          <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px' }}>
            Submit a Review Request
          </h3>
          <p style={{
            fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '12px',
          }}>
            If your audit result shows not eligible, you can submit a request for review.
          </p>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe your concern or reason for review..."
            style={{
              width: '100%', minHeight: '100px', padding: '12px',
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.15)',
              borderRadius: '10px', color: 'white',
              fontSize: '14px', resize: 'vertical', outline: 'none',
            }}
          />
          <div style={{ display: 'flex', gap: '10px', marginTop: '12px' }}>
            <button
              onClick={handleSubmit}
              disabled={submitting || !message.trim()}
              style={{
                padding: '10px 20px', borderRadius: '8px',
                background: submitting ? 'rgba(59,130,246,0.5)' : '#3b82f6',
                color: 'white', border: 'none',
                fontSize: '14px', fontWeight: '600',
                cursor: submitting ? 'not-allowed' : 'pointer',
              }}
            >
              {submitting ? 'Submitting...' : 'Submit Request'}
            </button>
            <button
              onClick={() => { setShowForm(false); setMessage(''); }}
              style={{
                padding: '10px 20px', borderRadius: '8px',
                background: 'rgba(255,255,255,0.1)',
                border: '1px solid rgba(255,255,255,0.2)',
                color: 'white', fontSize: '14px', cursor: 'pointer',
              }}
            >
              Cancel
            </button>
          </div>
        </motion.div>
      )}

      {/* Requests List */}
      {loading ? (
        <div style={{ color: 'rgba(255,255,255,0.5)' }}>Loading...</div>
      ) : requests.length === 0 ? (
        <div style={{
          background: 'rgba(255,255,255,0.05)', borderRadius: '14px',
          padding: '48px', textAlign: 'center',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>📨</div>
          <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: '15px' }}>
            No requests yet.
          </div>
          <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: '13px', marginTop: '6px' }}>
            Click "New Request" to submit a review request.
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '10px' }}>
          {requests.map((req) => {
            const st = statusConfig[req.status] || statusConfig.pending;
            return (
              <motion.div
                key={req.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '14px',
                  padding: '18px',
                }}
              >
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'center', marginBottom: '10px',
                }}>
                  <span style={{
                    fontSize: '12px', color: 'rgba(255,255,255,0.5)',
                  }}>
                    {new Date(req.created_at).toLocaleString()}
                  </span>
                  <span style={{
                    display: 'flex', alignItems: 'center', gap: '4px',
                    padding: '4px 12px', borderRadius: '12px',
                    fontSize: '12px', fontWeight: '600',
                    background: st.bg, color: st.color,
                  }}>
                    {st.icon}
                    {st.label}
                  </span>
                </div>
                <p style={{
                  fontSize: '14px', margin: 0, color: 'rgba(255,255,255,0.85)',
                  lineHeight: '1.5',
                }}>
                  {req.message}
                </p>
                {req.admin_notes && (
                  <div style={{
                    marginTop: '12px', padding: '12px',
                    background: 'rgba(59, 130, 246, 0.1)',
                    borderRadius: '8px',
                    border: '1px solid rgba(59, 130, 246, 0.2)',
                  }}>
                    <div style={{
                      fontSize: '11px', fontWeight: '600',
                      color: '#93c5fd', marginBottom: '4px',
                    }}>
                      Admin Response:
                    </div>
                    <div style={{
                      fontSize: '13px', color: 'rgba(255,255,255,0.8)',
                    }}>
                      {req.admin_notes}
                    </div>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      )}
    </StudentLayout>
  );
}
