import { useState } from 'react';
import { getHistory, deleteAnalysis, clearHistory } from '../services/storage';

const gradeColor = {
  A: 'bg-green-100 text-green-700',
  B: 'bg-yellow-100 text-yellow-700',
  C: 'bg-orange-100 text-orange-700',
  F: 'bg-red-100 text-red-700',
};

export default function HistoryPanel({ onSelect, onCompare }) {
  const [history, setHistory] = useState(getHistory);
  const [compareSelection, setCompareSelection] = useState([]);

  function handleDelete(id) {
    const updated = deleteAnalysis(id);
    setHistory(updated);
    setCompareSelection((prev) => prev.filter((s) => s.id !== id));
  }

  function handleClear() {
    clearHistory();
    setHistory([]);
    setCompareSelection([]);
  }

  function toggleCompare(entry) {
    setCompareSelection((prev) => {
      const exists = prev.find((s) => s.id === entry.id);
      if (exists) return prev.filter((s) => s.id !== entry.id);
      if (prev.length >= 2) return [prev[1], entry]; // replace oldest
      return [...prev, entry];
    });
  }

  if (history.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-2xl w-full text-center">
          <h1 className="text-2xl font-bold text-slate-800 mb-4">
            Analysis History
          </h1>
          <p className="text-slate-500 mb-6">
            No past analyses yet. Upload a food label to get started.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-slate-800">
            Analysis History
          </h1>
          <div className="flex items-center gap-2">
            {compareSelection.length === 2 && (
              <button
                onClick={() => onCompare(compareSelection[0], compareSelection[1])}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition cursor-pointer"
              >
                Compare Selected ({compareSelection.length}/2)
              </button>
            )}
            <button
              onClick={handleClear}
              className="px-3 py-2 text-sm text-red-500 hover:text-red-700 cursor-pointer"
            >
              Clear All
            </button>
          </div>
        </div>

        <div className="space-y-3">
          {history.map((entry) => {
            const isSelected = compareSelection.some((s) => s.id === entry.id);
            return (
              <div
                key={entry.id}
                className={`bg-white rounded-xl border p-4 flex items-center gap-4 transition-colors ${
                  isSelected ? 'border-blue-400 bg-blue-50/30' : 'border-slate-200'
                }`}
              >
                {/* Thumbnail */}
                {entry.image ? (
                  <img
                    src={entry.image}
                    alt={entry.productName}
                    className="w-14 h-14 object-cover rounded-lg border border-slate-200 shrink-0"
                  />
                ) : (
                  <div className="w-14 h-14 bg-slate-100 rounded-lg flex items-center justify-center shrink-0 text-2xl">
                    📷
                  </div>
                )}

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-slate-800 truncate">
                    {entry.productName}
                  </p>
                  <p className="text-sm text-slate-400 truncate">
                    {[entry.brand, entry.category].filter(Boolean).join(' — ')}
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {new Date(entry.timestamp).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                {/* Score */}
                <div className="text-center shrink-0">
                  <div
                    className={`text-xl font-bold ${
                      entry.score >= 85
                        ? 'text-green-600'
                        : entry.score >= 70
                        ? 'text-yellow-600'
                        : entry.score >= 50
                        ? 'text-orange-600'
                        : 'text-red-600'
                    }`}
                  >
                    {entry.score}
                  </div>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                      gradeColor[entry.grade] || 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {entry.grade}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-1 shrink-0">
                  <button
                    onClick={() => onSelect(entry)}
                    className="px-3 py-1 text-xs bg-slate-100 rounded-lg hover:bg-slate-200 cursor-pointer"
                  >
                    View
                  </button>
                  <button
                    onClick={() => toggleCompare(entry)}
                    className={`px-3 py-1 text-xs rounded-lg cursor-pointer ${
                      isSelected
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-slate-100 hover:bg-slate-200'
                    }`}
                  >
                    {isSelected ? 'Selected' : 'Compare'}
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="px-3 py-1 text-xs text-red-400 hover:text-red-600 cursor-pointer"
                  >
                    Delete
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
