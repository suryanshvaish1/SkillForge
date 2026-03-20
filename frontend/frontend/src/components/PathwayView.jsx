import React, { useState } from 'react';
import { BookOpen, Clock, ChevronRight, GraduationCap, Layers, ArrowRight } from 'lucide-react';

const difficultyColors = {
  beginner: 'text-green-400 bg-green-500/10 border-green-500/20',
  intermediate: 'text-brand-300 bg-brand-500/10 border-brand-500/20',
  advanced: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
};

const phaseAccents = [
  { border: 'border-l-green-400', dot: 'bg-green-400', glow: 'shadow-green-500/20' },
  { border: 'border-l-brand-400', dot: 'bg-brand-400', glow: 'shadow-brand-500/20' },
  { border: 'border-l-purple-400', dot: 'bg-purple-400', glow: 'shadow-purple-500/20' },
  { border: 'border-l-amber-400', dot: 'bg-amber-400', glow: 'shadow-amber-500/20' },
];

function CourseCard({ course, index }) {
  const [open, setOpen] = useState(false);
  const diffColor = difficultyColors[course.difficulty] || difficultyColors.intermediate;

  return (
    <div
      className="glass-card-hover p-4 cursor-pointer"
      onClick={() => setOpen(!open)}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-[10px] text-surface-400 bg-surface-700/60 px-1.5 py-0.5 rounded">{course.id}</span>
            <span className={`badge text-[10px] ${diffColor}`}>{course.difficulty}</span>
          </div>
          <h5 className="font-display font-semibold text-surface-100 text-sm">{course.title}</h5>
        </div>
        <div className="flex items-center gap-1 text-xs text-surface-400 shrink-0">
          <Clock className="w-3 h-3" />
          <span>{course.duration_hours}h</span>
        </div>
      </div>

      {open && (
        <div className="mt-3 pt-3 border-t border-surface-700/30 space-y-2 animate-fade-in">
          <p className="text-xs text-surface-300 leading-relaxed">{course.description}</p>
          {course.reason && (
            <p className="text-xs text-brand-300/80 italic">
              <span className="font-semibold text-brand-400">Why: </span>{course.reason}
            </p>
          )}
          <div className="flex flex-wrap gap-1.5 pt-1">
            {course.skills_covered?.map((s) => (
              <span key={s} className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-700/50 text-surface-300">{s}</span>
            ))}
          </div>
          {course.prerequisites?.length > 0 && (
            <p className="text-[10px] text-surface-500">
              Prerequisites: {course.prerequisites.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function Phase({ phase, accent }) {
  return (
    <div className={`border-l-2 ${accent.border} pl-6 pb-8 relative`}>
      {/* Timeline dot */}
      <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full ${accent.dot} ring-4 ring-surface-950 ${accent.glow} shadow-lg`} />

      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-mono text-surface-400 uppercase tracking-wider">Phase {phase.phase_number}</span>
          <ArrowRight className="w-3 h-3 text-surface-500" />
          <span className="text-xs font-mono text-surface-400">{phase.total_hours}h total</span>
        </div>
        <h4 className="font-display font-bold text-surface-50 text-xl">{phase.phase_name}</h4>
        <p className="text-sm text-surface-400 mt-1">{phase.description}</p>
      </div>

      <div className="space-y-3">
        {phase.courses.map((c, i) => (
          <CourseCard key={c.id} course={c} index={i} />
        ))}
      </div>
    </div>
  );
}

export default function PathwayView({ pathway, summary }) {
  if (!pathway || pathway.length === 0) {
    return (
      <div className="glass-card p-8 text-center">
        <GraduationCap className="w-10 h-10 text-surface-500 mx-auto mb-3" />
        <p className="text-surface-400">No learning pathway needed — you already meet all requirements!</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary strip */}
      <div className="glass-card p-5">
        <h3 className="font-display font-semibold text-surface-50 text-lg flex items-center gap-2 mb-4">
          <Layers className="w-5 h-5 text-brand-400" />
          Your Learning Roadmap
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Courses', value: summary.total_courses, icon: BookOpen },
            { label: 'Hours', value: summary.total_hours, icon: Clock },
            { label: 'Weeks', value: `~${summary.estimated_weeks}`, icon: GraduationCap },
            { label: 'Phases', value: summary.phases, icon: Layers },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="text-center p-3 rounded-xl bg-surface-800/40">
              <Icon className="w-5 h-5 text-brand-400 mx-auto mb-1" />
              <p className="font-display font-bold text-2xl text-surface-50">{value}</p>
              <p className="text-xs text-surface-400 font-mono">{label}</p>
            </div>
          ))}
        </div>

        {summary.domain_coverage && Object.keys(summary.domain_coverage).length > 0 && (
          <div className="mt-4 pt-4 border-t border-surface-700/30">
            <p className="text-xs font-mono text-surface-400 mb-2">Domain Coverage</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(summary.domain_coverage).map(([domain, count]) => (
                <span key={domain} className="badge bg-surface-700/60 text-surface-300 border border-surface-600/30">
                  {domain}: {count}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Phased timeline */}
      <div className="pl-2">
        {pathway.map((phase, i) => (
          <Phase
            key={phase.phase_number}
            phase={phase}
            accent={phaseAccents[i % phaseAccents.length]}
          />
        ))}
        {/* End marker */}
        <div className="relative pl-6">
          <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-accent-green ring-4 ring-surface-950 shadow-lg shadow-green-500/20" />
          <p className="font-display font-bold text-accent-green">Role Ready</p>
        </div>
      </div>
    </div>
  );
}
