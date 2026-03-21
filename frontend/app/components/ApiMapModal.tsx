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
  sources: string[]  // all deduplicated source files (render layer handles display truncation)
  colorIndex: number
}

// ─── Data transforms ──────────────────────────────────────────────────────────

/** Nodes deeper than this level start collapsed in the tree view. Root children are depth 1. */
const COLLAPSE_DEPTH = 2
/** Number of distinct colours in the treemap group palette. */
const GROUP_COLOR_COUNT = 5

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
    if (child.depth > COLLAPSE_DEPTH) acc.add(child.key)
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

  const sorted = Array.from(map.entries()).sort((a, b) => b[1].count - a[1].count)

  return sorted.map(([key, val], i) => {
    return { key, count: val.count, methods: [...val.methods], sources: Array.from(val.sources), colorIndex: i % GROUP_COLOR_COUNT }
  })
}

// placeholder export so file is valid — replaced in later tasks
export default function ApiMapModal(_: { endpoints: Endpoint[]; onClose: () => void }) {
  return null
}
