import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { getScanById } from '../lib/api';

export default function Result() {
  const { scanId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [result, setResult] = useState(location.state?.result || null);
  const [loading, setLoading] = useState(!result);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!result && scanId) {
      loadResult();
    }
  }, [scanId, result]);

  async function loadResult() {
    try {
      const data = await getScanById(scanId);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <p>Loading result...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <p style={styles.error}>{error}</p>
        <button onClick={() => navigate('/upload')} style={styles.button}>
          Back to Upload
        </button>
      </div>
    );
  }

  if (!result) {
    return (
      <div style={styles.container}>
        <p>No result found</p>
        <button onClick={() => navigate('/upload')} style={styles.button}>
          Back to Upload
        </button>
      </div>
    );
  }

  const summary = result.summary || {};
  const resultJson = result.result_json || {};

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Audit Result</h1>
        <div style={styles.nav}>
          <button onClick={() => navigate('/history')} style={styles.navBtn}>History</button>
          <button onClick={() => navigate('/admin')} style={styles.navBtn}>Admin</button>
        </div>
      </div>

      <div style={styles.card}>
        <div style={styles.summaryCard}>
          <h2 style={styles.cardTitle}>Summary</h2>
          <div style={styles.grid}>
            <div style={styles.gridItem}>
              <span style={styles.label}>Student ID</span>
              <span style={styles.value}>{result.student_id || '-'}</span>
            </div>
            <div style={styles.gridItem}>
              <span style={styles.label}>Program</span>
              <span style={styles.value}>{result.program}</span>
            </div>
            <div style={styles.gridItem}>
              <span style={styles.label}>Audit Level</span>
              <span style={styles.value}>{result.audit_level}</span>
            </div>
            <div style={styles.gridItem}>
              <span style={styles.label}>Total Credits</span>
              <span style={styles.value}>{summary.total_credits ?? '-'}</span>
            </div>
            <div style={styles.gridItem}>
              <span style={styles.label}>CGPA</span>
              <span style={styles.value}>{summary.cgpa ?? '-'}</span>
            </div>
            <div style={styles.gridItem}>
              <span style={styles.label}>Standing</span>
              <span style={styles.value}>{summary.standing ?? '-'}</span>
            </div>
            <div style={styles.gridItem}>
              <span style={styles.label}>Eligible</span>
              <span style={{
                ...styles.value,
                color: summary.eligible === true ? 'green' : summary.eligible === false ? 'red' : 'inherit'
              }}>
                {summary.eligible === true ? 'Yes' : summary.eligible === false ? 'No' : '-'}
              </span>
            </div>
            {result.ocr_confidence && (
              <div style={styles.gridItem}>
                <span style={styles.label}>OCR Confidence</span>
                <span style={styles.value}>{(result.ocr_confidence * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>

          {summary.missing_courses && summary.missing_courses.length > 0 && (
            <div style={styles.missingSection}>
              <h3 style={styles.missingTitle}>Missing Courses</h3>
              <ul style={styles.missingList}>
                {summary.missing_courses.map((course, idx) => (
                  <li key={idx}>{course}</li>
                ))}
              </ul>
            </div>
          )}

          <p style={styles.savedNote}>This result has been saved to your history.</p>
        </div>

        <div style={styles.resultSection}>
          <h2 style={styles.cardTitle}>Full Result</h2>
          <pre style={styles.pre}>
            {result.result_text || 'No detailed result available'}
          </pre>
        </div>

        <button onClick={() => navigate('/upload')} style={styles.button}>
          Run New Audit
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    fontFamily: 'system-ui, sans-serif',
    padding: '1rem'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem'
  },
  title: {
    margin: 0,
    color: '#1a1a1a'
  },
  nav: {
    display: 'flex',
    gap: '0.5rem'
  },
  navBtn: {
    padding: '8px 16px',
    backgroundColor: '#666',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  card: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    maxWidth: '800px',
    margin: '0 auto'
  },
  summaryCard: {
    marginBottom: '2rem'
  },
  cardTitle: {
    margin: '0 0 1rem',
    color: '#1a1a1a',
    fontSize: '1.25rem'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '1rem'
  },
  gridItem: {
    display: 'flex',
    flexDirection: 'column'
  },
  label: {
    fontSize: '0.875rem',
    color: '#666',
    marginBottom: '0.25rem'
  },
  value: {
    fontSize: '1.125rem',
    fontWeight: '500',
    color: '#1a1a1a'
  },
  missingSection: {
    marginTop: '1.5rem',
    padding: '1rem',
    backgroundColor: '#fff3e0',
    borderRadius: '4px'
  },
  missingTitle: {
    margin: '0 0 0.5rem',
    color: '#e65100'
  },
  missingList: {
    margin: 0,
    paddingLeft: '1.5rem'
  },
  savedNote: {
    marginTop: '1rem',
    color: '#4caf50',
    fontSize: '0.875rem'
  },
  resultSection: {
    marginBottom: '2rem'
  },
  pre: {
    backgroundColor: '#f5f5f5',
    padding: '1rem',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '0.875rem',
    maxHeight: '400px',
    whiteSpace: 'pre-wrap',
    fontFamily: 'monospace'
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#4285f4',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '1rem',
    cursor: 'pointer',
    fontWeight: '500'
  },
  error: {
    color: '#d32f2f',
    marginBottom: '1rem'
  }
};
