import { useEffect, useState } from 'react';

const RADIUS = 85;
const STROKE = 12;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function getColor(score) {
  if (score >= 85) return '#22c55e';
  if (score >= 70) return '#eab308';
  if (score >= 50) return '#f97316';
  return '#ef4444';
}

function getGradeBg(grade) {
  const map = {
    A: 'bg-green-100 text-green-700',
    B: 'bg-yellow-100 text-yellow-700',
    C: 'bg-orange-100 text-orange-700',
    F: 'bg-red-100 text-red-700',
  };
  return map[grade] || 'bg-slate-100 text-slate-700';
}

export default function ScoreGauge({ score, grade, summary }) {
  const [animatedOffset, setAnimatedOffset] = useState(CIRCUMFERENCE);
  const color = getColor(score);
  const targetOffset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;

  useEffect(() => {
    // Trigger animation after mount
    const timer = setTimeout(() => setAnimatedOffset(targetOffset), 50);
    return () => clearTimeout(timer);
  }, [targetOffset]);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-48 h-48">
        <svg viewBox="0 0 200 200" className="w-full h-full -rotate-90">
          {/* Background track */}
          <circle
            cx="100"
            cy="100"
            r={RADIUS}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={STROKE}
          />
          {/* Score arc */}
          <circle
            cx="100"
            cy="100"
            r={RADIUS}
            fill="none"
            stroke={color}
            strokeWidth={STROKE}
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={animatedOffset}
            className="transition-[stroke-dashoffset] duration-1000 ease-out"
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold" style={{ color }}>
            {score}
          </span>
          <span className="text-sm text-slate-400">/ 100</span>
        </div>
      </div>

      <span
        className={`inline-block px-4 py-1.5 rounded-full text-sm font-semibold ${getGradeBg(grade)}`}
      >
        Grade {grade}
      </span>

      <p className="text-slate-600 text-center text-sm max-w-xs">{summary}</p>
    </div>
  );
}
