function getIngredientRisk(ingredientName, findings, additives) {
  const nameLower = ingredientName.toLowerCase();

  // Check if any CRITICAL finding mentions this ingredient
  const hasCritical = findings.some(
    (f) =>
      f.severity === 'CRITICAL' &&
      (f.description.toLowerCase().includes(nameLower) ||
        f.title.toLowerCase().includes(nameLower))
  );
  if (hasCritical) return 'critical';

  // Check if any WARNING finding mentions this ingredient
  const hasWarning = findings.some(
    (f) =>
      f.severity === 'WARNING' &&
      (f.description.toLowerCase().includes(nameLower) ||
        f.title.toLowerCase().includes(nameLower))
  );
  if (hasWarning) return 'warning';

  // Check if this ingredient is an additive (notable even if approved)
  const isAdditive = additives.some(
    (a) => a.name.toLowerCase() === nameLower
  );
  if (isAdditive) return 'warning';

  return 'safe';
}

const dotStyle = {
  critical: 'bg-red-500',
  warning: 'bg-yellow-500',
  safe: 'bg-green-500',
};

const dotLabel = {
  critical: 'Flagged — see compliance findings',
  warning: 'Notable — additive or has warnings',
  safe: 'No concerns',
};

export default function IngredientPanel({ ingredients, findings, additives }) {
  if (!ingredients || ingredients.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          Extracted Ingredients
        </h2>
        <p className="text-slate-400">No ingredients detected.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">
        Extracted Ingredients
      </h2>
      <div className="flex items-center gap-4 mb-4 text-xs text-slate-400">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green-500 inline-block" /> Safe
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-yellow-500 inline-block" /> Notable
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-500 inline-block" /> Flagged
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {ingredients.map((ing, i) => {
          const risk = getIngredientRisk(ing, findings, additives);
          return (
            <span
              key={i}
              title={dotLabel[risk]}
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm border ${
                risk === 'critical'
                  ? 'bg-red-50 border-red-200 text-red-800'
                  : risk === 'warning'
                  ? 'bg-yellow-50 border-yellow-200 text-yellow-800'
                  : 'bg-slate-50 border-slate-200 text-slate-700'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full shrink-0 ${dotStyle[risk]}`}
              />
              {ing}
            </span>
          );
        })}
      </div>
    </div>
  );
}
