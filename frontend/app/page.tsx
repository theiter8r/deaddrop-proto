'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import ScanForm from './components/ScanForm'
import EndpointsTable, { Endpoint } from './components/EndpointsTable'
import DemoBanner from './components/DemoBanner'
import ApiMapModal from './components/ApiMapModal'

export default function DashboardPage() {
  const [endpoints, setEndpoints] = useState<Endpoint[]>([])
  const [tableLoading, setTableLoading] = useState(true)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [showMap, setShowMap] = useState(false)

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  const fetchEndpoints = useCallback(async () => {
    setTableLoading(true)
    try {
      const res = await fetch(`${apiBase}/endpoints`)
      if (!res.ok) throw new Error()
      const data: Endpoint[] = await res.json()
      setEndpoints(data)
    } catch {
      // keep existing list on refresh failure
    } finally {
      setTableLoading(false)
    }
  }, [apiBase])

  // Health check
  useEffect(() => {
    fetch(`${apiBase}/health`)
      .then(r => setApiOnline(r.ok))
      .catch(() => setApiOnline(false))
  }, [apiBase])

  // Initial load
  useEffect(() => { fetchEndpoints() }, [fetchEndpoints])

  const activeCt = endpoints.filter(e => !e.is_deprecated).length
  const zombieCt = endpoints.filter(e => e.is_deprecated).length

  return (
    <div className="min-h-screen flex flex-col">
      <DemoBanner />
      {/* ── Top bar ─────────────────────────────────────── */}
      <header className="border-b border-ops-border bg-ops-surface/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-screen-xl mx-auto px-6 py-3 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-4">
            <div className="flex flex-col">
              <span className="font-display text-lg tracking-[0.25em] text-signal-green leading-none">
                deaddrop
              </span>
              <span className="text-[9px] tracking-[0.3em] text-ops-dim mt-0.5">
                NOTHING GETS THROUGH
              </span>
            </div>
            <div className="h-8 w-px bg-ops-border" />
            <span className="text-[10px] tracking-widest text-ops-dim font-display">
              LAYER 4 // INTELLIGENCE DASHBOARD
            </span>
          </div>

          {/* Nav + status indicators */}
          <div className="flex items-center gap-5">
            <Link
              href="/get-started"
              className="text-[10px] tracking-widest font-display text-ops-dim hover:text-signal-green border border-ops-border hover:border-signal-green/40 px-3 py-1.5 rounded-sm transition-all"
            >
              GET STARTED
            </Link>
            <div className="flex items-center gap-2 text-[10px] tracking-widest">
              <span
                className={`w-2 h-2 rounded-full ${
                  apiOnline === null
                    ? 'bg-ops-dim'
                    : apiOnline
                    ? 'bg-signal-green shadow-glow-green animate-pulse-slow'
                    : 'bg-signal-red'
                }`}
              />
              <span className={apiOnline ? 'text-signal-green' : 'text-ops-dim'}>
                {apiOnline === null ? 'CONNECTING' : apiOnline ? 'BACKEND ONLINE' : 'BACKEND OFFLINE'}
              </span>
            </div>

            <div className="h-4 w-px bg-ops-border" />

            <div className="flex items-center gap-3 text-[10px] font-display tracking-widest">
              <span className="text-signal-green">{activeCt} ACTIVE</span>
              <span className="text-ops-border">·</span>
              <span className="text-signal-red">{zombieCt} ZOMBIE</span>
              <span className="text-ops-border">·</span>
              <span className="text-ops-dim">{endpoints.length} TOTAL</span>
            </div>
          </div>
        </div>
      </header>

      {/* ── Main layout ──────────────────────────────────── */}
      <main className="flex-1 max-w-screen-xl mx-auto w-full px-6 py-8">
        <div className="flex gap-6">

          {/* Left panel — scan form + legend */}
          <aside className="w-72 flex-shrink-0 flex flex-col gap-5">
            <ScanForm onScanComplete={fetchEndpoints} />

            {/* Legend */}
            <div className="p-5 bg-ops-card border border-ops-border rounded-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-1 h-5 bg-ops-border" />
                <span className="font-display text-xs tracking-[0.2em] text-ops-dim uppercase">Status Legend</span>
              </div>
              <div className="space-y-3">
                {[
                  { color: 'bg-signal-green', label: 'ACTIVE', desc: 'Live, non-deprecated endpoint' },
                  { color: 'bg-signal-red',   label: 'ZOMBIE', desc: 'Marked deprecated in spec' },
                  { color: 'bg-signal-amber', label: 'SHADOW', desc: 'Runtime-detected (Layer 2)' },
                ].map(item => (
                  <div key={item.label} className="flex items-start gap-2.5">
                    <span className={`mt-1 w-1.5 h-1.5 rounded-full flex-shrink-0 ${item.color}`} />
                    <div>
                      <div className="text-[10px] tracking-widest font-display text-ops-text">{item.label}</div>
                      <div className="text-[10px] text-ops-dim mt-0.5">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Supported formats */}
            <div className="p-5 bg-ops-card border border-ops-border rounded-sm">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-1 h-5 bg-ops-border" />
                <span className="font-display text-xs tracking-[0.2em] text-ops-dim uppercase">Detects</span>
              </div>
              <div className="space-y-1.5 text-[11px] text-ops-dim">
                {[
                  'swagger.json / swagger.yaml',
                  'openapi.json / openapi.yaml',
                  '*.postman_collection.json',
                ].map(f => (
                  <div key={f} className="flex items-center gap-2">
                    <span className="text-ops-faint">▸</span>
                    <span className="font-mono">{f}</span>
                  </div>
                ))}
              </div>
            </div>
          </aside>

          {/* Right panel — endpoints table */}
          <section className="flex-1 min-w-0">
            {/* Section header */}
            <div className="flex items-center gap-4 mb-5">
              <div className="flex items-center gap-3">
                <div className="w-1 h-6 bg-signal-green shadow-glow-green" />
                <h2 className="font-display text-sm tracking-[0.2em] text-ops-text uppercase">
                  Discovered Endpoints
                </h2>
              </div>
              <div className="flex-1 h-px bg-ops-border" />
              <button
                onClick={() => setShowMap(true)}
                className="flex items-center gap-2 text-[10px] tracking-widest font-display text-ops-dim hover:text-ops-text border border-ops-border hover:border-ops-border-bright px-3 py-1.5 rounded-sm transition-all"
              >
                <MapIcon />
                <span>MAP</span>
              </button>
              <button
                onClick={fetchEndpoints}
                disabled={tableLoading}
                className="flex items-center gap-2 text-[10px] tracking-widest font-display text-ops-dim hover:text-ops-text border border-ops-border hover:border-ops-border-bright px-3 py-1.5 rounded-sm transition-all disabled:opacity-40"
              >
                {tableLoading
                  ? <><span className="spinner w-3 h-3" /><span>REFRESHING</span></>
                  : <><RefreshIcon /><span>REFRESH</span></>
                }
              </button>
            </div>

            <EndpointsTable endpoints={endpoints} loading={tableLoading} />
          </section>
        </div>
      </main>

      {/* ── Footer ───────────────────────────────────────── */}
      <footer className="border-t border-ops-border bg-ops-surface/40 py-3">
        <div className="max-w-screen-xl mx-auto px-6 flex items-center justify-between">
          <span className="text-[9px] tracking-[0.25em] text-ops-dim font-display">
            deaddrop PROTO // LAYER 1 + LAYER 4
          </span>
          <span className="text-[9px] tracking-[0.2em] text-ops-faint font-display">
            CLASSIFICATION: INTERNAL
          </span>
        </div>
      </footer>
      {showMap && (
        <ApiMapModal endpoints={endpoints} onClose={() => setShowMap(false)} />
      )}
    </div>
  )
}

function MapIcon() {
  return (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  )
}

function RefreshIcon() {
  return (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  )
}
