# API Structure Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an API Structure Map modal to the dashboard that visualizes discovered endpoints as a collapsible path tree and a CSS treemap, toggled by a button in the endpoints section header.

**Architecture:** A single `ApiMapModal.tsx` component receives the already-loaded `endpoints` array from `page.tsx` — no new API calls. Two pure data-transform functions (`buildTree`, `buildGroups`) derive the visualization structures client-side. The modal mounts on top of the dashboard via a fixed overlay.

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Next.js 14 (static export). No new libraries.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| **Create** | `frontend/app/components/ApiMapModal.tsx` | Full modal: types, data transforms, tree view, treemap view, header, footer, Escape handler |
| **Modify** | `frontend/app/page.tsx` | Add `showMap` state, MAP button, conditional `<ApiMapModal>` render |

---

## Task 1: Data types and `buildTree`

**Files:**
- Create: `frontend/app/components/ApiMapModal.tsx`

- [ ] **Step 1: Create the file with types and `buildTree`**

Create `frontend/app/components/ApiMapModal.tsx` with the following content — just the types and tree-builder for now, no JSX yet:

```tsx
'use client'

import { useEffect, useMemo, useState } from 'react'
import MethodBadge from './MethodBadge'
import { Endpoint } from './EndpointsTable'

// ─── Types ────────────────────────────────────────────────────────────────────

interface TreeNode {
  key: string       // full path to this node, e.g. "/api/v1"
  segment: string   // just this node's label, e.g. "v1"
  depth: number     // root children are depth 1
  children: Map<string, TreeNode>
  endpoints: string[] // http_method values at this exact path
}

interface Group {
  key: string        // group path key, e.g. "/api/v1/users"
  count: number
  methods: string[]  // deduplicated
  sources: string[]  // deduplicated, up to 2 + overflow
  colorIndex: number
}

// ─── Data transforms ──────────────────────────────────────────────────────────

function buildTree(endpoints: Endpoint[]): TreeNode {
  const root: TreeNode = { key: '', segment: '', depth: 0, children: new Map(), endpoints: [] }

  for (const ep of endpoints) {
    const segments = ep.endpoint_path.split('/').filter(Boolean)
    let node = root
    let pathSoFar = ''

    for (let i = 0; i < segments.length; i++) {
      const seg = segments[i]
      pathSoFar += '/' + seg
      if (!node.children.has(seg)) {
        node.children.set(seg, {
          key: pathSoFar,
          segment: seg,
          depth: i + 1,        // root children are depth 1
          children: new Map(),
          endpoints: [],
        })
      }
      node = node.children.get(seg)!
    }
    // attach the HTTP method at the leaf path node
    node.endpoints.push(ep.http_method)
  }

  return root
}

function collectDeepKeys(node: TreeNode, acc: Set<string>) {
  for (const child of node.children.values()) {
    if (child.depth > 2) acc.add(child.key)
    collectDeepKeys(child, acc)
  }
}

function countEndpoints(node: TreeNode): number {
  let n = node.endpoints.length
  for (const child of node.children.values()) n += countEndpoints(child)
  return n
}

function buildGroups(endpoints: Endpoint[]): Group[] {
  const map = new Map<string, { methods: Set<string>; sources: Set<string>; count: number }>()

  for (const ep of endpoints) {
    const segs = ep.endpoint_path.split('/').filter(Boolean).slice(0, 3)
    const key = '/' + segs.join('/')
    if (!map.has(key)) map.set(key, { methods: new Set(), sources: new Set(), count: 0 })
    const g = map.get(key)!
    g.methods.add(ep.http_method)
    g.sources.add(ep.source_file)
    g.count++
  }

  const sorted = [...map.entries()].sort((a, b) => b[1].count - a[1].count)

  return sorted.map(([key, val], i) => {
    const srcArr = [...val.sources]
    const sources = srcArr.length > 2
      ? [...srcArr.slice(0, 2), `+${srcArr.length - 2} more`]
      : srcArr
    return { key, count: val.count, methods: [...val.methods], sources, colorIndex: i % 5 }
  })
}

// placeholder export so file is valid — replaced in later tasks
export default function ApiMapModal(_: { endpoints: Endpoint[]; onClose: () => void }) {
  return null
}
```

- [ ] **Step 2: Verify the file compiles**

```bash
cd /Users/raajpatkar/Code/Hackathons/DeadDrop-Proto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors (or only pre-existing unrelated errors).

- [ ] **Step 3: Commit**

```bash
git add frontend/app/components/ApiMapModal.tsx
git commit -m "feat: add buildTree and buildGroups data transforms for API map"
```

---

## Task 2: Tree View renderer

**Files:**
- Modify: `frontend/app/components/ApiMapModal.tsx`

- [ ] **Step 1: Add the `TreeNodeView` recursive component**

Replace the placeholder `export default` at the bottom of `ApiMapModal.tsx` with the following (keep everything above it):

```tsx
// ─── Tree view ────────────────────────────────────────────────────────────────

