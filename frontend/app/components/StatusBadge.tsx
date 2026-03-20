'use client'

export type Status = 'ACTIVE' | 'ZOMBIE' | 'SHADOW'

export function deriveStatus(isDeprecated: boolean): Status {
  return isDeprecated ? 'ZOMBIE' : 'ACTIVE'
}

const STATUS_CONFIG: Record<Status, { label: string; classes: string; dot: string }> = {
  ACTIVE: {
    label: 'ACTIVE',
    classes: 'bg-signal-green-dim border border-signal-green text-signal-green',
    dot: 'bg-signal-green shadow-glow-green animate-pulse-slow',
  },
  ZOMBIE: {
    label: 'ZOMBIE',
    classes: 'bg-signal-red-dim border border-signal-red text-signal-red',
    dot: 'bg-signal-red',
  },
  SHADOW: {
    label: 'SHADOW',
    classes: 'bg-signal-amber-dim border border-signal-amber text-signal-amber',
    dot: 'bg-signal-amber',
  },
}

export default function StatusBadge({ status }: { status: Status }) {
  const cfg = STATUS_CONFIG[status]
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-sm text-[10px] tracking-widest font-display ${cfg.classes}`}>
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${cfg.dot}`} />
      {cfg.label}
    </span>
  )
}
