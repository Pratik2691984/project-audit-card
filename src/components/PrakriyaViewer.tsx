import React, { useState } from 'react';
import { PrakriyaPayload, SutraType } from '../types/prakriya';

// Character diff renderer highlighting newly introduced or transformed phonemes
const DiffExpression: React.FC<{ prev: string; next: string }> = ({ prev, next }) => {
  if (!prev) {
    return <span className="font-mono text-emerald-300 font-semibold">{next}</span>;
  }

  // Find longest common prefix and suffix
  let start = 0;
  while (start < prev.length && start < next.length && prev[start] === next[start]) {
    start++;
  }

  let endPrev = prev.length - 1;
  let endNext = next.length - 1;
  while (endPrev >= start && endNext >= start && prev[endPrev] === next[endNext]) {
    endPrev--;
    endNext--;
  }

  const unchangedHead = next.slice(0, start);
  const changedBody = next.slice(start, endNext + 1);
  const unchangedTail = next.slice(endNext + 1);

  return (
    <span className="font-mono text-sm tracking-wide">
      <span className="text-slate-400">{unchangedHead}</span>
      {changedBody && (
        <span className="bg-amber-500/20 text-amber-300 font-bold px-1 py-0.5 rounded border border-amber-500/30">
          {changedBody}
        </span>
      )}
      <span className="text-slate-400">{unchangedTail}</span>
    </span>
  );
};

const STAGE_FAMILY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  dhātu_saṃjñā: { bg: 'bg-blue-950/40', text: 'text-blue-300', border: 'border-blue-800/40' },
  lakāra_vidhi: { bg: 'bg-indigo-950/40', text: 'text-indigo-300', border: 'border-indigo-800/40' },
  tiṅ_ādeśa: { bg: 'bg-purple-950/40', text: 'text-purple-300', border: 'border-purple-800/40' },
  vikaraṇa_vidhi: { bg: 'bg-emerald-950/40', text: 'text-emerald-300', border: 'border-emerald-800/40' },
  luk_elision: { bg: 'bg-rose-950/40', text: 'text-rose-300', border: 'border-rose-800/40' },
  ślu_elision: { bg: 'bg-rose-950/40', text: 'text-rose-300', border: 'border-rose-800/40' },
  dvitva: { bg: 'bg-cyan-950/40', text: 'text-cyan-300', border: 'border-cyan-800/40' },
  abhyāsa_kārya: { bg: 'bg-teal-950/40', text: 'text-teal-300', border: 'border-teal-800/40' },
  aṅga_guṇa: { bg: 'bg-amber-950/40', text: 'text-amber-300', border: 'border-amber-800/40' },
  laghūpadha_guṇa: { bg: 'bg-amber-950/40', text: 'text-amber-300', border: 'border-amber-800/40' },
  guṇa_pratiṣedha: { bg: 'bg-red-950/40', text: 'text-red-300', border: 'border-red-800/40' },
  mit_ac_antyat_parah: { bg: 'bg-orange-950/40', text: 'text-orange-300', border: 'border-orange-800/40' },
  hal_sandhi: { bg: 'bg-fuchsia-950/40', text: 'text-fuchsia-300', border: 'border-fuchsia-800/40' },
  padanirvṛtti: { bg: 'bg-emerald-900/50', text: 'text-emerald-200', border: 'border-emerald-700/60' },
};

const TYPE_BADGES: Record<SutraType, string> = {
  samjna: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  vidhi: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  niyama: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  adhikara: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  atidesha: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  paribhasa: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
};

