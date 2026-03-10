import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHistory, deleteScan } from '../lib/api';

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

  function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <p>Loading history...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Scan History</h1>
        <div style={styles.nav}>
          <button onClick={() => navigate('/upload')} style={styles.navBtn}>Upload</button>
          <button onClick={() => navigate('/admin')} style={styles.navBtn}>Admin</button>
        </div>
      </div>

      {error && <p style={styles.error}>{error}</p>}

      {scans.length === 0 ? (
        <div style={styles.empty}>
          <p>No scans found.</p>
          <button onClick={() => navigate('/upload')} style={styles.button}>
            Run Your First Audit
          </button>
        </div>
      ) : (
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Date</th>
                <th style={styles.th}>Type</th>
                <th style={styles.th}>Program</th>
                <th style={styles.th}>Level</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.scan_id} style={styles.tr}>
                  <td style={styles.td}>{formatDate(scan.created_at)}</td>
                  <td style={styles.td}>{scan.input_type}</td>
                  <td style={styles.td}>{scan.program}</td>
                  <td style={styles.td}>{scan.audit_level}</td>
                  <td style={styles.td}>
                    {scan.summary?.eligible === true && <span style={styles.eligible}>Eligible</span>}
                    {scan.summary?.eligible === false && <span style={styles.notEligible}>Not Eligible</span>}
                    {scan.summary?.eligible === undefined && <span>-</span>}
                  </td>
                  <td style={styles.td}>
                    <button 
                      onClick={() => navigate(`/result/${scan.scan_id}`)}
                      style={styles.viewBtn}
                    >
                      View
                    </button>
                    <button 
                      onClick={() => handleDelete(scan.scan_id)}
                      disabled={deleteId === scan.scan_id}
                      style={styles.deleteBtn}
                    >
                      {deleteId === scan.scan_id ? 'Deleting...' : 'Delete'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
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
  error: {
    color: '#d32f2f',
    marginBottom: '1rem',
    padding: '8px',
    backgroundColor: '#ffebee',
    borderRadius: '4px'
  },
  empty: {
    textAlign: 'center',
    padding: '3rem',
    backgroundColor: 'white',
    borderRadius: '8px'
  },
  tableContainer: {
    backgroundColor: 'white',
    borderRadius: '8px',
    overflow: 'hidden',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse'
  },
  th: {
    textAlign: 'left',
    padding: '12px',
    backgroundColor: '#f5f5f5',
    fontWeight: '600',
    borderBottom: '1px solid #ddd'
  },
  tr: {
    borderBottom: '1px solid #eee'
  },
  td: {
    padding: '12px'
  },
  eligible: {
    color: 'green',
    fontWeight: '500'
  },
  notEligible: {
    color: 'red',
    fontWeight: '500'
  },
  viewBtn: {
    padding: '6px 12px',
    backgroundColor: '#4285f4',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    marginRight: '8px'
  },
  deleteBtn: {
    padding: '6px 12px',
    backgroundColor: '#d32f2f',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
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
  }
};
