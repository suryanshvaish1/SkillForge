import React, { useState, useCallback } from 'react';
import Header from './components/Header';
import FileUploader from './components/FileUploader';
import SkillsPanel from './components/SkillsPanel';
import GapPanel from './components/GapPanel';
import PathwayView from './components/PathwayView';
import ReasoningTrace from './components/ReasoningTrace';
import LoadingState from './components/LoadingState';
import { useAnalysis } from './hooks/useAnalysis';
import { Sparkles, AlertCircle, ArrowRight } from 'lucide-react';

export default function App() {
  const { loading, error, result, analyse, reset } = useAnalysis();
  const [resumeFile, setResumeFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [resumeText, setResumeText] = useState(null);
  const [jdText, setJdText] = useState(null);

  const hasInput = resumeFile || jdFile || resumeText || jdText;

  const handleSubmit = useCallback(async () => {
    if (!hasInput) return;
    try {
      await analyse({ resumeFile, jdFile, resumeText, jdText });
    } catch (err) {
      // error is already set in state
    }
  }, [resumeFile, jdFile, resumeText, jdText, hasInput, analyse]);

  const handleReset = useCallback(() => {
    reset();
    setResumeFile(null);
    setJdFile(null);
    setResumeText(null);
    setJdText(null);
  }, [reset]);

  return (
    <div className="min-h-screen">
      <Header onReset={handleReset} hasResult={!!result} />

      <main className="max-w-5xl mx-auto px-6 pt-24 pb-16">
        {/* Results view */}
        {result ? (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="font-display font-bold text-3xl text-surface-50">
                Your Personalised Learning Pathway
              </h2>
              <p className="text-surface-400 mt-2 text-sm">
                Tailored training roadmap based on your skill profile and target role
              </p>
            </div>

            <SkillsPanel
              resumeSkills={result.resume_skills}
              jdSkills={result.jd_skills}
            />

            <GapPanel
              gaps={result.skill_gaps}
              alreadyMet={result.summary?.skills_already_met}
            />

            <PathwayView
              pathway={result.pathway}
              summary={result.summary}
            />

            <ReasoningTrace trace={result.reasoning_trace} />
          </div>
        ) : loading ? (
          <LoadingState />
        ) : (
          /* Upload form */
          <div className="max-w-3xl mx-auto animate-fade-in">
            {/* Hero */}
            <div className="text-center mb-12 pt-8">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-600/10 border border-brand-500/20 mb-6">
                <Sparkles className="w-4 h-4 text-brand-400" />
                <span className="text-xs font-mono text-brand-300">AI-Powered Adaptive Learning</span>
              </div>
              <h2 className="font-display font-extrabold text-4xl md:text-5xl text-surface-50 leading-tight">
                Stop Wasting Time on<br />
                <span className="bg-gradient-to-r from-brand-400 to-purple-400 bg-clip-text text-transparent">
                  One-Size-Fits-All
                </span>{' '}
                Training
              </h2>
              <p className="text-surface-400 mt-4 max-w-lg mx-auto leading-relaxed">
                Upload your resume and target job description. Our engine identifies exact skill gaps
                and builds a personalised, phased learning pathway — so you only learn what you need.
              </p>
            </div>

            {/* Upload cards */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="glass-card p-6">
                <FileUploader
                  label="Resume / CV"
                  onFile={setResumeFile}
                  onText={setResumeText}
                  placeholder="Paste your resume text here..."
                />
              </div>
              <div className="glass-card p-6">
                <FileUploader
                  label="Job Description"
                  onFile={setJdFile}
                  onText={setJdText}
                  placeholder="Paste the target job description here..."
                />
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-accent-red/10 border border-accent-red/20 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-accent-red shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-accent-red">Analysis Failed</p>
                  <p className="text-xs text-surface-300 mt-1">{error}</p>
                </div>
              </div>
            )}

            {/* Submit */}
            <div className="flex justify-center">
              <button
                onClick={handleSubmit}
                disabled={!hasInput || loading}
                className="btn-primary text-base flex items-center gap-2 px-8 py-4"
              >
                Generate Learning Pathway
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>

            {/* Feature highlights */}
            <div className="grid grid-cols-3 gap-4 mt-16">
              {[
                { title: 'NLP Skill Parsing', desc: 'Extracts skills from any resume or JD format' },
                { title: 'Gap Analysis', desc: 'Semantic matching identifies exact proficiency gaps' },
                { title: 'Adaptive Pathing', desc: 'Graph-based algorithm builds your optimal route' },
              ].map((f) => (
                <div key={f.title} className="text-center p-4">
                  <h4 className="font-display font-semibold text-surface-200 text-sm">{f.title}</h4>
                  <p className="text-xs text-surface-500 mt-1">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-700/20 py-6">
        <p className="text-center text-xs font-mono text-surface-500">
          SkillForge Adaptive Learning Engine • Zero-Hallucination Grounded Recommendations
        </p>
      </footer>
    </div>
  );
}
