import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllUsers, updateUserRole, getCurrentUser, getUserHistory } from '../lib/api';

export default function AdminPanel() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userHistory, setUserHistory] = useState([]);

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
    try {
      const data = await getUserHistory(userId, 20, 0);
      setUserHistory(data.scans || []);
      setSelectedUser(userId);
    } catch (err) {
      alert('Failed to load history: ' + err.message);
    }
  }

  function closeHistoryModal() {
    setSelectedUser(null);
    setUserHistory([]);
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Admin Panel</h1>
        <div style={styles.nav}>
          <button onClick={() => navigate('/upload')} style={styles.navBtn}>Upload</button>
          <button onClick={() => navigate('/history')} style={styles.navBtn}>History</button>
        </div>
      </div>

      {error && <p style={styles.error}>{error}</p>}

      <div style={styles.tableContainer}>
        <h2 style={styles.subtitle}>All Users</h2>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Role</th>
              <th style={styles.th}>Scans</th>
              <th style={styles.th}>Created</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} style={styles.tr}>
                <td style={styles.td}>{user.email}</td>
                <td style={styles.td}>
                  <span style={user.role === 'admin' ? styles.adminBadge : styles.studentBadge}>
                    {user.role}
                  </span>
                </td>
                <td style={styles.td}>{user.scan_count}</td>
                <td style={styles.td}>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</td>
                <td style={styles.td}>
                  <button 
                    onClick={() => handleViewHistory(user.id)}
                    style={styles.viewBtn}
                  >
                    View History
                  </button>
                  <button 
                    onClick={() => handleRoleChange(user.id, user.role === 'admin' ? 'student' : 'admin')}
                    style={styles.roleBtn}
                  >
                    Make {user.role === 'admin' ? 'Student' : 'Admin'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedUser && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <h2 style={styles.modalTitle}>User Scan History</h2>
            {userHistory.length === 0 ? (
              <p>No scans found.</p>
            ) : (
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Date</th>
                    <th style={styles.th}>Program</th>
                    <th style={styles.th}>Level</th>
                    <th style={styles.th}>Eligible</th>
                  </tr>
                </thead>
                <tbody>
                  {userHistory.map((scan) => (
                    <tr key={scan.scan_id} style={styles.tr}>
                      <td style={styles.td}>
                        {scan.created_at ? new Date(scan.created_at).toLocaleDateString() : '-'}
                      </td>
                      <td style={styles.td}>{scan.program}</td>
                      <td style={styles.td}>{scan.audit_level}</td>
                      <td style={styles.td}>
                        {scan.summary?.eligible === true && 'Yes'}
                        {scan.summary?.eligible === false && 'No'}
                        {scan.summary?.eligible === undefined && '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <button onClick={closeHistoryModal} style={styles.closeBtn}>
              Close
            </button>
          </div>
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
  subtitle: {
    margin: '0 0 1rem',
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
    marginBottom: '1rem'
  },
  tableContainer: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '8px',
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
  adminBadge: {
    padding: '4px 8px',
    backgroundColor: '#e3f2fd',
    color: '#1565c0',
    borderRadius: '4px',
    fontSize: '0.875rem',
    fontWeight: '500'
  },
  studentBadge: {
    padding: '4px 8px',
    backgroundColor: '#f5f5f5',
    color: '#666',
    borderRadius: '4px',
    fontSize: '0.875rem',
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
  roleBtn: {
    padding: '6px 12px',
    backgroundColor: '#ff9800',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  modalContent: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    maxWidth: '600px',
    width: '90%',
    maxHeight: '80vh',
    overflow: 'auto'
  },
  modalTitle: {
    margin: '0 0 1rem'
  },
  closeBtn: {
    marginTop: '1rem',
    padding: '8px 16px',
    backgroundColor: '#666',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  }
};
