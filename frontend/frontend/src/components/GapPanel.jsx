import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';

const priorityConfig = {
  critical: { class: 'badge-critical', label: 'CRITICAL', barColor: 'bg-accent-red' },
  high:     { class: 'badge-high',     label: 'HIGH',     barColor: 'bg-accent-amber' },
  medium:   { class: 'badge-medium',   label: 'MEDIUM',   barColor: 'bg-brand-500' },
  low:      { class: 'badge-low',      label: 'LOW',      barColor: 'bg-accent-green' },
};

function GapBar({ gap }) {
  const config = priorityConfig[gap.priority] || priorityConfig.medium;
  const pct = Math.round(gap.gap_score * 100);

  return (
    <div className="py-3 border-b border-surface-700/30 last:border-0">
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-surface-100">{gap.skill}</span>
          <span className={config.class}>{config.label}</span>
        </div>
        <span className="text-xs font-mono text-surface-400">
          {gap.current_level} → {gap.required_level}
        </span>
      </div>
      <div className="h-1.5 bg-surface-700/40 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${config.barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function GapPanel({ gaps, alreadyMet }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="glass-card p-6">
      <button
        className="w-full flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <h3 className="font-display font-semibold text-surface-50 text-lg flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-accent-amber" />
          Skill Gap Analysis
          <span className="text-sm font-mono text-surface-400 font-normal">({gaps.length} gaps)</span>
        </h3>
        {expanded ? <ChevronUp className="w-5 h-5 text-surface-400" /> : <ChevronDown className="w-5 h-5 text-surface-400" />}
      </button>

      {expanded && (
        <div className="mt-4 space-y-0">
          {gaps.map((g) => <GapBar key={g.skill} gap={g} />)}

          {alreadyMet && alreadyMet.length > 0 && (
            <div className="mt-4 pt-4 border-t border-surface-700/30">
              <h4 className="text-sm font-display font-medium text-accent-green flex items-center gap-1.5 mb-2">
                <CheckCircle2 className="w-4 h-4" /> Skills Already Met
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {alreadyMet.map((s) => (
                  <span key={s} className="badge-met">{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
