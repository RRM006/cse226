import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileCheck } from 'lucide-react';
import { uploadCSV, uploadOCR } from '../lib/api';
import DashboardLayout from '../components/layout/DashboardLayout';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Select';
import { Input } from '../components/ui/Input';
import { FileUpload } from '../components/ui/FileUpload';

const programOptions = [
  { value: 'BSCSE', label: 'BSc in Computer Science & Engineering' },
  { value: 'BSEEE', label: 'BSc in Electrical & Electronic Engineering' },
  { value: 'LLB', label: 'LLB Honors' },
];

const auditLevelOptions = [
  { value: 1, label: 'Level 1 - Credit Tally' },
  { value: 2, label: 'Level 2 - CGPA Calculation' },
  { value: 3, label: 'Level 3 - Full Graduation Check' },
];

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [program, setProgram] = useState('BSCSE');
  const [auditLevel, setAuditLevel] = useState(3);
  const [waivers, setWaivers] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  function handleFileChange(selectedFile) {
    setFile(selectedFile);
    setError('');
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
    <DashboardLayout>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex p-3 rounded-2xl gradient-bg mb-4">
              <FileCheck className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-800">Run Audit</h1>
            <p className="text-slate-500 mt-1">Upload your transcript to verify graduation eligibility</p>
          </div>

          <Card className="shadow-xl">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Upload Transcript
                </label>
                <FileUpload 
                  onFileChange={handleFileChange}
                  error={error && !file ? error : undefined}
                />
              </div>

              {/* Program Selection */}
              <Select
                label="Program"
                options={programOptions}
                value={program}
                onChange={(e) => setProgram(e.target.value)}
              />

              {/* Audit Level */}
              <Select
                label="Audit Level"
                options={auditLevelOptions}
                value={auditLevel}
                onChange={(e) => setAuditLevel(parseInt(e.target.value))}
              />

              {/* Waivers */}
              <Input
                label="Waivers (Optional)"
                placeholder="e.g., ENG102, MAT116"
                value={waivers}
                onChange={(e) => setWaivers(e.target.value)}
                maxLength={20}
              />

              {/* Error Message */}
              {error && file && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                size="lg"
                className="w-full"
                isLoading={loading}
                disabled={!file}
              >
                {loading ? 'Processing...' : 'Run Audit'}
              </Button>
            </form>
          </Card>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
