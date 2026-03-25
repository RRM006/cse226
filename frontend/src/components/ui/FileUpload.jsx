import { useState, useRef } from 'react';
import { Upload, FileText, Image, X } from 'lucide-react';
import { cn } from '../../lib/utils';

export function FileUpload({ 
  onFileChange, 
  accept = '.csv,.png,.jpg,.jpeg,.pdf',
  error 
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  };

  const handleFile = (selectedFile) => {
    setFile(selectedFile);
    onFileChange?.(selectedFile);
  };

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    setFile(null);
    onFileChange?.(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const getFileIcon = () => {
    if (!file) return <Upload className="w-10 h-10 text-slate-400" />;
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (['png', 'jpg', 'jpeg'].includes(ext)) {
      return <Image className="w-10 h-10 text-blue-500" />;
    }
    if (ext === 'pdf') {
      return <FileText className="w-10 h-10 text-red-500" />;
    }
    return <FileText className="w-10 h-10 text-green-500" />;
  };

  return (
    <div className="w-full">
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
          'hover:border-primary-400 hover:bg-primary-50/50',
          isDragging ? 'border-primary-500 bg-primary-50' : 'border-slate-300',
          error && 'border-red-500'
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
        />
        
        {file ? (
          <div className="flex items-center justify-center gap-3">
            {getFileIcon()}
            <div className="flex-1 text-left">
              <p className="font-medium text-slate-700">{file.name}</p>
              <p className="text-sm text-slate-500">
                {(file.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <button
              type="button"
              onClick={handleRemove}
              className="p-1 hover:bg-slate-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex justify-center">
              <Upload className="w-10 h-10 text-slate-400" />
            </div>
            <p className="text-slate-600 font-medium">
              Drop your file here or click to browse
            </p>
            <p className="text-sm text-slate-400">
              Supports CSV, PNG, JPG, PDF (max 10MB)
            </p>
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  );
}
