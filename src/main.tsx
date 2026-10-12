import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { PrakriyaViewer } from './components/PrakriyaViewer';
import { initialProjects } from './data/initialProjects';
import { ProjectAudit } from './types/audit';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'prakriya' | 'audit'>('prakriya');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-amber-500/20 selection:text-amber-300">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.6)]" />
            <h1 className="text-base font-bold tracking-tight text-white font-mono">
              Project Audit Ecosystem
            </h1>
          </div>

          <nav className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-lg border border-slate-700/60">
            <button
              onClick={() => setActiveTab('prakriya')}
              className={`px-3.5 py-1.5 rounded-md text-xs font-mono font-medium transition-colors ${
                activeTab === 'prakriya'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Morphological Prakriyā
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-3.5 py-1.5 rounded-md text-xs font-mono font-medium transition-colors ${
                activeTab === 'audit'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Research Audit Cards ({initialProjects.length})
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content View */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {activeTab === 'prakriya' ? (
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-bold tracking-tight text-white">
                Pāṇinian Morphological Derivation Inspector
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                Authoritative sūtra provenance and step-by-step phonological transformations across classical gaṇas.
              </p>
            </div>
            <PrakriyaViewer />
          </div>
        ) : (
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-bold tracking-tight text-white">
                Research Project Inventory
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                Audit specification cards for active and proposed research projects.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {initialProjects.map((project: ProjectAudit) => (
                <div
                  key={project.id}
                  className="bg-slate-900 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
                      <span>{project.id}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {project.category || 'Research'}
                      </span>
                    </div>
                    <h3 className="text-base font-semibold text-slate-200 mb-2">
                      {project.title}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-3">
                      {project.description}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono text-slate-500">
                    <span>Status: {project.status || 'Spec Only'}</span>
                    <span>v{project.version || '1.0'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);