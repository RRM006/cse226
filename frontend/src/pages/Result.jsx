import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, AlertTriangle, FileText, ArrowLeft, Save, Edit2 } from 'lucide-react';
import { getScanById, saveAuditWithStudentId } from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatDate, getProgramLabel, getAuditLevelLabel } from '../lib/utils';

const STUDENT_ID_REGEX = /^2\d{9}$/;

function isValidStudentId(id) {
  return STUDENT_ID_REGEX.test(id.trim());
}

export default function Result() {
  const { scanId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [result, setResult] = useState(location.state?.result || null);
  const [loading, setLoading] = useState(!result);
  const [error, setError] = useState('');

  const [confirmStudentId, setConfirmStudentId] = useState('');
  const [editingId, setEditingId] = useState(false);
  const [savingId, setSavingId] = useState(false);
  const [idSaved, setIdSaved] = useState(false);
  const [idError, setIdError] = useState('');

  useEffect(() => {
    if (!result && scanId) {
      loadResult();
    }
  }, [scanId, result]);

  useEffect(() => {
    if (result) {
      const resultJson = result.result_json || {};
      const detectedId = resultJson.student_id || '';
      setConfirmStudentId(detectedId);
      if (isValidStudentId(detectedId)) {
        setIdSaved(true);
      }
    }
  }, [result]);

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

  async function handleSaveStudentId() {
    const trimmed = confirmStudentId.trim();
    if (!trimmed) {
      setIdError('Student ID is required');
      return;
    }
    if (!isValidStudentId(trimmed)) {
      setIdError('Invalid format. Must be 10 digits starting with 2 (e.g., 2211234567)');
      return;
    }
    setSavingId(true);
    setIdError('');
    try {
      const resultJson = result.result_json || {};
      await saveAuditWithStudentId({
        student_id: trimmed,
        program: result.program || resultJson.program || '',
        input_type: result.input_type || 'csv',
        raw_input: '',
        waivers: resultJson.waivers_applied || [],
        audit_level: result.audit_level || resultJson.audit_level || 3,
        result_json: { ...resultJson, student_id: trimmed },
        result_text: result.result_text || '',
      });
      setIdSaved(true);
      setEditingId(false);
    } catch (err) {
      setIdError(err.message);
    } finally {
      setSavingId(false);
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-500">Loading result...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <Card className="max-w-2xl mx-auto text-center py-12">
          <div className="flex justify-center mb-4">
            <div className="p-4 rounded-full bg-red-100">
              <XCircle className="w-8 h-8 text-red-500" />
            </div>
          </div>
          <h3 className="text-lg font-medium text-slate-700 mb-2">Error Loading Result</h3>
          <p className="text-slate-500 mb-6">{error}</p>
          <Button onClick={() => navigate('/upload')}>
            Back to Upload
          </Button>
        </Card>
      </DashboardLayout>
    );
  }

  if (!result) {
    return (
      <DashboardLayout>
        <Card className="max-w-2xl mx-auto text-center py-12">
          <h3 className="text-lg font-medium text-slate-700 mb-2">No Result Found</h3>
          <p className="text-slate-500 mb-6">The requested result could not be found</p>
          <Button onClick={() => navigate('/upload')}>
            Back to Upload
          </Button>
        </Card>
      </DashboardLayout>
    );
  }

  const summary = result.summary || {};
  const resultJson = result.result_json || {};
  const detectedId = resultJson.student_id || '';
  const alreadyValid = isValidStudentId(detectedId) && !editingId && idSaved;

  return (
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="max-w-4xl mx-auto">
          {/* Back Button */}
          <Button 
            variant="ghost" 
            onClick={() => navigate('/history')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to History
          </Button>

          {/* NSU Student ID Confirmation — always shows until valid ID confirmed */}
          <Card className={`mb-6 border-2 ${alreadyValid ? 'border-green-300 bg-green-50' : 'border-amber-300 bg-amber-50'}`}>
            <div className="flex items-center gap-2 mb-3">
              {alreadyValid ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              )}
              <h3 className="text-lg font-semibold text-slate-800">
                {alreadyValid ? 'Student ID Confirmed' : 'Confirm NSU Student ID'}
              </h3>
            </div>

            {alreadyValid ? (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-700">
                    Audit saved for student <strong>{detectedId}</strong>
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    Student can now view this result in their portal
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => { setIdSaved(false); setEditingId(true); }}>
                  <Edit2 className="w-4 h-4 mr-1" /> Change
                </Button>
              </div>
            ) : (
              <div>
                <p className="text-sm text-amber-700 mb-3">
                  {editingId || !detectedId || detectedId === 'Unknown'
                    ? 'Enter the NSU student ID for this audit:'
                    : `Auto-detected ID: ${detectedId}. Confirm or correct it:`}
                </p>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={confirmStudentId}
                    onChange={(e) => { setConfirmStudentId(e.target.value); setIdError(''); }}
                    placeholder="e.g., 2211234567"
                    maxLength={10}
                    className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <Button onClick={handleSaveStudentId} isLoading={savingId} disabled={!confirmStudentId.trim()}>
                    <Save className="w-4 h-4 mr-1" /> Save
                  </Button>
                </div>
                {idError && (
                  <p className="text-sm text-red-600 mt-2">{idError}</p>
                )}
                <p className="text-xs text-amber-600 mt-2">
                  Must be 10 digits starting with 2. If the student doesn't exist, an account will be auto-created with default password = student ID
                </p>
              </div>
            )}
          </Card>

          {/* Status Banner */}
          {summary.eligible === true && (
            <Card className="mb-6 bg-green-50 border-green-200">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-full bg-green-100">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-green-800">Congratulations!</h2>
                  <p className="text-green-700">You meet all graduation requirements</p>
                </div>
              </div>
            </Card>
          )}
          
          {summary.eligible === false && (
            <Card className="mb-6 bg-red-50 border-red-200">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-full bg-red-100">
                  <XCircle className="w-8 h-8 text-red-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-red-800">Not Eligible</h2>
                  <p className="text-red-700">You have not yet met all graduation requirements</p>
                </div>
              </div>
            </Card>
          )}

          {/* Summary Card */}
          <Card className="mb-6 shadow-xl">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Audit Summary</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 mb-1">Program</p>
                <p className="font-semibold text-slate-800">{getProgramLabel(result.program)}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 mb-1">Level</p>
                <p className="font-semibold text-slate-800">{getAuditLevelLabel(result.audit_level)}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 mb-1">Total Credits</p>
                <p className="font-semibold text-slate-800">{summary.total_credits ?? '-'}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500 mb-1">CGPA</p>
                <p className="font-semibold text-slate-800">{summary.cgpa ?? '-'}</p>
              </div>
            </div>

            {summary.missing_courses > 0 && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
                <div className="flex items-center gap-2 text-amber-700 mb-2">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="font-medium">{summary.missing_courses} Missing Course{summary.missing_courses !== 1 ? 's' : ''}</span>
                </div>
                <p className="text-sm text-amber-600">You need to complete additional courses to become eligible</p>
              </div>
            )}

            <p className="text-sm text-slate-500 mt-4">
              Scan ID: {result.scan_id} • {formatDate(result.created_at)}
            </p>
          </Card>

          {/* Full Result Card */}
          <Card className="mb-6 shadow-xl">
            <div className="flex items-center gap-2 mb-4">
              <FileText className="w-5 h-5 text-slate-600" />
              <h3 className="text-lg font-semibold text-slate-800">Detailed Result</h3>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 max-h-[400px] overflow-auto">
              <pre className="text-sm text-slate-600 whitespace-pre-wrap font-mono">
                {result.result_text || 'No detailed result available'}
              </pre>
            </div>
          </Card>

          {/* Actions */}
          <div className="flex justify-center gap-4">
            <Button onClick={() => navigate('/history')}>
              View History
            </Button>
            <Button variant="secondary" onClick={() => navigate('/upload')}>
              Run New Audit
            </Button>
          </div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
