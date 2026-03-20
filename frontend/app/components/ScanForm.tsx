'use client'

import { useState } from 'react'

interface ScanFormProps {
  onScanComplete: () => void
}

export default function ScanForm({ onScanComplete }: ScanFormProps) {
  const [repoUrl, setRepoUrl] = useState('')
  const [token, setToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<{ count: number } | null>(null)

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setLastResult(null)

    try {
      const res = await fetch(`${apiBase}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, token }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail ?? `HTTP ${res.status}`)
      }

      const data = await res.json()
      setLastResult({ count: data.endpoints_discovered })
      onScanComplete()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative bracket p-5 bg-ops-card border border-ops-border">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5">
        <div className="w-1 h-5 bg-signal-green shadow-glow-green" />
        <span className="font-display text-xs tracking-[0.2em] text-ops-dim uppercase">
          Initiate Scan
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-[10px] tracking-widest text-ops-dim mb-1.5 uppercase">
            Repository URL
          </label>
          <input
            type="url"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            placeholder="https://github.com/org/repo"
            required
            className="input-ops w-full px-3 py-2.5 text-sm rounded-sm"
          />
        </div>

        <div>
          <label className="block text-[10px] tracking-widest text-ops-dim mb-1.5 uppercase">
            Access Token
          </label>
          <input
            type="password"
            value={token}
            onChange={e => setToken(e.target.value)}
            placeholder="ghp_••••••••••••••••"
            required
            className="input-ops w-full px-3 py-2.5 text-sm rounded-sm"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full py-3 text-xs rounded-sm flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <span className="spinner w-3.5 h-3.5" />
              <span>SCANNING...</span>
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>INITIATE SCAN</span>
            </>
          )}
        </button>
      </form>

      {/* Feedback */}
      {error && (
        <div className="mt-3 px-3 py-2 bg-signal-red-dim border border-signal-red/30 rounded-sm text-signal-red text-xs animate-fade-in">
          <span className="font-display tracking-wider">ERR //</span> {error}
        </div>
      )}
      {lastResult && (
        <div className="mt-3 px-3 py-2 bg-signal-green-dim border border-signal-green/30 rounded-sm text-signal-green text-xs animate-fade-in">
          <span className="font-display tracking-wider">OK //</span>{' '}
          {lastResult.count} endpoint{lastResult.count !== 1 ? 's' : ''} discovered
        </div>
      )}
    </div>
  )
}
