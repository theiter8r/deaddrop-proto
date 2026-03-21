# API Structure Map — Design Spec
**Date:** 2026-03-21
**Status:** Approved

---

## Overview

Add an "API Structure Map" modal to the DEADDROP dashboard. It visualizes all discovered endpoints as a hierarchical structure, giving users two complementary views toggled by a button: a collapsible path tree and a treemap (area chart). The modal is triggered by a button in the existing dashboard UI and does not replace the endpoints table.

---

## User Experience

- A **"MAP" button** appears in the "Discovered Endpoints" section header (next to the existing REFRESH button).
- Clicking it opens a **full-screen overlay modal**.
- The modal has a **TREE / TREEMAP toggle** in the header to switch views.
- A **close button (✕)** dismisses the modal.
- The modal renders entirely from the `endpoints` array already loaded in `page.tsx` — no extra API calls.

---

## Component Design

### `ApiMapModal.tsx`
Single new component. Receives `endpoints: Endpoint[]` and `onClose: () => void` as props.

**Internal state:**
- `view: 'tree' | 'treemap'` — which visualization is active (default: `'tree'`)

**Sections:**
- **Header** — title (`API STRUCTURE MAP`), total endpoint + group counts, TREE/TREEMAP toggle, close button
- **Body** — conditionally renders `<TreeView>` or `<TreemapView>` based on `view`
- **Footer** — Active / Zombie / Shadow summary counts

### Tree View (internal)
Built from scratch in React — no third-party library.

**Path parsing logic:**
- Split each `endpoint_path` on `/` to get segments (e.g. `/api/v1/users/{id}` → `['api', 'v1', 'users', '{id}']`)
- Build a nested object tree grouping endpoints by segment
- Each internal node stores: `segment`, `children`, `endpoints[]` (leaf-level HTTP methods)
- Each leaf stores: `http_method`, `is_deprecated`

**Rendering:**
- Recursive `TreeNode` sub-component
- Internal nodes show: toggle arrow (▼/▶), path segment, endpoint count badge
- Leaf nodes show: method chip (colored GET/POST/PUT/DEL/PATCH), path segment (dimmed)
- Nodes are expanded by default for the first 2 levels, collapsed beyond that
- Click on any internal node toggles expand/collapse (local state per node via a `Set<string>` of collapsed paths)

### Treemap View (internal)
Pure CSS grid — no D3 or charting library.

**Grouping logic:**
- Group endpoints by their **first two path segments** (e.g. `/api/v1/users/...` → group key `/api/v1/users`)
- Sort groups by endpoint count descending
- Assign each group a color from a fixed palette (green, blue, amber, red, purple, cycling)

**Rendering:**
- CSS grid with `grid-template-columns` weighted by relative group sizes (approximated to a 2-column layout)
- Each cell shows: group path, source file(s), endpoint count (large dimmed number), method chips
- Hover brightens the cell (`filter: brightness(1.2)`)
- Largest group spans 2 rows to reflect its weight visually

---

## Integration into `page.tsx`

- Add `showMap: boolean` state (default `false`)
- Render `<ApiMapModal>` conditionally when `showMap` is true
- Add a **MAP button** to the "Discovered Endpoints" section header (alongside the REFRESH button)
- Pass `endpoints` and `onClose={() => setShowMap(false)}` to the modal

---

## Styling

Follows existing design system strictly:
- `bg-ops-card`, `border-ops-border`, `font-display`, `tracking-widest` — same tokens as the rest of the dashboard
- Method chip colors: GET=blue, POST=green, PUT=amber, DEL=red, PATCH=purple
- `signal-green` accent for the modal border/glow (same as `DemoBanner`)
- No new CSS — Tailwind only

---

## Data Flow

```
page.tsx
  └─ endpoints: Endpoint[]  (already fetched)
       └─ ApiMapModal
            ├─ buildTree(endpoints) → nested node structure
            └─ buildGroups(endpoints) → flat group array
```

No new network requests. The modal derives all data client-side from the existing endpoint list.

---

## Out of Scope

- Clicking a node does NOT filter the endpoints table (read-only visualization)
- No search/filter within the modal
- No export or share functionality
- No animation between tree ↔ treemap transitions (instant swap is fine)
