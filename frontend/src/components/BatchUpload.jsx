import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { analyzeLabel } from '../services/api';

export default function BatchUpload({ onResults }) {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const [error, setError] = useState(null);

  const onDrop = useCallback((accepted) => {
    setFiles((prev) => [...prev, ...accepted].slice(0, 10));
    setError(null);
  }, []);

  const onDropRejected = useCallback(() => {
    setError('Some files were rejected. Only JPG, PNG, WebP images under 10MB are accepted.');
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 10,
    maxSize: 10 * 1024 * 1024,
    disabled: processing,
  });

  function removeFile(index) {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleAnalyze() {
    if (files.length === 0) return;
    setProcessing(true);
    setResults([]);
    setError(null);

    const batchResults = [];
    for (let i = 0; i < files.length; i++) {
      setCurrentIndex(i);
      try {
        const result = await analyzeLabel(files[i]);
        batchResults.push({
          fileName: files[i].name,
          result,
          error: null,
        });
      } catch (err) {
        batchResults.push({
          fileName: files[i].name,
          result: null,
          error: err.response?.data?.detail || 'Analysis failed',
        });
      }
      setResults([...batchResults]);
    }

    setProcessing(false);
    setCurrentIndex(-1);
    onResults(batchResults);
  }

  const completedCount = results.length;
  const progressPct = files.length > 0 ? Math.round((completedCount / files.length) * 100) : 0;

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-slate-800">Batch Analysis</h1>
        <p className="text-slate-500">
          Upload up to 10 food label images for bulk compliance checking.
        </p>

        {/* Drop zone */}
        {!processing && (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-8 cursor-pointer transition-all text-center ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-slate-300 bg-white hover:border-blue-400'
            }`}
          >
            <input {...getInputProps()} />
            <p className="text-slate-600">
              {isDragActive
                ? 'Drop images here...'
                : 'Drag & drop label images, or click to browse'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              JPG, PNG, WebP — max 10MB each — up to 10 files
            </p>
          </div>
        )}

        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}

        {/* File list */}
        {files.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-slate-600">
                {files.length} file{files.length !== 1 ? 's' : ''} selected
              </h2>
              {!processing && (
                <button
                  onClick={handleAnalyze}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 cursor-pointer"
                >
                  Analyze All
                </button>
              )}
            </div>

            {/* Progress bar */}
            {processing && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Processing {currentIndex + 1} of {files.length}...</span>
                  <span>{progressPct}%</span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-300"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              {files.map((file, i) => {
                const batchResult = results[i];
                return (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-2 rounded-lg bg-slate-50"
                  >
                    <div className="w-10 h-10 bg-slate-200 rounded overflow-hidden shrink-0">
                      <img
                        src={URL.createObjectURL(file)}
                        alt={file.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-700 truncate">{file.name}</p>
                      <p className="text-xs text-slate-400">
                        {(file.size / 1024).toFixed(0)} KB
                      </p>
                    </div>

                    {/* Status */}
                    {batchResult ? (
                      batchResult.error ? (
                        <span className="text-xs text-red-500">Failed</span>
                      ) : (
                        <span
                          className={`text-lg font-bold ${
                            batchResult.result.risk_score.overall_score >= 85
                              ? 'text-green-600'
                              : batchResult.result.risk_score.overall_score >= 70
                              ? 'text-yellow-600'
                              : batchResult.result.risk_score.overall_score >= 50
                              ? 'text-orange-600'
                              : 'text-red-600'
                          }`}
                        >
                          {batchResult.result.risk_score.overall_score}
                        </span>
                      )
                    ) : processing && i === currentIndex ? (
                      <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    ) : processing && i > currentIndex ? (
                      <span className="text-xs text-slate-400">Pending</span>
                    ) : null}

                    {!processing && (
                      <button
                        onClick={() => removeFile(i)}
                        className="text-slate-400 hover:text-red-500 cursor-pointer"
                      >
                        &times;
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Results summary */}
        {!processing && results.length > 0 && (
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">
              Batch Results
            </h2>
            <div className="grid grid-cols-3 gap-4 mb-4 text-center">
              <div className="p-3 rounded-lg bg-slate-50">
                <div className="text-2xl font-bold text-slate-800">
                  {results.filter((r) => r.result).length}
                </div>
                <div className="text-xs text-slate-500">Analyzed</div>
              </div>
              <div className="p-3 rounded-lg bg-red-50">
                <div className="text-2xl font-bold text-red-600">
                  {results.filter(
                    (r) => r.result && r.result.risk_score.overall_score < 50
                  ).length}
                </div>
                <div className="text-xs text-slate-500">Critical (F grade)</div>
              </div>
              <div className="p-3 rounded-lg bg-green-50">
                <div className="text-2xl font-bold text-green-600">
                  {results.filter(
                    (r) => r.result && r.result.risk_score.overall_score >= 85
                  ).length}
                </div>
                <div className="text-xs text-slate-500">Compliant (A grade)</div>
              </div>
            </div>

            <div className="space-y-2">
              {results
                .filter((r) => r.result)
                .sort(
                  (a, b) =>
                    a.result.risk_score.overall_score -
                    b.result.risk_score.overall_score
                )
                .map((r, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 rounded-lg border border-slate-100"
                  >
                    <div
                      className={`text-xl font-bold w-12 text-center ${
                        r.result.risk_score.overall_score >= 85
                          ? 'text-green-600'
                          : r.result.risk_score.overall_score >= 70
                          ? 'text-yellow-600'
                          : r.result.risk_score.overall_score >= 50
                          ? 'text-orange-600'
                          : 'text-red-600'
                      }`}
                    >
                      {r.result.risk_score.overall_score}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-700">
                        {r.result.label_data.product_name || r.fileName}
                      </p>
                      <p className="text-xs text-slate-400">
                        {r.result.findings.filter((f) => f.severity === 'CRITICAL')
                          .length}{' '}
                        critical,{' '}
                        {r.result.findings.filter((f) => f.severity === 'WARNING')
                          .length}{' '}
                        warnings
                      </p>
                    </div>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                        r.result.risk_score.grade === 'A'
                          ? 'bg-green-100 text-green-700'
                          : r.result.risk_score.grade === 'B'
                          ? 'bg-yellow-100 text-yellow-700'
                          : r.result.risk_score.grade === 'C'
                          ? 'bg-orange-100 text-orange-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      Grade {r.result.risk_score.grade}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
