import React from 'react';

const steps = [
  'Parsing documents...',
  'Extracting skills with NLP...',
  'Computing semantic similarity...',
  'Identifying skill gaps...',
  'Building course graph...',
  'Generating adaptive pathway...',
];

export default function LoadingState() {
  const [stepIdx, setStepIdx] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setStepIdx((prev) => (prev + 1) % steps.length);
    }, 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center py-20">
      {/* Animated rings */}
      <div className="relative w-20 h-20 mb-8">
        <div className="absolute inset-0 rounded-full border-2 border-brand-500/20 animate-ping" />
        <div className="absolute inset-2 rounded-full border-2 border-brand-400/30 animate-pulse" />
        <div className="absolute inset-4 rounded-full border-2 border-brand-300/40 animate-pulse-slow" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-6 h-6 rounded-full bg-brand-500 animate-pulse" />
        </div>
      </div>

      <p className="font-display font-semibold text-surface-100 text-lg mb-2">Analysing...</p>
      <p className="font-mono text-sm text-brand-300 animate-pulse">{steps[stepIdx]}</p>
    </div>
  );
}
