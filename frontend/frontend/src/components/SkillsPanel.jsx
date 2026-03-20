import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Zap, Target } from 'lucide-react';

const levelColors = {
  none: 'bg-surface-700 text-surface-400',
  beginner: 'bg-blue-500/15 text-blue-300 border border-blue-500/20',
  intermediate: 'bg-brand-500/15 text-brand-300 border border-brand-500/20',
  advanced: 'bg-purple-500/15 text-purple-300 border border-purple-500/20',
  expert: 'bg-amber-500/15 text-amber-300 border border-amber-500/20',
};

function SkillChip({ skill }) {
  return (
    <div className="group relative">
      <span className={`badge ${levelColors[skill.level] || levelColors.none}`}>
        {skill.name}
        <span className="ml-1.5 opacity-60 text-[10px]">{skill.level}</span>
      </span>
      {skill.context && (
        <div className="absolute bottom-full left-0 mb-2 w-64 p-3 glass-card text-xs text-surface-300
                        opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-20">
          <p className="italic">"{skill.context}"</p>
          {skill.years_experience && <p className="mt-1 text-brand-400">{skill.years_experience}+ years</p>}
        </div>
      )}
    </div>
  );
}

export default function SkillsPanel({ resumeSkills, jdSkills }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="glass-card p-6">
      <button
        className="w-full flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <h3 className="font-display font-semibold text-surface-50 text-lg flex items-center gap-2">
          <Zap className="w-5 h-5 text-brand-400" />
          Extracted Skills
        </h3>
        {expanded ? <ChevronUp className="w-5 h-5 text-surface-400" /> : <ChevronDown className="w-5 h-5 text-surface-400" />}
      </button>

      {expanded && (
        <div className="mt-5 grid md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 rounded-full bg-accent-green" />
              <h4 className="text-sm font-display font-medium text-surface-200">Your Skills ({resumeSkills.length})</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {resumeSkills.map((s) => <SkillChip key={s.name} skill={s} />)}
              {resumeSkills.length === 0 && <p className="text-xs text-surface-500">No skills detected</p>}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-4 h-4 text-accent-cyan" />
              <h4 className="text-sm font-display font-medium text-surface-200">Required Skills ({jdSkills.length})</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {jdSkills.map((s) => <SkillChip key={s.name} skill={s} />)}
              {jdSkills.length === 0 && <p className="text-xs text-surface-500">No requirements detected</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
