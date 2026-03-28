'use client'

import Link from 'next/link'
import { useState } from 'react'

function Step({ n, title, children }: { n: number; title: string; children: React.ReactNode }) {
  return (
    <div className="flex gap-5">
      <div className="flex flex-col items-center">
        <div className="w-8 h-8 rounded-sm border border-signal-green/40 bg-signal-green-dim flex items-center justify-center font-display text-xs text-signal-green flex-shrink-0">
          {String(n).padStart(2, '0')}
        </div>
        <div className="flex-1 w-px bg-ops-border mt-2" />
      </div>
      <div className="pb-10 flex-1">
        <h3 className="font-display text-sm tracking-[0.15em] text-ops-text mb-4 uppercase">{title}</h3>
        <div className="space-y-3 text-sm text-ops-dim leading-relaxed">{children}</div>
      </div>
    </div>
  )
}

function Terminal({ children }: { children: React.ReactNode }) {
  return (
    <div className="my-3 bg-ops-bg border border-ops-border rounded-sm overflow-hidden">
      <div className="flex items-center gap-1.5 px-3 py-2 border-b border-ops-border bg-ops-surface">
        <span className="w-2 h-2 rounded-full bg-signal-red/50" />
        <span className="w-2 h-2 rounded-full bg-signal-amber/50" />
        <span className="w-2 h-2 rounded-full bg-signal-green/50" />
      </div>
      <pre className="px-4 py-3 text-xs text-signal-green font-mono overflow-x-auto leading-relaxed">{children}</pre>
    </div>
  )
}

function CopyableToken({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <div className="flex items-center gap-2 my-2">
      <span className="text-[10px] tracking-widest text-ops-dim font-display w-20">{label}</span>
      <div className="flex-1 flex items-center gap-2 bg-ops-bg border border-ops-border rounded-sm px-3 py-1.5">
        <code className="flex-1 text-xs text-signal-green font-mono">{value}</code>
        <button
          onClick={() => { navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 1500) }}
          className="text-[9px] tracking-widest font-display text-ops-dim hover:text-signal-green transition-colors"
        >
          {copied ? 'COPIED' : 'COPY'}
        </button>
      </div>
    </div>
  )
}

function Callout({ type, children }: { type: 'info' | 'warn' | 'danger'; children: React.ReactNode }) {
  const cfg = {
    info:   { border: 'border-signal-blue/30',  bg: 'bg-signal-blue-dim',   icon: 'ℹ', color: 'text-signal-blue' },
    warn:   { border: 'border-signal-amber/30', bg: 'bg-signal-amber-dim',  icon: '⚠', color: 'text-signal-amber' },
    danger: { border: 'border-signal-red/30',   bg: 'bg-signal-red-dim',    icon: '✕', color: 'text-signal-red' },
  }[type]
  return (
    <div className={`flex gap-3 px-4 py-3 rounded-sm border ${cfg.border} ${cfg.bg} my-3`}>
      <span className={`text-sm ${cfg.color} flex-shrink-0`}>{cfg.icon}</span>
      <span className="text-xs leading-relaxed">{children}</span>
    </div>
  )
}

function ScopeTag({ label }: { label: string }) {
  return (
    <span className="inline-block px-2 py-0.5 text-[10px] font-mono bg-ops-surface border border-ops-border rounded-sm text-ops-text mr-1.5 mb-1">
      {label}
    </span>
  )
}

