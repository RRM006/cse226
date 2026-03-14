import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, AlertTriangle, FileText, ArrowLeft } from 'lucide-react';
import { getScanById } from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { formatDate, getProgramLabel, getAuditLevelLabel } from '../lib/utils';

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
