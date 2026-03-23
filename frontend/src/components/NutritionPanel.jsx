// ICMR/WHO Recommended Daily Values (per day, based on 2000 kcal diet)
const DAILY_VALUES = {
  energy_kcal: { label: 'Energy', unit: 'kcal', dv: 2000 },
  protein_g: { label: 'Protein', unit: 'g', dv: 60 },
  carbohydrates_g: { label: 'Carbohydrates', unit: 'g', dv: 300 },
  sugar_g: { label: 'Sugar', unit: 'g', dv: 50 },
  total_fat_g: { label: 'Total Fat', unit: 'g', dv: 67 },
  saturated_fat_g: { label: 'Saturated Fat', unit: 'g', dv: 22 },
  trans_fat_g: { label: 'Trans Fat', unit: 'g', dv: 2.2 },
  sodium_mg: { label: 'Sodium', unit: 'mg', dv: 2000 },
  fiber_g: { label: 'Fiber', unit: 'g', dv: 30 },
};

function getBarColor(pct) {
  if (pct > 80) return 'bg-red-500';
  if (pct > 50) return 'bg-yellow-500';
  return 'bg-green-500';
}

function getTextColor(pct) {
  if (pct > 80) return 'text-red-600';
  if (pct > 50) return 'text-yellow-600';
  return 'text-green-600';
}

export default function NutritionPanel({ nutritionalInfo }) {
  if (!nutritionalInfo) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          Nutritional Information
        </h2>
        <p className="text-slate-400">No nutritional data found on this label.</p>
      </div>
    );
  }

  const entries = Object.entries(DAILY_VALUES)
    .map(([key, meta]) => {
      const value = nutritionalInfo[key];
      if (value == null) return null;
      const pct = Math.round((value / meta.dv) * 100);
      return { key, value, pct, ...meta };
    })
    .filter(Boolean);

  if (entries.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          Nutritional Information
        </h2>
        <p className="text-slate-400">No nutritional values extracted.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800">
          Nutritional Information
        </h2>
        <span className="text-xs text-slate-400">per 100g | % Daily Value</span>
      </div>

      <div className="space-y-3">
        {entries.map((e) => (
          <div key={e.key} className="flex items-center gap-3">
            <div className="w-28 text-sm text-slate-600 shrink-0">{e.label}</div>
            <div className="flex-1">
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${getBarColor(e.pct)}`}
                  style={{ width: `${Math.min(e.pct, 100)}%` }}
                />
              </div>
            </div>
            <div className="w-24 text-right text-sm shrink-0">
              <span className="text-slate-700 font-medium">
                {e.value}
                {e.unit}
              </span>
            </div>
            <div className={`w-12 text-right text-sm font-semibold shrink-0 ${getTextColor(e.pct)}`}>
              {e.pct}%
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs text-slate-400 mt-4">
        % Daily Values based on ICMR/WHO recommended daily intake (2000 kcal diet).
      </p>
    </div>
  );
}
