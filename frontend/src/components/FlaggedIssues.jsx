import { useState } from 'react';

const SEVERITY_ORDER = { CRITICAL: 0, WARNING: 1, INFO: 2 };

const severityStyle = {
  CRITICAL: 'bg-red-100 text-red-700 border-red-200',
  WARNING: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  INFO: 'bg-blue-100 text-blue-700 border-blue-200',
};

const filterStyle = {
  all: 'bg-slate-800 text-white',
  CRITICAL: 'bg-red-600 text-white',
  WARNING: 'bg-yellow-500 text-white',
  INFO: 'bg-blue-500 text-white',
};

export default function FlaggedIssues({ findings }) {
  const [filter, setFilter] = useState('all');

  const sorted = [...findings].sort(
    (a, b) => (SEVERITY_ORDER[a.severity] ?? 3) - (SEVERITY_ORDER[b.severity] ?? 3)
  );

  const filtered = filter === 'all'
    ? sorted
    : sorted.filter((f) => f.severity === filter);

  const counts = {
    all: findings.length,
    CRITICAL: findings.filter((f) => f.severity === 'CRITICAL').length,
    WARNING: findings.filter((f) => f.severity === 'WARNING').length,
    INFO: findings.filter((f) => f.severity === 'INFO').length,
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-4">
        All Findings
      </h2>

      {/* Filter pills */}
      <div className="flex flex-wrap gap-2 mb-4">
        {['all', 'CRITICAL', 'WARNING', 'INFO'].map((key) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-colors cursor-pointer ${
              filter === key
                ? filterStyle[key]
                : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
            }`}
          >
            {key === 'all' ? 'All' : key.charAt(0) + key.slice(1).toLowerCase()}{' '}
            ({counts[key]})
          </button>
        ))}
      </div>

      {/* Findings list */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <p className="text-slate-400">
            No {filter === 'all' ? '' : filter.toLowerCase() + ' '}findings.
          </p>
        ) : (
          filtered.map((f, i) => (
            <div
              key={i}
              className={`p-4 rounded-lg border ${
                severityStyle[f.severity] || 'bg-slate-50 text-slate-700 border-slate-200'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase">{f.severity}</span>
                <span className="text-xs opacity-60">| {f.module}</span>
              </div>
              <p className="font-medium">{f.title}</p>
              <p className="text-sm mt-1 opacity-80">{f.description}</p>
              {f.regulation && (
                <p className="text-xs mt-2 opacity-60">Ref: {f.regulation}</p>
              )}
              {f.recommendation && (
                <p className="text-xs mt-1 italic opacity-70">
                  Fix: {f.recommendation}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
