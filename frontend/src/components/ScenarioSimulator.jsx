import { useState } from 'react';
import { runSimulation } from '../services/api';

export default function ScenarioSimulator({ labelData, originalScore }) {
  const [removedIngredients, setRemovedIngredients] = useState(new Set());
  const [removedAdditives, setRemovedAdditives] = useState(new Set());
  const [removedAllergens, setRemovedAllergens] = useState(new Set());
  const [addedAllergens, setAddedAllergens] = useState([]);
  const [removedClaims, setRemovedClaims] = useState(new Set());
  const [addedClaim, setAddedClaim] = useState('');
  const [license, setLicense] = useState(labelData.fssai_license || '');
  const [newAllergen, setNewAllergen] = useState('');

  const [simResult, setSimResult] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  const hasModifications =
    removedIngredients.size > 0 ||
    removedAdditives.size > 0 ||
    removedAllergens.size > 0 ||
    addedAllergens.length > 0 ||
    removedClaims.size > 0 ||
    license !== (labelData.fssai_license || '');

  async function handleRunSimulation() {
    setIsRunning(true);
    setError(null);
    try {
      const modifications = {};
      if (removedIngredients.size > 0)
        modifications.remove_ingredients = [...removedIngredients];
      if (removedAdditives.size > 0)
        modifications.remove_additives = [...removedAdditives];
      if (removedAllergens.size > 0)
        modifications.remove_allergen_declaration = [...removedAllergens];
      if (addedAllergens.length > 0)
        modifications.add_allergen_declaration = addedAllergens;
      if (removedClaims.size > 0) {
        // The API accepts single remove_claim, so we send the first one
        // For multiple removals, we'd need to extend the API
        // For now, handle via remove_ingredients pattern
        modifications.remove_claim = [...removedClaims][0];
      }
      if (license !== (labelData.fssai_license || ''))
        modifications.set_fssai_license = license;

      const result = await runSimulation(labelData, modifications);
      setSimResult(result);
    } catch (err) {
      console.error('Simulation failed:', err);
      setError('Simulation failed. Please try again.');
    } finally {
      setIsRunning(false);
    }
  }

  function handleReset() {
    setRemovedIngredients(new Set());
    setRemovedAdditives(new Set());
    setRemovedAllergens(new Set());
    setAddedAllergens([]);
    setRemovedClaims(new Set());
    setLicense(labelData.fssai_license || '');
    setNewAllergen('');
    setAddedClaim('');
    setSimResult(null);
    setError(null);
  }

  function toggleSet(set, setter, value) {
    const next = new Set(set);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    setter(next);
  }

  function getScoreColor(score) {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  }

  const delta = simResult
    ? simResult.risk_score.overall_score - originalScore.overall_score
    : 0;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800">
          What-If Simulator
        </h2>
        {hasModifications && (
          <button
            onClick={handleReset}
            className="text-xs text-slate-400 hover:text-slate-600 cursor-pointer"
          >
            Reset All
          </button>
        )}
      </div>
      <p className="text-sm text-slate-400 mb-6">
        Toggle ingredients, additives, allergens, or claims and re-run
        compliance checks to see how the score changes.
      </p>

      <div className="space-y-5">
        {/* Ingredients */}
        {labelData.ingredients.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-slate-600 mb-2">
              Ingredients
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {labelData.ingredients.map((ing, i) => {
                const removed = removedIngredients.has(ing);
                return (
                  <button
                    key={i}
                    onClick={() =>
                      toggleSet(removedIngredients, setRemovedIngredients, ing)
                    }
                    className={`px-2.5 py-1 rounded-full text-xs border transition-all cursor-pointer ${
                      removed
                        ? 'bg-red-50 border-red-300 text-red-500 line-through'
                        : 'bg-slate-50 border-slate-200 text-slate-700 hover:border-slate-300'
                    }`}
                  >
                    {ing}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Additives */}
        {labelData.additives && labelData.additives.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-slate-600 mb-2">
              Additives
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {labelData.additives.map((a, i) => {
                const removed = removedAdditives.has(a.name);
                return (
                  <button
                    key={i}
                    onClick={() =>
                      toggleSet(removedAdditives, setRemovedAdditives, a.name)
                    }
                    className={`px-2.5 py-1 rounded-full text-xs border transition-all cursor-pointer ${
                      removed
                        ? 'bg-red-50 border-red-300 text-red-500 line-through'
                        : 'bg-purple-50 border-purple-200 text-purple-700 hover:border-purple-300'
                    }`}
                  >
                    {a.name} {a.e_code ? `(${a.e_code})` : ''}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Allergen Declarations */}
        <div>
          <h3 className="text-sm font-medium text-slate-600 mb-2">
            Allergen Declarations
          </h3>
          <div className="flex flex-wrap gap-1.5 mb-2">
            {labelData.declared_allergens.map((a, i) => {
              const removed = removedAllergens.has(a);
              return (
                <button
                  key={i}
                  onClick={() =>
                    toggleSet(removedAllergens, setRemovedAllergens, a)
                  }
                  className={`px-2.5 py-1 rounded-full text-xs border transition-all cursor-pointer ${
                    removed
                      ? 'bg-red-50 border-red-300 text-red-500 line-through'
                      : 'bg-orange-50 border-orange-200 text-orange-700 hover:border-orange-300'
                  }`}
                >
                  {a}
                </button>
              );
            })}
            {addedAllergens.map((a, i) => (
              <button
                key={`added-${i}`}
                onClick={() =>
                  setAddedAllergens(addedAllergens.filter((x) => x !== a))
                }
                className="px-2.5 py-1 rounded-full text-xs border bg-green-50 border-green-300 text-green-700 cursor-pointer"
              >
                + {a}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={newAllergen}
              onChange={(e) => setNewAllergen(e.target.value)}
              placeholder="Add allergen declaration..."
              className="px-3 py-1.5 text-xs border border-slate-200 rounded-lg flex-1"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && newAllergen.trim()) {
                  setAddedAllergens([...addedAllergens, newAllergen.trim()]);
                  setNewAllergen('');
                }
              }}
            />
            <button
              onClick={() => {
                if (newAllergen.trim()) {
                  setAddedAllergens([...addedAllergens, newAllergen.trim()]);
                  setNewAllergen('');
                }
              }}
              className="px-3 py-1.5 text-xs bg-slate-100 border border-slate-200 rounded-lg hover:bg-slate-200 cursor-pointer"
            >
              Add
            </button>
          </div>
        </div>

        {/* Claims */}
        {labelData.nutritional_claims.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-slate-600 mb-2">Claims</h3>
            <div className="flex flex-wrap gap-1.5">
              {labelData.nutritional_claims.map((c, i) => {
                const removed = removedClaims.has(c);
                return (
                  <button
                    key={i}
                    onClick={() =>
                      toggleSet(removedClaims, setRemovedClaims, c)
                    }
                    className={`px-2.5 py-1 rounded-full text-xs border transition-all cursor-pointer ${
                      removed
                        ? 'bg-red-50 border-red-300 text-red-500 line-through'
                        : 'bg-teal-50 border-teal-200 text-teal-700 hover:border-teal-300'
                    }`}
                  >
                    {c}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* FSSAI License */}
        <div>
          <h3 className="text-sm font-medium text-slate-600 mb-2">
            FSSAI License
          </h3>
          <input
            type="text"
            value={license}
            onChange={(e) => setLicense(e.target.value)}
            placeholder="14-digit FSSAI license number"
            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg w-full max-w-xs"
          />
        </div>
      </div>

      {/* Run button */}
      <div className="mt-6 flex items-center gap-4">
        <button
          onClick={handleRunSimulation}
          disabled={!hasModifications || isRunning}
          className={`px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors cursor-pointer ${
            hasModifications && !isRunning
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
        >
          {isRunning ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
              Running...
            </span>
          ) : (
            'Run Simulation'
          )}
        </button>
        {!hasModifications && (
          <span className="text-xs text-slate-400">
            Toggle items above to enable simulation
          </span>
        )}
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-600">{error}</p>
      )}

      {/* Results comparison */}
      {simResult && (
        <div className="mt-6 pt-6 border-t border-slate-200">
          <h3 className="text-sm font-semibold text-slate-600 mb-4">
            Simulation Result
          </h3>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
            {/* Original */}
            <div className="text-center">
              <div className="text-xs text-slate-400 mb-1">Original</div>
              <div
                className={`text-4xl font-bold ${getScoreColor(
                  originalScore.overall_score
                )}`}
              >
                {originalScore.overall_score}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Grade {originalScore.grade}
              </div>
            </div>

            {/* Delta arrow */}
            <div className="text-center">
              <div
                className={`text-2xl font-bold ${
                  delta > 0
                    ? 'text-green-600'
                    : delta < 0
                    ? 'text-red-600'
                    : 'text-slate-400'
                }`}
              >
                {delta > 0 ? `+${delta}` : delta === 0 ? '0' : delta}
              </div>
              <div className="text-lg text-slate-300">
                {delta >= 0 ? '\u2192' : '\u2192'}
              </div>
            </div>

            {/* Simulated */}
            <div className="text-center">
              <div className="text-xs text-slate-400 mb-1">Simulated</div>
              <div
                className={`text-4xl font-bold ${getScoreColor(
                  simResult.risk_score.overall_score
                )}`}
              >
                {simResult.risk_score.overall_score}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Grade {simResult.risk_score.grade}
              </div>
            </div>
          </div>

          {/* Simulated findings summary */}
          <div className="mt-6 space-y-2">
            {simResult.findings
              .filter((f) => f.severity !== 'INFO')
              .map((f, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg border text-sm ${
                    f.severity === 'CRITICAL'
                      ? 'bg-red-50 border-red-200 text-red-700'
                      : 'bg-yellow-50 border-yellow-200 text-yellow-700'
                  }`}
                >
                  <span className="text-xs font-bold uppercase mr-2">
                    {f.severity}
                  </span>
                  {f.title}
                </div>
              ))}
            {simResult.findings.filter((f) => f.severity !== 'INFO').length ===
              0 && (
              <p className="text-green-600 text-sm flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                No issues in simulated scenario — full compliance!
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
