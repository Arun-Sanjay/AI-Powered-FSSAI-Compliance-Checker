import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { analyzeLabel } from '../services/api';
import AnimatedLoader from './AnimatedLoader';

export default function UploadPage({ onResult, loading, setLoading }) {
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    setError(null);
    setLoading(true);
    try {
      const result = await analyzeLabel(acceptedFiles[0]);
      onResult(result);
    } catch (err) {
      console.error('Analysis failed:', err);
      const status = err.response?.status;
      if (status === 413) {
        setError('File too large. Maximum size is 10MB.');
      } else if (status === 400) {
        setError('Invalid file type. Please upload a JPG, PNG, or WebP image.');
      } else if (status === 500) {
        setError('Analysis failed. The AI could not read this label. Try a clearer image.');
      } else {
        setError('Cannot reach the server. Make sure the backend is running on port 8000.');
      }
    } finally {
      setLoading(false);
    }
  }, [onResult, setLoading]);

  const onDropRejected = useCallback((fileRejections) => {
    const rejection = fileRejections[0];
    if (rejection?.errors?.some(e => e.code === 'file-too-large')) {
      setError('File too large. Maximum size is 10MB.');
    } else {
      setError('Invalid file type. Please upload a JPG, PNG, or WebP image.');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled: loading,
  });

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-4xl font-bold text-slate-800 mb-2">
          Food Label Analyzer
        </h1>
        <p className="text-lg text-slate-500 mb-8">
          AI-Powered FSSAI Compliance Checker
        </p>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-2xl p-12 cursor-pointer transition-all duration-200 ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-slate-300 bg-white hover:border-blue-400 hover:bg-blue-50/50'
          } ${loading ? 'opacity-50 cursor-wait' : ''}`}
        >
          <input {...getInputProps()} />
          {loading ? (
            <AnimatedLoader />
          ) : (
            <div className="space-y-3">
              <div className="text-5xl">📷</div>
              <p className="text-slate-700 font-medium text-lg">
                {isDragActive
                  ? 'Drop the label image here...'
                  : 'Drag & drop a food label image, or click to browse'}
              </p>
              <p className="text-sm text-slate-400">
                Supports JPG, PNG, WebP (max 10MB)
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 flex items-center justify-between">
            <p className="text-sm">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-400 hover:text-red-600 text-lg font-bold cursor-pointer"
            >
              &times;
            </button>
          </div>
        )}

        <p className="mt-6 text-xs text-slate-400">
          Biosafety & Food Safety — Experiential Learning Project | RVCE 2025-26
        </p>
      </div>
    </div>
  );
}
