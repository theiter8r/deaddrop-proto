'use client'

const METHOD_CONFIG: Record<string, string> = {
  GET:     'bg-signal-blue-dim   border border-signal-blue   text-signal-blue',
  POST:    'bg-signal-green-dim  border border-signal-green  text-signal-green',
  PUT:     'bg-signal-amber-dim  border border-signal-amber  text-signal-amber',
  PATCH:   'bg-signal-orange-dim border border-signal-orange text-signal-orange',
  DELETE:  'bg-signal-red-dim    border border-signal-red    text-signal-red',
  HEAD:    'bg-signal-purple-dim border border-signal-purple text-signal-purple',
  OPTIONS: 'border border-ops-border text-ops-dim',
}

export default function MethodBadge({ method }: { method: string }) {
  const classes = METHOD_CONFIG[method.toUpperCase()] ?? 'border border-ops-border text-ops-dim'
  return (
    <span className={`inline-block px-2 py-0.5 rounded-sm text-[10px] tracking-widest font-display min-w-[52px] text-center ${classes}`}>
      {method.toUpperCase()}
    </span>
  )
}
