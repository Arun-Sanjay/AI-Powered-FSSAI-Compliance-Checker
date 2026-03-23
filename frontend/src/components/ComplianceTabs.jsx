import { useState } from 'react';

const MODULES = [
  { key: 'additives', label: 'Additives' },
  { key: 'allergens', label: 'Allergens' },
  { key: 'claims', label: 'Claims' },
  { key: 'license', label: 'License' },
  { key: 'labelling', label: 'Labelling' },
];

const severityStyle = {
  CRITICAL: 'bg-red-100 text-red-700 border-red-200',
  WARNING: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  INFO: 'bg-blue-100 text-blue-700 border-blue-200',
};

function getBadgeStyle(findings) {
  if (findings.some((f) => f.severity === 'CRITICAL'))
    return 'bg-red-500 text-white';
  if (findings.some((f) => f.severity === 'WARNING'))
    return 'bg-yellow-500 text-white';
  return 'bg-slate-200 text-slate-600';
}

export default function ComplianceTabs({ findings, moduleScores }) {
  const [activeTab, setActiveTab] = useState('additives');

  const findingsByModule = {};
  for (const m of MODULES) {
    findingsByModule[m.key] = findings.filter((f) => f.module === m.key);
  }

  const activeFindings = findingsByModule[activeTab] || [];
  const activeScore = moduleScores.find((m) => m.module === activeTab);

  return (
    <div className="bg-white rounded-xl border border-slate-200">
      {/* Tab bar */}
      <div className="flex border-b border-slate-200 overflow-x-auto">
        {MODULES.map((m) => {
          const modFindings = findingsByModule[m.key];
          const issueCount = modFindings.filter(
            (f) => f.severity !== 'INFO'
          ).length;
          const isActive = activeTab === m.key;

          return (
            <button
              key={m.key}
              onClick={() => setActiveTab(m.key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors cursor-pointer ${
                isActive
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {m.label}
              {issueCount > 0 && (
                <span
                  className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${getBadgeStyle(
                    modFindings
                  )}`}
                >
                  {issueCount}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <div className="p-6">
        {activeScore && (
          <div className="flex items-center gap-3 mb-4">
            <span
              className={`text-2xl font-bold ${
                activeScore.score >= 85
                  ? 'text-green-600'
                  : activeScore.score >= 70
                  ? 'text-yellow-600'
                  : activeScore.score >= 50
                  ? 'text-orange-600'
                  : 'text-red-600'
              }`}
            >
              {activeScore.score}/100
            </span>
            <span className="text-sm text-slate-400">
              {activeScore.critical_count} critical, {activeScore.warning_count}{' '}
              warnings
            </span>
          </div>
        )}

        <div className="space-y-3">
          {activeFindings.length === 0 ? (
            <div className="flex items-center gap-2 text-green-600">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span>No issues found in this module.</span>
            </div>
          ) : (
            activeFindings.map((f, i) => (
              <div
                key={i}
                className={`p-4 rounded-lg border ${
                  severityStyle[f.severity] || 'bg-slate-50 text-slate-700 border-slate-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold uppercase">{f.severity}</span>
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
    </div>
  );
}
