'use client'

import { useState } from 'react'
import MethodBadge from './MethodBadge'
import StatusBadge, { deriveStatus, Status } from './StatusBadge'

export interface Endpoint {
  id: number
  endpoint_path: string
  http_method: string
  source_file: string
  is_deprecated: boolean
}

type Filter = 'ALL' | Status

interface EndpointsTableProps {
  endpoints: Endpoint[]
  loading: boolean
}

export default function EndpointsTable({ endpoints, loading }: EndpointsTableProps) {
  const [filter, setFilter] = useState<Filter>('ALL')

  const counts = {
    ALL:    endpoints.length,
    ACTIVE: endpoints.filter(e => !e.is_deprecated).length,
    ZOMBIE: endpoints.filter(e => e.is_deprecated).length,
    SHADOW: 0,
  }

  const filtered = filter === 'ALL'
    ? endpoints
    : endpoints.filter(e => deriveStatus(e.is_deprecated) === filter)

  const FILTERS: { key: Filter; label: string; activeClass: string }[] = [
    { key: 'ALL',    label: 'ALL',    activeClass: 'border-ops-text text-ops-text' },
    { key: 'ACTIVE', label: 'ACTIVE', activeClass: 'border-signal-green text-signal-green' },
    { key: 'ZOMBIE', label: 'ZOMBIE', activeClass: 'border-signal-red text-signal-red' },
    { key: 'SHADOW', label: 'SHADOW', activeClass: 'border-signal-amber text-signal-amber' },
  ]

  return (
    <div className="flex flex-col gap-4">
      {/* Filter tabs + count */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1">
          {FILTERS.map(f => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-3 py-1.5 text-[10px] tracking-widest font-display border rounded-sm transition-all duration-150
                ${filter === f.key
                  ? `${f.activeClass} bg-white/5`
                  : 'border-ops-border text-ops-dim hover:border-ops-border-bright hover:text-ops-text'
                }`}
            >
              {f.label}
              <span className="ml-1.5 opacity-60">{counts[f.key]}</span>
            </button>
          ))}
        </div>
        <span className="text-[10px] tracking-widest text-ops-dim font-display">
          {filtered.length} RECORD{filtered.length !== 1 ? 'S' : ''}
        </span>
      </div>

      {/* Table */}
      <div className="relative border border-ops-border rounded-sm overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-[80px_1fr_180px_100px_90px] gap-0 border-b border-ops-border bg-ops-surface">
          {['METHOD', 'ENDPOINT PATH', 'SOURCE FILE', 'STATUS', 'ACTION'].map(h => (
            <div key={h} className="px-4 py-2.5 text-[9px] tracking-[0.2em] text-ops-dim font-display uppercase border-r border-ops-border last:border-r-0">
              {h}
            </div>
          ))}
        </div>

        {/* Body */}
        <div className="divide-y divide-ops-border/50">
          {loading && (
            <div className="flex items-center justify-center gap-3 py-16 text-ops-dim text-xs">
              <span className="spinner w-4 h-4" />
              <span className="font-display tracking-widest">FETCHING INTELLIGENCE...</span>
            </div>
          )}

          {!loading && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 gap-2 text-ops-dim">
              <svg className="w-8 h-8 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-[10px] tracking-widest font-display">NO RECORDS FOUND</span>
            </div>
          )}

          {!loading && filtered.map((ep, i) => {
            const status = deriveStatus(ep.is_deprecated)
            return (
              <div
                key={ep.id}
                className="row-animate grid grid-cols-[80px_1fr_180px_100px_90px] gap-0 hover:bg-white/[0.02] transition-colors group"
                style={{ animationDelay: `${Math.min(i * 30, 300)}ms` }}
              >
                {/* Method */}
                <div className="px-4 py-3 flex items-center border-r border-ops-border/50">
                  <MethodBadge method={ep.http_method} />
                </div>

                {/* Path */}
                <div className="px-4 py-3 flex items-center border-r border-ops-border/50 overflow-hidden">
                  <span className="text-xs text-ops-text truncate group-hover:text-signal-green transition-colors">
                    {ep.endpoint_path}
                  </span>
                </div>

                {/* Source */}
                <div className="px-4 py-3 flex items-center border-r border-ops-border/50 overflow-hidden">
                  <span className="text-[11px] text-ops-dim truncate font-mono">
                    {ep.source_file}
                  </span>
                </div>

                {/* Status */}
                <div className="px-4 py-3 flex items-center border-r border-ops-border/50">
                  <StatusBadge status={status} />
                </div>

                {/* Action */}
                <div className="px-4 py-3 flex items-center">
                  <button className="btn-decom px-2 py-1 rounded-sm" disabled title="Webhook decommission — coming in Layer 3">
                    DECOM
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