// Preset library reflecting the 10-gaṇa test suite
const PRESET_PARADIGMS: Record<string, PrakriyaPayload> = {
  'bhū → bhavati (Class 1)': {
    root_left: 'bhū', root_right: 'tip', gana_name: 'Bhvādi', gana_number: 1, final_output: 'bhavati',
    steps: [
      { step_index: 0, rule_applied: { number: '1.3.1', name: 'bhūvādayo dhātavaḥ', type: 'samjna' }, left_operand: 'bhū', right_operand: '', output: 'bhū', metadata: { stage: 'dhātu_saṃjñā' } },
      { step_index: 1, rule_applied: { number: '3.2.123', name: 'vartamāne laṭ', type: 'vidhi' }, left_operand: 'bhū', right_operand: 'laṭ', output: 'bhū + laṭ', metadata: { stage: 'lakāra_vidhi' } },
      { step_index: 2, rule_applied: { number: '3.4.78', name: 'tiptasjhi...', type: 'vidhi' }, left_operand: 'bhū', right_operand: 'tip', output: 'bhū + tip', metadata: { stage: 'tiṅ_ādeśa' } },
      { step_index: 3, rule_applied: { number: '1.3.9', name: 'tasya lopaḥ', type: 'vidhi' }, left_operand: 'tip', right_operand: '', output: 'bhū + ti', metadata: { stage: 'it_lopa_tiṅ' } },
      { step_index: 4, rule_applied: { number: '3.1.68', name: 'kartari śap', type: 'vidhi' }, left_operand: 'bhū', right_operand: 'śap', output: 'bhū + śap + ti', metadata: { stage: 'vikaraṇa_vidhi' } },
      { step_index: 5, rule_applied: { number: '1.3.9', name: 'tasya lopaḥ', type: 'vidhi' }, left_operand: 'śap', right_operand: '', output: 'bhū + a + ti', metadata: { stage: 'it_lopa_vikaraṇa' } },
      { step_index: 6, rule_applied: { number: '7.3.84', name: 'sārvadhātukārdhadhātukayoḥ', type: 'vidhi' }, left_operand: 'bhū', right_operand: 'a', output: 'bho + a + ti', metadata: { stage: 'aṅga_guṇa' } },
      { step_index: 7, rule_applied: { number: '6.1.78', name: "eco'yavāyāvaḥ", type: 'vidhi' }, left_operand: 'bho', right_operand: 'a', output: 'bhava + ti', metadata: { stage: 'ac_sandhi' } },
      { step_index: 8, rule_applied: { number: 'varṇa-melana', name: 'saṃyoga / padanirvṛtti', type: 'vidhi' }, left_operand: 'bhava', right_operand: 'ti', output: 'bhavati', metadata: { stage: 'padanirvṛtti' } },
    ]
  },
  'ad → atti (Class 2)': {
    root_left: 'ad', root_right: 'tip', gana_name: 'Adādi', gana_number: 2, final_output: 'atti',
    steps: [
      { step_index: 0, rule_applied: { number: '3.1.68', name: 'kartari śap', type: 'vidhi' }, left_operand: 'ad', right_operand: 'śap', output: 'ad + śap + ti', metadata: { stage: 'vikaraṇa_vidhi' } },
      { step_index: 1, rule_applied: { number: '2.4.72', name: 'adiprabhṛtibhyaḥ śapaḥ', type: 'vidhi' }, left_operand: 'ad', right_operand: 'śap', output: 'ad + ∅ + ti', metadata: { stage: 'luk_elision' } },
      { step_index: 2, rule_applied: { number: '8.4.55', name: 'khari ca', type: 'vidhi' }, left_operand: 'ad', right_operand: 'ti', output: 'atti', metadata: { stage: 'hal_sandhi' } },
    ]
  },
  'hu → juhoti (Class 3)': {
    root_left: 'hu', root_right: 'tip', gana_name: 'Juhotyādi', gana_number: 3, final_output: 'juhoti',
    steps: [
      { step_index: 0, rule_applied: { number: '3.1.68', name: 'kartari śap', type: 'vidhi' }, left_operand: 'hu', right_operand: 'śap', output: 'hu + śap + ti', metadata: { stage: 'vikaraṇa_vidhi' } },
      { step_index: 1, rule_applied: { number: '2.4.75', name: 'juhotyādibhyaḥ śluḥ', type: 'vidhi' }, left_operand: 'hu', right_operand: 'śap', output: 'hu + ∅ + ti', metadata: { stage: 'ślu_elision' } },
      { step_index: 2, rule_applied: { number: '6.1.10', name: 'ślau', type: 'vidhi' }, left_operand: 'hu', right_operand: '', output: 'hu + hu + ti', metadata: { stage: 'dvitva' } },
      { step_index: 3, rule_applied: { number: '6.1.4', name: "pūrvo'bhyāsaḥ", type: 'samjna' }, left_operand: 'hu', right_operand: '', output: 'abhyāsa(hu) + hu', metadata: { stage: 'abhyāsa_kārya' } },
      { step_index: 4, rule_applied: { number: '7.4.62', name: 'kuhoścuḥ', type: 'vidhi' }, left_operand: 'hu', right_operand: '', output: 'jhu + hu + ti', metadata: { stage: 'abhyāsa_kārya' } },
      { step_index: 5, rule_applied: { number: '8.4.54', name: 'abhyāse carca', type: 'vidhi' }, left_operand: 'jhu', right_operand: '', output: 'ju + hu + ti', metadata: { stage: 'abhyāsa_kārya' } },
      { step_index: 6, rule_applied: { number: '7.3.84', name: 'sārvadhātukārdhadhātukayoḥ', type: 'vidhi' }, left_operand: 'juhu', right_operand: 'ti', output: 'juho + ti', metadata: { stage: 'aṅga_guṇa' } },
      { step_index: 7, rule_applied: { number: 'varṇa-melana', name: 'saṃyoga / padanirvṛtti', type: 'vidhi' }, left_operand: 'juho', right_operand: 'ti', output: 'juhoti', metadata: { stage: 'padanirvṛtti' } },
    ]
  },
  'rudh → ruṇaddhi (Class 7)': {
    root_left: 'rudh', root_right: 'tip', gana_name: 'Rudhādi', gana_number: 7, final_output: 'ruṇaddhi',
    steps: [
      { step_index: 0, rule_applied: { number: '3.1.78', name: 'rudhādibhyaḥ śnam', type: 'vidhi' }, left_operand: 'rudh', right_operand: 'śnam', output: 'rudh + śnam + ti', metadata: { stage: 'vikaraṇa_vidhi' } },
      { step_index: 1, rule_applied: { number: '1.3.9', name: 'tasya lopaḥ', type: 'vidhi' }, left_operand: 'śnam', right_operand: '', output: 'rudh + na + ti', metadata: { stage: 'it_lopa_vikaraṇa' } },
      { step_index: 2, rule_applied: { number: '1.1.47', name: "midaco'ntyāt paraḥ", type: 'paribhasa' }, left_operand: 'rudh', right_operand: 'na', output: 'runadh + ti', metadata: { stage: 'mit_ac_antyat_parah' } },
      { step_index: 3, rule_applied: { number: '8.4.1', name: 'raṣābhyāṃ no ṇaḥ samānapade', type: 'vidhi' }, left_operand: 'runadh', right_operand: '', output: 'ruṇadh + ti', metadata: { stage: 'hal_sandhi' } },
      { step_index: 4, rule_applied: { number: '8.2.40', name: "jhaṣastathordho'dhaḥ", type: 'vidhi' }, left_operand: 'ruṇadh', right_operand: 'ti', output: 'ruṇadh + dhi', metadata: { stage: 'hal_sandhi' } },
      { step_index: 5, rule_applied: { number: '8.4.53', name: 'jhalāṁ jaś jhaśi', type: 'vidhi' }, left_operand: 'ruṇadh + dhi', right_operand: '', output: 'ruṇaddhi', metadata: { stage: 'padanirvṛtti' } },
    ]
  },
  'cur → corayati (Class 10)': {
    root_left: 'cur', root_right: 'tip', gana_name: 'Curādi', gana_number: 10, final_output: 'corayati',
    steps: [
      { step_index: 0, rule_applied: { number: '3.1.25', name: 'satyāpapāśa... curādibhyo ṇic', type: 'vidhi' }, left_operand: 'cur', right_operand: 'ṇic', output: 'cur + ṇic + ti', metadata: { stage: 'vikaraṇa_vidhi' } },
      { step_index: 1, rule_applied: { number: '1.3.9', name: 'tasya lopaḥ', type: 'vidhi' }, left_operand: 'ṇic', right_operand: '', output: 'cur + i + ti', metadata: { stage: 'it_lopa_vikaraṇa' } },
      { step_index: 2, rule_applied: { number: '7.3.86', name: 'pugantalaghūpadhasya ca', type: 'vidhi' }, left_operand: 'cur', right_operand: 'i', output: 'cor + i + ti', metadata: { stage: 'laghūpadha_guṇa' } },
      { step_index: 3, rule_applied: { number: '3.1.68', name: 'kartari śap', type: 'vidhi' }, left_operand: 'cori', right_operand: 'śap', output: 'cor + i + śap + ti', metadata: { stage: 'vikaraṇa_vidhi' } },
      { step_index: 4, rule_applied: { number: '7.3.84', name: 'sārvadhātukārdhadhātukayoḥ', type: 'vidhi' }, left_operand: 'i', right_operand: 'a', output: 'cor + e + a + ti', metadata: { stage: 'aṅga_guṇa' } },
      { step_index: 5, rule_applied: { number: '6.1.78', name: "eco'yavāyāvaḥ", type: 'vidhi' }, left_operand: 'core', right_operand: 'a', output: 'coraya + ti', metadata: { stage: 'ac_sandhi' } },
      { step_index: 6, rule_applied: { number: 'varṇa-melana', name: 'saṃyoga / padanirvṛtti', type: 'vidhi' }, left_operand: 'coraya', right_operand: 'ti', output: 'corayati', metadata: { stage: 'padanirvṛtti' } },
    ]
  }
};

