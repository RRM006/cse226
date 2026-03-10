import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadCSV, uploadOCR } from '../lib/api';

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [program, setProgram] = useState('BSCSE');
  const [auditLevel, setAuditLevel] = useState(3);
  const [waivers, setWaivers] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function handleFileChange(e) {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const isImage = file.type.startsWith('image/') || 
                      file.name.endsWith('.png') || 
                      file.name.endsWith('.jpg') || 
                      file.name.endsWith('.jpeg');
      const isCSV = file.name.endsWith('.csv');
      
      if (!isImage && !isCSV) {
        throw new Error('Please upload a CSV or image file (PNG, JPG)');
      }

      const waiverList = waivers.split(',').map(w => w.trim()).filter(w => w);
      
      let result;
      if (isCSV) {
        result = await uploadCSV(file, program, auditLevel, waiverList.join(','));
      } else {
        result = await uploadOCR(file, program, auditLevel, waiverList.join(','));
      }

      navigate(`/result/${result.scan_id}`, { state: { result } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Run Audit</h1>
        <div style={styles.nav}>
          <button onClick={() => navigate('/history')} style={styles.navBtn}>History</button>
          <button onClick={() => navigate('/admin')} style={styles.navBtn}>Admin</button>
        </div>
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.field}>
          <label style={styles.label}>Upload File (CSV or Image)</label>
          <input 
            type="file" 
            accept=".csv,.png,.jpg,.jpeg" 
            onChange={handleFileChange}
            style={styles.fileInput}
          />
          {file && <p style={styles.fileName}>{file.name}</p>}
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Program</label>
          <select 
            value={program} 
            onChange={(e) => setProgram(e.target.value)}
            style={styles.select}
          >
            <option value="BSCSE">BSc in Computer Science & Engineering</option>
            <option value="BSEEE">BSc in Electrical & Electronic Engineering</option>
            <option value="LLB">LLB Honors</option>
          </select>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Audit Level</label>
          <select 
            value={auditLevel} 
            onChange={(e) => setAuditLevel(parseInt(e.target.value))}
            style={styles.select}
          >
            <option value={1}>Level 1 - Credit Tally</option>
            <option value={2}>Level 2 - CGPA Calculation</option>
            <option value={3}>Level 3 - Full Graduation Check</option>
          </select>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Waivers (comma-separated, optional)</label>
          <input 
            type="text" 
            value={waivers}
            onChange={(e) => setWaivers(e.target.value)}
            placeholder="e.g., ENG102, MAT116"
            style={styles.input}
          />
        </div>

        {error && <p style={styles.error}>{error}</p>}

        <button 
          type="submit" 
          disabled={loading || !file}
          style={{...styles.button, opacity: loading || !file ? 0.6 : 1}}
        >
          {loading ? 'Processing...' : 'Run Audit'}
        </button>
      </form>
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
  form: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    maxWidth: '500px',
    margin: '0 auto'
  },
  field: {
    marginBottom: '1.5rem'
  },
  label: {
    display: 'block',
    marginBottom: '0.5rem',
    fontWeight: '500',
    color: '#333'
  },
  fileInput: {
    width: '100%',
    padding: '8px'
  },
  fileName: {
    margin: '0.5rem 0 0',
    color: '#666',
    fontSize: '0.875rem'
  },
  select: {
    width: '100%',
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '1rem'
  },
  input: {
    width: '100%',
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '1rem'
  },
  button: {
    width: '100%',
    padding: '12px',
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
    marginBottom: '1rem',
    padding: '8px',
    backgroundColor: '#ffebee',
    borderRadius: '4px'
  }
};