function TreeNodeView({
  node,
  collapsed,
  onToggle,
}: {
  node: TreeNode
  collapsed: Set<string>
  onToggle: (key: string) => void
}) {
  const isCollapsed = collapsed.has(node.key)
  const hasChildren = node.children.size > 0
  const childCount = countEndpoints(node)

  return (
    <div>
      {/* Internal node row */}
      {node.depth > 0 && (
        <div
          className="flex items-center gap-2 px-2 py-1 rounded-sm hover:bg-white/[0.03] cursor-pointer group"
          onClick={() => hasChildren && onToggle(node.key)}
        >
          <span className="text-ops-dim text-[10px] w-3 flex-shrink-0">
            {hasChildren ? (isCollapsed ? '▶' : '▼') : ''}
          </span>
          <span className="text-ops-text text-xs font-mono truncate max-w-xs group-hover:text-signal-green transition-colors">
            /{node.segment}
          </span>
          {hasChildren && (
            <span className="ml-auto text-[9px] font-display tracking-widest text-ops-dim bg-ops-surface border border-ops-border px-1.5 py-0.5 rounded-sm flex-shrink-0">
              {childCount}
            </span>
          )}
        </div>
      )}

      {/* Leaf method rows */}
      {node.endpoints.map((method, i) => (
        <div key={`${node.key}-${method}-${i}`} className="flex items-center gap-2 px-2 py-0.5 pl-7">
          <MethodBadge method={method} />
          <span className="text-[11px] text-ops-dim font-mono truncate max-w-xs">{node.key}</span>
        </div>
      ))}

      {/* Children */}
      {!isCollapsed && hasChildren && (
        <div className="ml-3 border-l border-ops-border/40 pl-2">
          {[...node.children.values()].map(child => (
            <TreeNodeView key={child.key} node={child} collapsed={collapsed} onToggle={onToggle} />
          ))}
        </div>
      )}
    </div>
  )
}

function TreeView({ root, collapsed, onToggle }: { root: TreeNode; collapsed: Set<string>; onToggle: (key: string) => void }) {
  const hasContent = root.children.size > 0

  if (!hasContent) return (
    <div className="flex items-center justify-center h-full text-ops-dim text-[11px] font-display tracking-widest">
      NO ENDPOINTS DISCOVERED — RUN A SCAN FIRST
    </div>
  )

  return (
    <div className="overflow-y-auto h-full pr-1">
      {[...root.children.values()].map(child => (
        <TreeNodeView key={child.key} node={child} collapsed={collapsed} onToggle={onToggle} />
      ))}
    </div>
  )
}

// placeholder export — replaced in Task 4
export default function ApiMapModal(_: { endpoints: Endpoint[]; onClose: () => void }) {
  return null
}
```

- [ ] **Step 2: Verify no TS errors**

```bash
cd /Users/raajpatkar/Code/Hackathons/DeadDrop-Proto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no new errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/app/components/ApiMapModal.tsx
git commit -m "feat: add TreeNodeView recursive renderer for API map tree view"
```

---

## Task 3: Treemap View renderer

**Files:**
- Modify: `frontend/app/components/ApiMapModal.tsx`

- [ ] **Step 1: Add the color palette and `TreemapView` component**

Replace the placeholder `export default` at the bottom of `ApiMapModal.tsx` with:

```tsx
// ─── Treemap view ─────────────────────────────────────────────────────────────

const PALETTE = [
  { border: 'border-signal-green/40', bg: 'bg-signal-green-dim', text: 'text-signal-green' },
  { border: 'border-signal-blue/40',  bg: 'bg-signal-blue-dim',  text: 'text-signal-blue'  },
  { border: 'border-signal-amber/40', bg: 'bg-signal-amber-dim', text: 'text-signal-amber' },
  { border: 'border-signal-red/40',   bg: 'bg-signal-red-dim',   text: 'text-signal-red'   },
  { border: 'border-signal-purple/40',bg: 'bg-signal-purple-dim',text: 'text-signal-purple' },
]

