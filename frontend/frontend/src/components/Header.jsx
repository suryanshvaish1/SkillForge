import React from 'react';
import { Cpu } from 'lucide-react';

export default function Header({ onReset, hasResult }) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-surface-950/80 backdrop-blur-xl border-b border-surface-700/30">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3 cursor-pointer" onClick={onReset}>
          <div className="w-9 h-9 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
            <Cpu className="w-5 h-5 text-brand-400" />
          </div>
          <div>
            <h1 className="font-display font-bold text-lg leading-none text-surface-50">SkillForge</h1>
            <p className="text-[10px] font-mono text-surface-300/60 tracking-widest uppercase mt-0.5">Adaptive Learning Engine</p>
          </div>
        </div>

        {hasResult && (
          <button onClick={onReset} className="btn-secondary text-sm">
            New Analysis
          </button>
        )}
      </div>
    </header>
  );
}
