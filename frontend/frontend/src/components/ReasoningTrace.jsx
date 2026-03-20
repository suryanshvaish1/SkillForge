import React, { useState } from 'react';
import { Brain, ChevronDown, ChevronUp, Code2 } from 'lucide-react';

export default function ReasoningTrace({ trace }) {
  const [expanded, setExpanded] = useState(false);

  if (!trace || trace.length === 0) return null;

  return (
    <div className="glass-card p-6">
      <button
        className="w-full flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <h3 className="font-display font-semibold text-surface-50 text-lg flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          Reasoning Trace
          <span className="text-sm font-mono text-surface-400 font-normal">({trace.length} steps)</span>
        </h3>
        {expanded ? <ChevronUp className="w-5 h-5 text-surface-400" /> : <ChevronDown className="w-5 h-5 text-surface-400" />}
      </button>

      {expanded && (
        <div className="mt-4 space-y-3">
          {trace.map((step, i) => (
            <div key={i} className="flex gap-4 relative">
              {/* Timeline line */}
              {i < trace.length - 1 && (
                <div className="absolute left-[15px] top-8 bottom-0 w-px bg-surface-700/50" />
              )}
              {/* Step number */}
              <div className="w-8 h-8 rounded-lg bg-purple-500/15 border border-purple-500/20 flex items-center justify-center shrink-0 relative z-10">
                <span className="text-xs font-mono text-purple-300">{step.step}</span>
              </div>
              {/* Content */}
              <div className="flex-1 pb-2">
                <h5 className="text-sm font-display font-semibold text-surface-100">{step.action}</h5>
                <p className="text-xs text-surface-400 mt-0.5">{step.detail}</p>
                {step.data && (
                  <details className="mt-2">
                    <summary className="text-[10px] font-mono text-surface-500 cursor-pointer hover:text-surface-300 flex items-center gap-1">
                      <Code2 className="w-3 h-3" /> View data
                    </summary>
                    <pre className="mt-1 p-2 rounded-lg bg-surface-900/60 text-[10px] font-mono text-surface-400 overflow-x-auto max-h-40">
                      {JSON.stringify(step.data, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