function TreemapView({ groups }: { groups: Group[] }) {
  if (groups.length === 0) return (
    <div className="flex items-center justify-center h-full text-ops-dim text-[11px] font-display tracking-widest">
      NO ENDPOINTS DISCOVERED — RUN A SCAN FIRST
    </div>
  )

  return (
    <div className="overflow-y-auto h-full">
      <p className="text-[9px] tracking-[0.2em] text-ops-dim font-display uppercase mb-3">
        Top-level path groups · sized by endpoint count
      </p>
      <div className="grid grid-cols-2 gap-1">
        {groups.map((group, i) => {
          const palette = PALETTE[group.colorIndex]
          const isLargest = i === 0
          return (
            <div
              key={group.key}
              className={`rounded-sm border p-3 flex flex-col justify-between h-24 hover:brightness-110 transition-all ${palette.bg} ${palette.border}`}
              style={isLargest ? { gridRow: 'span 2', height: 'auto', minHeight: '10rem' } : undefined}
            >
              <div>
                <div className={`text-[11px] font-mono truncate ${palette.text}`}>{group.key}</div>
                <div className="text-[9px] text-ops-dim mt-1 truncate">
                  {group.sources.join(' · ')}
                </div>
              </div>
              <div className="flex items-end justify-between mt-2">
                <span className="text-3xl font-display opacity-20">{group.count}</span>
                <div className="flex flex-wrap gap-1 justify-end">
                  {group.methods.map(m => <MethodBadge key={m} method={m} />)}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// placeholder export — replaced in Task 4
export default function ApiMapModal(_: { endpoints: Endpoint[]; onClose: () => void }) {
  return null
}
```

- [ ] **Step 2: Verify no TS errors**

```bash
cd /Users/raajpatkar/Code/Hackathons/DeadDrop-Proto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no new errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/app/components/ApiMapModal.tsx
git commit -m "feat: add TreemapView renderer for API map treemap view"
```

---

## Task 4: Assemble the full modal

**Files:**
- Modify: `frontend/app/components/ApiMapModal.tsx`

- [ ] **Step 1: Replace the placeholder export with the real `ApiMapModal` component**

Replace the final `export default function ApiMapModal(...)` placeholder with:

```tsx
// ─── Modal ────────────────────────────────────────────────────────────────────

export default function ApiMapModal({ endpoints, onClose }: { endpoints: Endpoint[]; onClose: () => void }) {
  const [view, setView] = useState<'tree' | 'treemap'>('tree')

  const root = useMemo(() => buildTree(endpoints), [endpoints])
  const groups = useMemo(() => buildGroups(endpoints), [endpoints])

  const [collapsed, setCollapsed] = useState<Set<string>>(() => {
    const s = new Set<string>()
    collectDeepKeys(root, s)
    return s
  })

  // Re-seed collapsed keys when endpoints change (e.g. new scan while modal is open)
  useEffect(() => {
    const s = new Set<string>()
    collectDeepKeys(root, s)
    setCollapsed(s)
  }, [root])

  function toggle(key: string) {
    setCollapsed(prev => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  // Escape to close
  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const activeCt = endpoints.filter(e => !e.is_deprecated).length
  const zombieCt = endpoints.filter(e => e.is_deprecated).length

  return (
    <div
      className="fixed inset-0 z-[90] flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="relative w-full max-w-3xl mx-4 bg-ops-card border border-signal-green/30 rounded-sm shadow-glow-green flex flex-col max-h-[85vh]">

        {/* Corner accents */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-signal-green/50 pointer-events-none" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-signal-green/50 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-signal-green/50 pointer-events-none" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-signal-green/50 pointer-events-none" />

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-ops-border flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-1 h-5 bg-signal-green shadow-glow-green" />
            <span className="font-display text-xs tracking-[0.25em] text-signal-green uppercase">API Structure Map</span>
            <span className="text-[9px] tracking-widest text-ops-dim font-display">
              // {endpoints.length} ENDPOINTS · {groups.length} GROUPS
            </span>
          </div>
          <div className="flex items-center gap-2">
            {/* Toggle */}
            <div className="flex items-center border border-ops-border rounded-sm overflow-hidden">
              {(['tree', 'treemap'] as const).map(v => (
                <button
                  key={v}
                  onClick={() => setView(v)}
                  className={`px-3 py-1.5 text-[9px] font-display tracking-widest uppercase transition-all ${
                    view === v
                      ? 'bg-signal-green-dim text-signal-green border-r border-ops-border'
                      : 'text-ops-dim hover:text-ops-text border-r border-ops-border last:border-r-0'
                  }`}
                >
                  {v === 'tree' ? '⊞ TREE' : '▦ TREEMAP'}
                </button>
              ))}
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 flex items-center justify-center border border-ops-border rounded-sm text-ops-dim hover:text-ops-text hover:border-ops-border-bright transition-all text-xs font-display"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-hidden p-5">
          {view === 'tree'
            ? <TreeView root={root} collapsed={collapsed} onToggle={toggle} />
            : <TreemapView groups={groups} />
          }
        </div>

        {/* Footer */}
        <div className="flex items-center gap-5 px-5 py-2.5 border-t border-ops-border bg-ops-surface/40 flex-shrink-0">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-signal-green" />
            <span className="text-[9px] tracking-widest font-display text-ops-dim">ACTIVE</span>
            <span className="text-[9px] tracking-widest font-display text-signal-green">{activeCt}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-signal-red" />
            <span className="text-[9px] tracking-widest font-display text-ops-dim">ZOMBIE</span>
            <span className="text-[9px] tracking-widest font-display text-signal-red">{zombieCt}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-signal-amber" />
            <span className="text-[9px] tracking-widest font-display text-ops-dim">SHADOW</span>
            <span className="text-[9px] tracking-widest font-display text-ops-dim">0</span>
          </div>
          <div className="ml-auto text-[9px] tracking-widest font-display text-ops-faint">
            ESC TO CLOSE
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify no TS errors**

```bash
cd /Users/raajpatkar/Code/Hackathons/DeadDrop-Proto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/app/components/ApiMapModal.tsx
git commit -m "feat: assemble ApiMapModal with header, tree/treemap toggle, footer, Escape handler"
```

---

## Task 5: Wire modal into `page.tsx`

**Files:**
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Add the import at the top of `page.tsx`**

Add after the existing imports:

```tsx
import ApiMapModal from './components/ApiMapModal'
```

- [ ] **Step 2: Add `showMap` state**

In the `DashboardPage` component body, after the existing state declarations (`endpoints`, `tableLoading`, `apiOnline`), add:

```tsx
const [showMap, setShowMap] = useState(false)
```

- [ ] **Step 3: Add the `MapIcon` helper at the bottom of `page.tsx`**

Add next to the existing `RefreshIcon` function (do this **before** wiring the button so the function is defined first):

```tsx
function MapIcon() {
  return (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
        d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
    </svg>
  )
}
```

- [ ] **Step 4: Add the MAP button next to REFRESH**

In `page.tsx`, find the REFRESH button block inside the "Discovered Endpoints" section header:

```tsx
<button
  onClick={fetchEndpoints}
  disabled={tableLoading}
  className="flex items-center gap-2 text-[10px] tracking-widest font-display text-ops-dim hover:text-ops-text border border-ops-border hover:border-ops-border-bright px-3 py-1.5 rounded-sm transition-all disabled:opacity-40"
>
```

Add a MAP button **before** it (inside the same flex container):

```tsx
<button
  onClick={() => setShowMap(true)}
  className="flex items-center gap-2 text-[10px] tracking-widest font-display text-ops-dim hover:text-ops-text border border-ops-border hover:border-ops-border-bright px-3 py-1.5 rounded-sm transition-all"
>
  <MapIcon />
  <span>MAP</span>
</button>
```

- [ ] **Step 5: Render `<ApiMapModal>` conditionally**

In the JSX of `DashboardPage`, just before the closing `</div>` of the outermost `min-h-screen` div (after `<footer>`), add:

```tsx
{showMap && (
  <ApiMapModal endpoints={endpoints} onClose={() => setShowMap(false)} />
)}
```

- [ ] **Step 6: Verify no TS errors**

```bash
cd /Users/raajpatkar/Code/Hackathons/DeadDrop-Proto/frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: no errors.

- [ ] **Step 7: Run dev server and manually verify**

```bash
cd /Users/raajpatkar/Code/Hackathons/DeadDrop-Proto/frontend && npm run dev
```

Open http://localhost:3000. Check:
- MAP button appears next to REFRESH in the "Discovered Endpoints" header
- Clicking MAP opens the modal overlay
- TREE / TREEMAP toggle switches views
- ✕ button closes the modal
- Pressing Escape closes the modal
- Clicking the backdrop (outside the modal) closes it
- Empty state shows if no endpoints are loaded

- [ ] **Step 8: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat: wire ApiMapModal into dashboard with MAP button and showMap state"
```

---

## Task 6: Update `todo.md`

**Files:**
- Modify: `todo.md`

- [ ] **Step 1: Add and check off the new card in `todo.md`**

Add the following card to the "Sprint: Layer 4" section and mark it complete:

```markdown
- [x] **Card F4: API Structure Map Modal** ✅ DONE
  - `ApiMapModal` — tree + treemap toggle modal triggered from endpoints header
  - `buildTree` — path-segment tree with depth tracking, expand/collapse
  - `buildGroups` — first-3-segment grouping, count sort, color palette
  - Escape / backdrop / ✕ close handlers
  - Empty state, long-path truncation, source file dedup
```

- [ ] **Step 2: Commit**

```bash
git add todo.md
git commit -m "chore: mark Card F4 API Structure Map Modal as complete in todo.md"
```
