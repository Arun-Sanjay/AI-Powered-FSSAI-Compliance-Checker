import ScoreGauge from './ScoreGauge';
import IngredientPanel from './IngredientPanel';
import ComplianceTabs from './ComplianceTabs';
import FlaggedIssues from './FlaggedIssues';
import AllergenTable from './AllergenTable';
import ScenarioSimulator from './ScenarioSimulator';
import ReportDownload from './ReportDownload';
import NutritionPanel from './NutritionPanel';

export default function Dashboard({ result, imageUrl, onReset }) {
  const { label_data, findings, risk_score, summary } = result;

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            {imageUrl && (
              <img
                src={imageUrl}
                alt="Uploaded label"
                className="w-16 h-16 sm:w-20 sm:h-20 object-cover rounded-lg border border-slate-200 shrink-0"
              />
            )}
            <div>
              <h1 className="text-2xl font-bold text-slate-800">
                {label_data.product_name || 'Analysis Results'}
              </h1>
              <p className="text-slate-500">
                {[label_data.brand, label_data.food_category]
                  .filter(Boolean)
                  .join(' — ')}
              </p>
              {label_data.detected_languages?.length > 0 && (
                <p className="text-xs text-slate-400 mt-0.5">
                  Languages: {label_data.detected_languages.join(', ')}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ReportDownload result={result} />
            <button
              onClick={onReset}
              className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 transition cursor-pointer shrink-0"
            >
              Scan Another Label
            </button>
          </div>
        </div>

        {/* Score Section — gauge + module cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Gauge */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 flex items-center justify-center">
            <ScoreGauge
              score={risk_score.overall_score}
              grade={risk_score.grade}
              summary={summary}
            />
          </div>

          {/* Module score cards */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
              Module Scores
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 gap-3">
              {risk_score.modules.map((m) => (
                <div
                  key={m.module}
                  className="rounded-lg border border-slate-100 p-3 text-center"
                >
                  <div
                    className={`text-2xl font-bold ${
                      m.score >= 85
                        ? 'text-green-600'
                        : m.score >= 70
                        ? 'text-yellow-600'
                        : m.score >= 50
                        ? 'text-orange-600'
                        : 'text-red-600'
                    }`}
                  >
                    {m.score}
                  </div>
                  <div className="text-xs text-slate-500 capitalize mt-1">
                    {m.module}
                  </div>
                  {/* Mini bar */}
                  <div className="mt-2 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        m.score >= 85
                          ? 'bg-green-500'
                          : m.score >= 70
                          ? 'bg-yellow-500'
                          : m.score >= 50
                          ? 'bg-orange-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${m.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Compliance Tabs */}
        <ComplianceTabs
          findings={findings}
          moduleScores={risk_score.modules}
        />

        {/* Ingredient Panel */}
        <IngredientPanel
          ingredients={label_data.ingredients}
          findings={findings}
          additives={label_data.additives || []}
        />

        {/* Nutritional Info */}
        <NutritionPanel nutritionalInfo={label_data.nutritional_info} />

        {/* Allergen Cross-Reference */}
        <AllergenTable findings={findings} />

        {/* All Findings (sorted + filterable) */}
        <FlaggedIssues findings={findings} />

        {/* What-If Simulator */}
        <ScenarioSimulator
          labelData={label_data}
          originalScore={risk_score}
        />

        {/* Footer */}
        <p className="text-center text-xs text-slate-400 pb-4">
          Food Label Analyzer | AI-Powered FSSAI Compliance Checker
        </p>
      </div>
    </div>
  );
}
