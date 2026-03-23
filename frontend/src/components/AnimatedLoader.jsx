import { useEffect, useState } from 'react';

const STEPS = [
  'Reading label with AI vision...',
  'Identifying additives & allergens...',
  'Checking FSSAI compliance rules...',
  'Calculating risk score...',
  'Generating report...',
];

export default function AnimatedLoader() {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center py-8">
      <div className="w-full max-w-xs space-y-0">
        {STEPS.map((step, i) => {
          const isCompleted = i < activeStep;
          const isActive = i === activeStep;
          const isFuture = i > activeStep;

          return (
            <div key={i} className="flex items-start gap-3">
              {/* Timeline */}
              <div className="flex flex-col items-center">
                {/* Dot */}
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
                    isCompleted
                      ? 'bg-green-500'
                      : isActive
                      ? 'bg-blue-500'
                      : 'bg-slate-200'
                  }`}
                >
                  {isCompleted ? (
                    <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : isActive ? (
                    <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <span className="w-2 h-2 bg-slate-400 rounded-full" />
                  )}
                </div>
                {/* Connecting line */}
                {i < STEPS.length - 1 && (
                  <div
                    className={`w-0.5 h-6 transition-colors duration-300 ${
                      isCompleted ? 'bg-green-300' : 'bg-slate-200'
                    }`}
                  />
                )}
              </div>

              {/* Label */}
              <p
                className={`text-sm pt-0.5 transition-all duration-300 ${
                  isCompleted
                    ? 'text-green-600'
                    : isActive
                    ? 'text-blue-600 font-medium'
                    : 'text-slate-400'
                }`}
              >
                {step}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
