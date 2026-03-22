'use client'

import { useState } from 'react'

export default function DemoBanner() {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="relative max-w-lg w-full mx-4 bg-ops-card border border-signal-green/40 rounded-sm shadow-glow-green p-8">
        {/* Corner accents */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-signal-green/60" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-signal-green/60" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-signal-green/60" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-signal-green/60" />

        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <span className="w-2 h-2 rounded-full bg-signal-green animate-pulse-slow shadow-glow-green" />
          <span className="font-display text-[10px] tracking-[0.3em] text-ops-dim uppercase">
            System Notice
          </span>
        </div>

        <h2 className="font-display text-xl tracking-[0.15em] text-signal-green mb-3 uppercase leading-tight">
          Static Scanning Demo
        </h2>

        <p className="text-sm text-ops-text leading-relaxed mb-4">
          This is a <span className="text-signal-green font-display tracking-wider">demonstration</span> of
          Layer 1 — Automated Static API Discovery. The scanner detects and normalizes API definitions
          directly from your source repositories.
        </p>

        <div className="bg-ops-surface border border-ops-border rounded-sm p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-signal-amber text-[10px] font-display tracking-widest">REQUIREMENT</span>
          </div>
          <p className="text-xs text-ops-dim leading-relaxed mb-3">
            To discover endpoints, make sure your repository contains at least one of the following:
          </p>
          <div className="space-y-2">
            {[
              { file: 'api.yaml', note: 'recommended' },
              { file: 'openapi.json / openapi.yaml', note: '' },
              { file: 'swagger.json / swagger.yaml', note: '' },
              { file: '*.postman_collection.json', note: '' },
            ].map(({ file, note }) => (
              <div key={file} className="flex items-center gap-2">
                <span className="text-signal-green text-[10px]">▸</span>
                <span className="font-mono text-xs text-ops-text">{file}</span>
                {note && (
                  <span className="text-[9px] font-display tracking-widest text-signal-green/60 border border-signal-green/30 px-1.5 py-0.5 rounded-sm">
                    {note}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        <button
          onClick={() => setDismissed(true)}
          className="btn-primary w-full py-3 text-xs tracking-[0.2em] rounded-sm font-display"
        >
          ACKNOWLEDGE &amp; ENTER
        </button>
      </div>
    </div>
  )
}