export default function GetStartedPage() {
  const [provider, setProvider] = useState<'github' | 'gitlab'>('github')

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-ops-border bg-ops-surface/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-screen-lg mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex flex-col hover:opacity-80 transition-opacity">
              <span className="font-display text-lg tracking-[0.25em] text-signal-green leading-none">deaddrop</span>
              <span className="text-[9px] tracking-[0.3em] text-ops-dim mt-0.5">NOTHING GETS THROUGH</span>
            </Link>
            <div className="h-8 w-px bg-ops-border" />
            <span className="text-[10px] tracking-widest text-ops-dim font-display">OPERATOR BRIEFING</span>
          </div>
          <Link
            href="/"
            className="flex items-center gap-2 text-[10px] tracking-widest font-display text-ops-dim hover:text-signal-green border border-ops-border hover:border-signal-green/40 px-3 py-1.5 rounded-sm transition-all"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            BACK TO DASHBOARD
          </Link>
        </div>
      </header>

      <main className="flex-1 max-w-screen-lg mx-auto w-full px-6 py-12">
        {/* Hero */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-7 bg-signal-green shadow-glow-green" />
            <h1 className="font-display text-2xl tracking-[0.2em] text-ops-text uppercase">Operator Briefing</h1>
          </div>
          <p className="text-sm text-ops-dim max-w-2xl leading-relaxed ml-4">
            deaddrop scans your code repositories for API specification files and maps every endpoint into a
            unified intelligence layer. This guide will get you operational in under five minutes.
          </p>
        </div>

        {/* What deaddrop Finds */}
        <div className="mb-10 p-5 bg-ops-card border border-ops-border rounded-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-1 h-5 bg-ops-border" />
            <h2 className="font-display text-xs tracking-[0.2em] text-ops-dim uppercase">What deaddrop Scans For</h2>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { file: 'openapi.json / openapi.yaml', desc: 'OpenAPI 3.x specs', color: 'border-signal-blue/30 text-signal-blue' },
              { file: 'swagger.json / swagger.yaml', desc: 'Swagger 2.x specs', color: 'border-signal-green/30 text-signal-green' },
              { file: '*.postman_collection.json',   desc: 'Postman Collections v2.1', color: 'border-signal-amber/30 text-signal-amber' },
            ].map(item => (
              <div key={item.file} className={`p-3 border rounded-sm ${item.color} bg-ops-bg`}>
                <div className={`font-mono text-xs mb-1 ${item.color.split(' ')[1]}`}>{item.file}</div>
                <div className="text-[10px] text-ops-dim">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Provider toggle */}
        <div className="flex items-center gap-1 mb-8">
          {(['github', 'gitlab'] as const).map(p => (
            <button
              key={p}
              onClick={() => setProvider(p)}
              className={`px-4 py-2 text-[10px] tracking-widest font-display border rounded-sm transition-all
                ${provider === p
                  ? 'border-signal-green text-signal-green bg-signal-green-dim'
                  : 'border-ops-border text-ops-dim hover:border-ops-border-bright'}`}
            >
              {p === 'github' ? '◎ GITHUB' : '◈ GITLAB'}
            </button>
          ))}
          <span className="ml-3 text-[10px] text-ops-dim font-display tracking-widest">
            — SELECT YOUR PROVIDER
          </span>
        </div>

        {/* Steps */}
        <div>
          {provider === 'github' ? (
            <>
              <Step n={1} title="Create a GitHub Personal Access Token">
                <p>deaddrop needs read access to your repository contents to walk the file tree and download spec files.</p>
                <ol className="list-none space-y-2 mt-3">
                  {[
                    <>Go to <strong className="text-ops-text">github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)</strong></>,
                    <>Click <strong className="text-ops-text">"Generate new token (classic)"</strong></>,
                    <>Set an expiry and add a note like <code className="text-signal-green text-xs">deaddrop-scanner</code></>,
                    <>Select the following scopes:</>,
                  ].map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-ops-faint mt-0.5">▸</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ol>
                <div className="mt-2 ml-4">
                  <p className="text-[10px] text-ops-dim mb-2 tracking-widest font-display">REQUIRED SCOPES:</p>
                  <ScopeTag label="repo" />
                  <p className="text-[10px] text-ops-dim mt-2">
                    For public repos only, you can use <ScopeTag label="public_repo" /> instead.
                  </p>
                </div>
                <Callout type="warn">
                  Copy the token immediately after generation — GitHub will not show it again.
                </Callout>
                <CopyableToken label="TOKEN URL" value="https://github.com/settings/tokens/new" />
              </Step>

              <Step n={2} title="Find Your Repository URL">
                <p>Use the HTTPS clone URL of your repository — the same URL you&apos;d use with <code className="text-signal-green text-xs">git clone</code>.</p>
                <Terminal>{`# Public repo
https://github.com/your-org/your-repo

# Private repo (same format — the token handles auth)
https://github.com/your-org/private-repo`}</Terminal>
                <Callout type="info">
                  Do not include <code className="text-signal-green text-xs">.git</code> at the end — both formats are accepted.
                </Callout>
              </Step>

              <Step n={3} title="Run Your First Scan">
                <p>Enter the repo URL and your token in the Scan panel on the dashboard, then click <strong className="text-ops-text">INITIATE SCAN</strong>.</p>
                <p>Alternatively, call the API directly:</p>
                <Terminal>{`curl -X POST http://localhost:8000/scan \\
  -H "Content-Type: application/json" \\
  -d '{
    "repo_url": "https://github.com/your-org/your-repo",
    "token": "ghp_xxxxxxxxxxxxxxxxxxxx"
  }'`}</Terminal>
                <p>deaddrop will walk the full file tree, find every matching spec file, parse all endpoints, and persist them to the database in a single operation.</p>
              </Step>
            </>
          ) : (
            <>
              <Step n={1} title="Create a GitLab Personal Access Token">
                <p>deaddrop needs read access to your repository to enumerate files and fetch their content.</p>
                <ol className="list-none space-y-2 mt-3">
                  {[
                    <>Go to <strong className="text-ops-text">gitlab.com → User Settings → Access Tokens</strong></>,
                    <>Click <strong className="text-ops-text">"Add new token"</strong></>,
                    <>Set a name like <code className="text-signal-green text-xs">deaddrop-scanner</code> and an expiry date</>,
                    <>Select the following scopes:</>,
                  ].map((item, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-ops-faint mt-0.5">▸</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ol>
                <div className="mt-2 ml-4">
                  <p className="text-[10px] text-ops-dim mb-2 tracking-widest font-display">REQUIRED SCOPES:</p>
                  <ScopeTag label="read_api" />
                  <ScopeTag label="read_repository" />
                </div>
                <Callout type="warn">
                  Copy the token immediately — GitLab will not show it again after you leave the page.
                </Callout>
                <CopyableToken label="TOKEN URL" value="https://gitlab.com/-/user_settings/personal_access_tokens" />
              </Step>

              <Step n={2} title="Find Your Repository URL">
                <p>Use the HTTPS URL shown on your project&apos;s main page under <strong className="text-ops-text">Clone → Clone with HTTPS</strong>.</p>
                <Terminal>{`# Public project
https://gitlab.com/your-group/your-project

# Private project (same format — token handles auth)
https://gitlab.com/your-group/subgroup/your-project`}</Terminal>
                <Callout type="info">
                  Nested group paths like <code className="text-signal-green text-xs">group/subgroup/repo</code> are fully supported.
                </Callout>
              </Step>

              <Step n={3} title="Run Your First Scan">
                <p>Enter the repo URL and your token in the Scan panel on the dashboard, then click <strong className="text-ops-text">INITIATE SCAN</strong>.</p>
                <p>Alternatively, call the API directly:</p>
                <Terminal>{`curl -X POST http://localhost:8000/scan \\
  -H "Content-Type: application/json" \\
  -d '{
    "repo_url": "https://gitlab.com/your-group/your-project",
    "token": "glpat-xxxxxxxxxxxxxxxxxxxx"
  }'`}</Terminal>
                <p>deaddrop paginates the GitLab tree API automatically — large monorepos with hundreds of files are handled without manual configuration.</p>
              </Step>
            </>
          )}

          {/* Shared final step */}
          <Step n={4} title="Interpret Your Results">
            <p>Once the scan completes, your endpoints appear in the dashboard table with the following status tags:</p>
            <div className="space-y-3 mt-3">
              {[
                {
                  color: 'bg-signal-green border-signal-green text-signal-green',
                  dot: 'bg-signal-green',
                  label: 'ACTIVE',
                  desc: 'Endpoint is present in the spec and not marked deprecated. It is a known, live API surface.'
                },
                {
                  color: 'bg-signal-red-dim border-signal-red text-signal-red',
                  dot: 'bg-signal-red',
                  label: 'ZOMBIE',
                  desc: 'Endpoint is marked deprecated: true in the OpenAPI spec. It should be reviewed for decommission.'
                },
                {
                  color: 'bg-signal-amber-dim border-signal-amber text-signal-amber',
                  dot: 'bg-signal-amber',
                  label: 'SHADOW',
                  desc: 'Endpoint detected at runtime but absent from any spec. Requires Layer 2 (traffic analysis) — not yet available.'
                },
              ].map(item => (
                <div key={item.label} className="flex items-start gap-3 p-3 bg-ops-bg border border-ops-border rounded-sm">
                  <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-sm text-[10px] tracking-widest font-display border flex-shrink-0 ${item.color} bg-opacity-10`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${item.dot}`} />
                    {item.label}
                  </span>
                  <p className="text-xs leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
            <Callout type="info">
              Re-scanning the same repository is safe — deaddrop replaces previous results for those source files rather than duplicating them.
            </Callout>
          </Step>
        </div>

        {/* CTA */}
        <div className="mt-4 p-6 bg-ops-card border border-signal-green/20 rounded-sm flex items-center justify-between">
          <div>
            <div className="font-display text-sm tracking-[0.15em] text-ops-text mb-1">READY TO SCAN?</div>
            <div className="text-xs text-ops-dim">Your token is set — head back to the dashboard and initiate your first scan.</div>
          </div>
          <Link
            href="/"
            className="btn-primary px-6 py-3 text-xs rounded-sm flex items-center gap-2"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
            OPEN DASHBOARD
          </Link>
        </div>
      </main>

      <footer className="border-t border-ops-border bg-ops-surface/40 py-3">
        <div className="max-w-screen-lg mx-auto px-6 flex items-center justify-between">
          <span className="text-[9px] tracking-[0.25em] text-ops-dim font-display">deaddrop PROTO // OPERATOR BRIEFING</span>
          <span className="text-[9px] tracking-[0.2em] text-ops-faint font-display">CLASSIFICATION: INTERNAL</span>
        </div>
      </footer>
    </div>
  )
}
