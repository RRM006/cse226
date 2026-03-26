import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, ChevronDown, ChevronUp, Send } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getStudentAuditResults, getStudentAuditResultById, submitStudentRequest } from '../lib/api';
import { getStudentToken } from '../lib/supabase';
import StudentLayout from '../components/StudentLayout';

export default function StudentAuditResults() {
  const navigate = useNavigate();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showRequestForm, setShowRequestForm] = useState(null);
  const [requestMessage, setRequestMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!getStudentToken()) {
      navigate('/student/login');
      return;
    }
    loadResults();
  }, []);

  const loadResults = async () => {
    setLoading(true);
    try {
      const data = await getStudentAuditResults();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = async (id) => {
    if (expandedId === id) {
      setExpandedId(null);
      setDetail(null);
      return;
    }
    setExpandedId(id);
    setDetailLoading(true);
    try {
      const data = await getStudentAuditResultById(id);
      setDetail(data);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSubmitRequest = async (auditResultId) => {
    if (!requestMessage.trim()) return;
    setSubmitting(true);
    try {
      await submitStudentRequest(requestMessage, auditResultId);
      setShowRequestForm(null);
      setRequestMessage('');
      alert('Request submitted successfully!');
    } catch (err) {
      alert('Failed: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <StudentLayout>
      <h2 style={{ fontSize: '22px', fontWeight: '700', marginBottom: '24px' }}>
        Audit Results
      </h2>

      {loading ? (
        <div style={{ color: 'rgba(255,255,255,0.5)' }}>Loading...</div>
      ) : results.length === 0 ? (
        <div style={{
          background: 'rgba(255,255,255,0.05)', borderRadius: '14px',
          padding: '48px', textAlign: 'center',
        }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>📋</div>
          <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: '15px' }}>
            No audit results available yet.
          </div>
          <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: '13px', marginTop: '6px' }}>
            Your administrator will upload your transcript results here.
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {results.map((result) => (
            <motion.div
              key={result.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '14px',
                overflow: 'hidden',
              }}
            >
              {/* Header row */}
              <div
                onClick={() => toggleExpand(result.id)}
                style={{
                  padding: '16px 20px',
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'center', cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{
                    width: '40px', height: '40px', borderRadius: '10px',
                    background: result.eligible ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    {result.eligible
                      ? <CheckCircle size={20} color="#22c55e" />
                      : <XCircle size={20} color="#ef4444" />
                    }
                  </div>
                  <div>
                    <div style={{ fontWeight: '600', fontSize: '15px' }}>
                      {result.program} — Level {result.audit_level}
                    </div>
                    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
                      {new Date(result.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    padding: '4px 14px', borderRadius: '20px',
                    fontSize: '12px', fontWeight: '600',
                    background: result.eligible ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: result.eligible ? '#86efac' : '#fca5a5',
                  }}>
                    {result.eligible ? 'Eligible' : 'Not Eligible'}
                  </span>
                  {expandedId === result.id
                    ? <ChevronUp size={18} color="rgba(255,255,255,0.4)" />
                    : <ChevronDown size={18} color="rgba(255,255,255,0.4)" />
                  }
                </div>
              </div>

              {/* Expanded detail */}
              {expandedId === result.id && (
                <div style={{
                  borderTop: '1px solid rgba(255,255,255,0.1)',
                  padding: '16px 20px',
                  background: 'rgba(0,0,0,0.15)',
                }}>
                  {detailLoading ? (
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px' }}>
                      Loading details...
                    </div>
                  ) : detail ? (
                    <>
                      {/* Eligibility status */}
                      <div style={{
                        marginBottom: '16px',
                        padding: '14px',
                        borderRadius: '10px',
                        background: detail.eligible
                          ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        border: `1px solid ${detail.eligible
                          ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                      }}>
                        <div style={{
                          fontWeight: '600', fontSize: '14px', marginBottom: '4px',
                          color: detail.eligible ? '#86efac' : '#fca5a5',
                        }}>
                          {detail.eligible
                            ? '✅ You are eligible'
                            : '❌ You are not eligible'
                          }
                        </div>
                        {detail.eligible && (
                          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)' }}>
                            Congratulations! Your transcript meets the requirements.
                          </div>
                        )}
                      </div>

                      {/* Result text */}
                      {detail.result_text && (
                        <div style={{
                          background: 'rgba(255,255,255,0.05)',
                          borderRadius: '10px',
                          padding: '14px',
                          marginBottom: '16px',
                          fontSize: '13px',
                          color: 'rgba(255,255,255,0.8)',
                          whiteSpace: 'pre-wrap',
                          maxHeight: '300px',
                          overflowY: 'auto',
                        }}>
                          {detail.result_text}
                        </div>
                      )}

                      {/* Result JSON summary */}
                      {detail.result_json && (
                        <div style={{
                          background: 'rgba(255,255,255,0.05)',
                          borderRadius: '10px',
                          padding: '14px',
                          marginBottom: '16px',
                        }}>
                          <div style={{
                            fontSize: '12px', fontWeight: '600',
                            color: 'rgba(255,255,255,0.5)', marginBottom: '8px',
                          }}>
                            Summary
                          </div>
                          {Object.entries(detail.result_json).map(([key, val]) => {
                            if (typeof val === 'object') return null;
                            return (
                              <div key={key} style={{
                                display: 'flex', justifyContent: 'space-between',
                                padding: '6px 0',
                                borderBottom: '1px solid rgba(255,255,255,0.05)',
                                fontSize: '13px',
                              }}>
                                <span style={{ color: 'rgba(255,255,255,0.6)', textTransform: 'capitalize' }}>
                                  {key.replace(/_/g, ' ')}
                                </span>
                                <span style={{ fontWeight: '600' }}>
                                  {String(val)}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Request button for failed results */}
                      {!detail.eligible && (
                        <>
                          {showRequestForm !== result.id ? (
                            <button
                              onClick={() => setShowRequestForm(result.id)}
                              style={{
                                display: 'flex', alignItems: 'center', gap: '6px',
                                padding: '10px 16px', borderRadius: '8px',
                                background: 'rgba(245, 158, 11, 0.15)',
                                border: '1px solid rgba(245, 158, 11, 0.3)',
                                color: '#fcd34d', cursor: 'pointer',
                                fontSize: '13px', fontWeight: '500',
                              }}
                            >
                              <Send size={14} />
                              Submit Review Request for This Result
                            </button>
                          ) : (
                            <div style={{
                              background: 'rgba(255,255,255,0.05)',
                              borderRadius: '10px', padding: '14px',
                            }}>
                              <textarea
                                value={requestMessage}
                                onChange={(e) => setRequestMessage(e.target.value)}
                                placeholder="Explain why you need a review..."
                                style={{
                                  width: '100%', minHeight: '80px', padding: '10px',
                                  background: 'rgba(0,0,0,0.2)',
                                  border: '1px solid rgba(255,255,255,0.15)',
                                  borderRadius: '8px', color: 'white',
                                  fontSize: '13px', resize: 'vertical', outline: 'none',
                                }}
                              />
                              <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                                <button
                                  onClick={() => handleSubmitRequest(result.id)}
                                  disabled={submitting || !requestMessage.trim()}
                                  style={{
                                    padding: '8px 16px', borderRadius: '8px',
                                    background: submitting ? 'rgba(59,130,246,0.5)' : '#3b82f6',
                                    color: 'white', border: 'none',
                                    fontSize: '13px', fontWeight: '600',
                                    cursor: submitting ? 'not-allowed' : 'pointer',
                                  }}
                                >
                                  {submitting ? 'Submitting...' : 'Submit'}
                                </button>
                                <button
                                  onClick={() => { setShowRequestForm(null); setRequestMessage(''); }}
                                  style={{
                                    padding: '8px 16px', borderRadius: '8px',
                                    background: 'rgba(255,255,255,0.1)',
                                    border: '1px solid rgba(255,255,255,0.2)',
                                    color: 'white', fontSize: '13px', cursor: 'pointer',
                                  }}
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          )}
                        </>
                      )}
                    </>
                  ) : (
                    <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px' }}>
                      Failed to load details.
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </StudentLayout>
  );
}