export const PrakriyaViewer: React.FC = () => {
  const [selectedKey, setSelectedKey] = useState<string>('bhū → bhavati (Class 1)');
  const [expandedSutra, setExpandedSutra] = useState<string | null>(null);

  const payload = PRESET_PARADIGMS[selectedKey];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-slate-100 shadow-2xl max-w-4xl mx-auto">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono font-semibold uppercase px-2.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Pāṇinian Morphological Provenance
            </span>
            <span className="text-xs font-mono text-slate-400">
              Gaṇa {payload.gana_number} · {payload.gana_name}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-2">
            <span className="text-2xl font-bold font-mono text-slate-200">{payload.root_left}</span>
            <span className="text-slate-600 text-lg">⟶</span>
            <span className="text-2xl font-bold font-mono text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-800/40">
              {payload.final_output}
            </span>
          </div>
        </div>

        <div>
          <label className="block text-[11px] uppercase tracking-wider text-slate-400 font-semibold mb-1">
            Derivation Paradigm
          </label>
          <select
            value={selectedKey}
            onChange={(e) => setSelectedKey(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm font-medium text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber-500/40"
          >
            {Object.keys(PRESET_PARADIGMS).map((key) => (
              <option key={key} value={key}>{key}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Step Sequence Timeline */}
      <div className="mt-8 relative pl-6 border-l-2 border-slate-800 space-y-4">
        {payload.steps.map((step, idx) => {
          const prevOutput = idx === 0 ? '' : payload.steps[idx - 1].output;
          const stageStyle = STAGE_FAMILY_COLORS[step.metadata?.stage || ''] || {
            bg: 'bg-slate-800/40',
            text: 'text-slate-300',
            border: 'border-slate-700/40',
          };
          const typeBadge = TYPE_BADGES[step.rule_applied.type] || 'bg-slate-700 text-slate-300 border-slate-600';
          const isExpanded = expandedSutra === `${step.step_index}-${step.rule_applied.number}`;

          return (
            <div key={step.step_index} className="relative group">
              {/* Timeline Node */}
              <div className="absolute -left-[31px] top-4 w-3 h-3 rounded-full bg-slate-700 border-2 border-slate-900 group-hover:bg-amber-400 transition-colors" />

              {/* Badge Card */}
              <div className={`rounded-xl border p-4 transition-all ${stageStyle.bg} ${stageStyle.border}`}>
                <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setExpandedSutra(isExpanded ? null : `${step.step_index}-${step.rule_applied.number}`)}
                      className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-slate-900 text-amber-300 border border-slate-700 hover:border-amber-400 transition-colors flex items-center gap-1.5"
                    >
                      <span>{step.rule_applied.number}</span>
                      <span className="text-[10px] text-slate-500">{isExpanded ? '▲' : '▼'}</span>
                    </button>
                    <span className="text-sm font-medium text-slate-200">
                      {step.rule_applied.name}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {step.metadata?.stage && (
                      <span className={`text-[11px] font-mono px-2 py-0.5 rounded border ${stageStyle.text} ${stageStyle.border} bg-slate-950/60`}>
                        {step.metadata.stage}
                      </span>
                    )}
                    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${typeBadge}`}>
                      {step.rule_applied.type}
                    </span>
                  </div>
                </div>

                {/* Sūtra Details Drawer */}
                {isExpanded && (
                  <div className="mb-3 p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs text-slate-300 font-mono">
                    <div className="text-amber-400 font-semibold mb-1">Aṣṭādhyāyī Sūtra {step.rule_applied.number}</div>
                    <div>{step.rule_applied.name}</div>
                    <div className="text-slate-500 text-[11px] mt-1">Classification: {step.rule_applied.type.toUpperCase()} · Provenance Verified</div>
                  </div>
                )}

                {/* Operand & Diff Transformation */}
                <div className="flex items-center justify-between bg-slate-950/70 border border-slate-800/80 px-4 py-2.5 rounded-lg">
                  <div className="text-xs font-mono text-slate-400">
                    <span className="text-slate-500 mr-2">Input:</span>
                    <span>{step.left_operand}{step.right_operand ? ` + ${step.right_operand}` : ''}</span>
                  </div>
                  <div className="text-slate-600 font-bold px-2">⟶</div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-slate-500">Output:</span>
                    <DiffExpression prev={prevOutput} next={step.output} />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};