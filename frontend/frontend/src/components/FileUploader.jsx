import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X, Type } from 'lucide-react';

export default function FileUploader({ label, accept, onFile, onText, placeholder }) {
  const [mode, setMode] = useState('file'); // 'file' | 'text'
  const [file, setFile] = useState(null);
  const [text, setText] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const handleFile = useCallback((f) => {
    if (!f) return;
    setFile(f);
    setText('');
    onFile?.(f);
    onText?.(null);
  }, [onFile, onText]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  }, [handleFile]);

  const handleTextChange = useCallback((val) => {
    setText(val);
    setFile(null);
    onText?.(val);
    onFile?.(null);
  }, [onFile, onText]);

  const clear = () => {
    setFile(null);
    setText('');
    onFile?.(null);
    onText?.(null);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="font-display font-semibold text-surface-100 text-sm">{label}</label>
        <div className="flex gap-1 bg-surface-800/60 rounded-lg p-0.5">
          <button
            onClick={() => setMode('file')}
            className={`px-3 py-1 text-xs font-mono rounded-md transition-all ${
              mode === 'file' ? 'bg-brand-600/30 text-brand-300' : 'text-surface-400 hover:text-surface-200'
            }`}
          >
            <Upload className="w-3 h-3 inline mr-1" />File
          </button>
          <button
            onClick={() => setMode('text')}
            className={`px-3 py-1 text-xs font-mono rounded-md transition-all ${
              mode === 'text' ? 'bg-brand-600/30 text-brand-300' : 'text-surface-400 hover:text-surface-200'
            }`}
          >
            <Type className="w-3 h-3 inline mr-1" />Paste
          </button>
        </div>
      </div>

      {mode === 'file' ? (
        <div
          className={`upload-zone ${dragActive ? 'active' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={accept || '.pdf,.docx,.doc,.txt'}
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          {file ? (
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-brand-400" />
              <div>
                <p className="text-sm font-medium text-surface-100">{file.name}</p>
                <p className="text-xs text-surface-400">{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button onClick={(e) => { e.stopPropagation(); clear(); }} className="ml-2 p-1 rounded-lg hover:bg-surface-700">
                <X className="w-4 h-4 text-surface-400" />
              </button>
            </div>
          ) : (
            <>
              <Upload className="w-8 h-8 text-surface-500 mb-2" />
              <p className="text-sm text-surface-400">Drop file here or <span className="text-brand-400 font-medium">browse</span></p>
              <p className="text-xs text-surface-500 mt-1">PDF, DOCX, or TXT</p>
            </>
          )}
        </div>
      ) : (
        <div className="relative">
          <textarea
            value={text}
            onChange={(e) => handleTextChange(e.target.value)}
            placeholder={placeholder || 'Paste content here...'}
            rows={6}
            className="w-full bg-surface-800/40 border border-surface-600/40 rounded-2xl p-4 text-sm text-surface-200
                       placeholder-surface-500 resize-none focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/20
                       transition-all font-body"
          />
          {text && (
            <button onClick={clear} className="absolute top-3 right-3 p-1 rounded-lg hover:bg-surface-700">
              <X className="w-4 h-4 text-surface-400" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
