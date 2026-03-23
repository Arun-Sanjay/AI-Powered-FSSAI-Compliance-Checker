import { useState, useRef } from 'react';
import { useTheme } from './hooks/useTheme';
import UploadPage from './components/UploadPage';
import Dashboard from './components/Dashboard';
import HistoryPanel from './components/HistoryPanel';
import CompareView from './components/CompareView';
import BatchUpload from './components/BatchUpload';
import { saveAnalysis, compressImage } from './services/storage';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState(null);
  const [view, setView] = useState('upload'); // upload | dashboard | history | compare
  const [compareEntries, setCompareEntries] = useState([null, null]);
  const [historyImage, setHistoryImage] = useState(null);
  const uploadedFile = useRef(null);
  const { dark, toggle: toggleTheme } = useTheme();

  const handleResult = async (analysisResult) => {
    setResult(analysisResult);
    setView('dashboard');

    // Save to history with compressed thumbnail
    let thumb = null;
    if (uploadedFile.current) {
      try {
        thumb = await compressImage(uploadedFile.current);
      } catch {
        // ignore compression errors
      }
    }
    saveAnalysis(analysisResult, thumb);
  };

  const handleImageUrl = (url) => {
    setImageUrl(url);
  };

  const handleFileSelected = (file) => {
    uploadedFile.current = file;
  };

  const handleReset = () => {
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    setResult(null);
    setImageUrl(null);
    uploadedFile.current = null;
    setView('upload');
  };

  const handleHistorySelect = (entry) => {
    setResult(entry.result);
    setHistoryImage(entry.image);
    setImageUrl(null);
    setView('dashboard');
  };

  const handleCompare = (entryA, entryB) => {
    setCompareEntries([entryA, entryB]);
    setView('compare');
  };

  // Navigation bar (shown on all views)
  const nav = (
    <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 px-4 py-2 flex items-center gap-4">
      <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm">FSSAI Checker</span>
      <div className="flex gap-1 ml-auto">
        <button
          onClick={() => { handleReset(); }}
          className={`px-3 py-1.5 text-xs rounded-lg cursor-pointer transition-colors ${
            view === 'upload' ? 'bg-blue-100 text-blue-700' : 'text-slate-500 hover:bg-slate-100'
          }`}
        >
          Upload
        </button>
        <button
          onClick={() => setView('batch')}
          className={`px-3 py-1.5 text-xs rounded-lg cursor-pointer transition-colors ${
            view === 'batch' ? 'bg-blue-100 text-blue-700' : 'text-slate-500 hover:bg-slate-100'
          }`}
        >
          Batch
        </button>
        <button
          onClick={() => setView('history')}
          className={`px-3 py-1.5 text-xs rounded-lg cursor-pointer transition-colors ${
            view === 'history' ? 'bg-blue-100 text-blue-700' : 'text-slate-500 hover:bg-slate-100'
          }`}
        >
          History
        </button>
        <button
          onClick={toggleTheme}
          className="px-3 py-1.5 text-xs rounded-lg cursor-pointer text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
          title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {dark ? '☀️' : '🌙'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950">
      {nav}
      <div className="flex-1">
        {view === 'dashboard' && result && (
          <Dashboard
            result={result}
            imageUrl={imageUrl || historyImage}
            onReset={handleReset}
          />
        )}
        {view === 'history' && (
          <HistoryPanel
            onSelect={handleHistorySelect}
            onCompare={handleCompare}
          />
        )}
        {view === 'compare' && compareEntries[0] && compareEntries[1] && (
          <CompareView
            entryA={compareEntries[0]}
            entryB={compareEntries[1]}
            onBack={() => setView('history')}
          />
        )}
        {view === 'batch' && (
          <BatchUpload onResults={() => {}} />
        )}
        {view === 'upload' && (
          <UploadPage
            onResult={handleResult}
            onImageUrl={handleImageUrl}
            onFileSelected={handleFileSelected}
            loading={loading}
            setLoading={setLoading}
          />
        )}
      </div>
    </div>
  );
}

export default App;
