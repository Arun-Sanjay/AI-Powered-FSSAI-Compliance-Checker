export default function AllergenTable({ findings }) {
  // Extract allergen findings only
  const allergenFindings = findings.filter((f) => f.module === 'allergens');

  if (allergenFindings.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          Allergen Cross-Reference
        </h2>
        <p className="text-slate-400">No allergen data detected on this label.</p>
      </div>
    );
  }

  // Parse findings to build cross-reference data
  const rows = allergenFindings
    .filter((f) => f.title.includes(':'))
    .map((f) => {
      const category = f.title.split(':').slice(1).join(':').trim();
      const isUndeclared = f.title.startsWith('Undeclared Allergen');
      const isDeclared = f.title.startsWith('Allergen Declared');
      const isDeclarationPresent = f.title.startsWith('Allergen Declaration Present');

      // Skip the generic "Allergen Declaration Present" info finding
      if (isDeclarationPresent) return null;

      return {
        category,
        detected: isUndeclared || isDeclared,
        declared: isDeclared,
        severity: f.severity,
        description: f.description,
      };
    })
    .filter(Boolean);

  if (rows.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">
          Allergen Cross-Reference
        </h2>
        <p className="text-slate-400">No specific allergens detected in ingredients.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-4">
        Allergen Cross-Reference
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-2 px-3 text-slate-500 font-medium">
                Allergen Category
              </th>
              <th className="text-center py-2 px-3 text-slate-500 font-medium">
                Detected in Ingredients
              </th>
              <th className="text-center py-2 px-3 text-slate-500 font-medium">
                Declared on Label
              </th>
              <th className="text-center py-2 px-3 text-slate-500 font-medium">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className={`border-b border-slate-100 ${
                  i % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'
                }`}
              >
                <td className="py-2.5 px-3 font-medium text-slate-700">
                  {row.category}
                </td>
                <td className="py-2.5 px-3 text-center">
                  {row.detected ? (
                    <span className="text-green-600 text-lg">&#10003;</span>
                  ) : (
                    <span className="text-slate-300">—</span>
                  )}
                </td>
                <td className="py-2.5 px-3 text-center">
                  {row.declared ? (
                    <span className="text-green-600 text-lg">&#10003;</span>
                  ) : (
                    <span className="text-red-500 text-lg font-bold">&#10007;</span>
                  )}
                </td>
                <td className="py-2.5 px-3 text-center">
                  {row.declared ? (
                    <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                      Compliant
                    </span>
                  ) : (
                    <span className="inline-block px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700">
                      UNDECLARED
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
