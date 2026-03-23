import ScoreGauge from './ScoreGauge';

function getScoreColor(score) {
  if (score >= 85) return 'text-green-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 50) return 'text-orange-600';
  return 'text-red-600';
}

function CompareCell({ label, valueA, valueB, unit = '', higherIsBetter = true }) {
  const numA = parseFloat(valueA);
  const numB = parseFloat(valueB);
  const aIsNA = valueA == null || isNaN(numA);
  const bIsNA = valueB == null || isNaN(numB);

  let colorA = 'text-slate-700';
  let colorB = 'text-slate-700';

  if (!aIsNA && !bIsNA && numA !== numB) {
    if (higherIsBetter) {
      colorA = numA > numB ? 'text-green-600 font-semibold' : 'text-red-600';
      colorB = numB > numA ? 'text-green-600 font-semibold' : 'text-red-600';
    } else {
      colorA = numA < numB ? 'text-green-600 font-semibold' : 'text-red-600';
      colorB = numB < numA ? 'text-green-600 font-semibold' : 'text-red-600';
    }
  }

  return (
    <tr className="border-b border-slate-100">
      <td className="py-2 px-3 text-sm text-slate-500">{label}</td>
      <td className={`py-2 px-3 text-sm text-center ${colorA}`}>
        {aIsNA ? '—' : `${valueA}${unit}`}
      </td>
      <td className={`py-2 px-3 text-sm text-center ${colorB}`}>
        {bIsNA ? '—' : `${valueB}${unit}`}
      </td>
    </tr>
  );
}

export default function CompareView({ entryA, entryB, onBack }) {
  const a = entryA.result;
  const b = entryB.result;
  const niA = a.label_data.nutritional_info || {};
  const niB = b.label_data.nutritional_info || {};

  const aFindings = a.findings.filter((f) => f.severity !== 'INFO');
  const bFindings = b.findings.filter((f) => f.severity !== 'INFO');

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-slate-800">
            Product Comparison
          </h1>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition cursor-pointer"
          >
            Back to History
          </button>
        </div>

        {/* Score comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[a, b].map((result, i) => {
            const entry = i === 0 ? entryA : entryB;
            return (
              <div
                key={i}
                className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col items-center"
              >
                <div className="flex items-center gap-3 mb-4 w-full">
                  {entry.image && (
                    <img
                      src={entry.image}
                      alt={entry.productName}
                      className="w-12 h-12 object-cover rounded-lg border border-slate-200"
                    />
                  )}
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-800 truncate">
                      {entry.productName}
                    </p>
                    <p className="text-xs text-slate-400 truncate">
                      {entry.brand}
                    </p>
                  </div>
                </div>
                <ScoreGauge
                  score={result.risk_score.overall_score}
                  grade={result.risk_score.grade}
                  summary=""
                />
              </div>
            );
          })}
        </div>

        {/* Module scores comparison */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">
            Module Scores
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">
                    Module
                  </th>
                  <th className="text-center py-2 px-3 text-slate-500 font-medium">
                    {entryA.productName}
                  </th>
                  <th className="text-center py-2 px-3 text-slate-500 font-medium">
                    {entryB.productName}
                  </th>
                </tr>
              </thead>
              <tbody>
                {a.risk_score.modules.map((modA, i) => {
                  const modB = b.risk_score.modules[i];
                  return (
                    <tr key={modA.module} className="border-b border-slate-100">
                      <td className="py-2 px-3 text-slate-600 capitalize">
                        {modA.module}
                      </td>
                      <td
                        className={`py-2 px-3 text-center font-semibold ${getScoreColor(
                          modA.score
                        )}`}
                      >
                        {modA.score}
                      </td>
                      <td
                        className={`py-2 px-3 text-center font-semibold ${getScoreColor(
                          modB?.score ?? 0
                        )}`}
                      >
                        {modB?.score ?? '—'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Nutritional comparison */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">
            Nutritional Comparison
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">
                    Nutrient
                  </th>
                  <th className="text-center py-2 px-3 text-slate-500 font-medium">
                    {entryA.productName}
                  </th>
                  <th className="text-center py-2 px-3 text-slate-500 font-medium">
                    {entryB.productName}
                  </th>
                </tr>
              </thead>
              <tbody>
                <CompareCell label="Energy" valueA={niA.energy_kcal} valueB={niB.energy_kcal} unit=" kcal" higherIsBetter={false} />
                <CompareCell label="Protein" valueA={niA.protein_g} valueB={niB.protein_g} unit="g" higherIsBetter={true} />
                <CompareCell label="Carbohydrates" valueA={niA.carbohydrates_g} valueB={niB.carbohydrates_g} unit="g" higherIsBetter={false} />
                <CompareCell label="Sugar" valueA={niA.sugar_g} valueB={niB.sugar_g} unit="g" higherIsBetter={false} />
                <CompareCell label="Total Fat" valueA={niA.total_fat_g} valueB={niB.total_fat_g} unit="g" higherIsBetter={false} />
                <CompareCell label="Saturated Fat" valueA={niA.saturated_fat_g} valueB={niB.saturated_fat_g} unit="g" higherIsBetter={false} />
                <CompareCell label="Trans Fat" valueA={niA.trans_fat_g} valueB={niB.trans_fat_g} unit="g" higherIsBetter={false} />
                <CompareCell label="Sodium" valueA={niA.sodium_mg} valueB={niB.sodium_mg} unit=" mg" higherIsBetter={false} />
                <CompareCell label="Fiber" valueA={niA.fiber_g} valueB={niB.fiber_g} unit="g" higherIsBetter={true} />
              </tbody>
            </table>
          </div>
        </div>

        {/* Issues comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { entry: entryA, findings: aFindings },
            { entry: entryB, findings: bFindings },
          ].map(({ entry, findings }, i) => (
            <div
              key={i}
              className="bg-white rounded-xl border border-slate-200 p-6"
            >
              <h3 className="text-sm font-semibold text-slate-600 mb-3">
                {entry.productName} — {findings.length} issue
                {findings.length !== 1 ? 's' : ''}
              </h3>
              <div className="space-y-2">
                {findings.length === 0 ? (
                  <p className="text-green-600 text-sm">No issues found.</p>
                ) : (
                  findings.map((f, j) => (
                    <div
                      key={j}
                      className={`p-2 rounded-lg text-xs ${
                        f.severity === 'CRITICAL'
                          ? 'bg-red-50 text-red-700'
                          : 'bg-yellow-50 text-yellow-700'
                      }`}
                    >
                      <span className="font-bold mr-1">{f.severity}</span>
                      {f.title}
                    </div>
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
