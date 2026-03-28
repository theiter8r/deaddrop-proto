import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'deaddrop // Nothing Gets Through',
  description: 'Automated API Security & Governance — Layer 4 Dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="grid-bg min-h-screen">{children}</body>
    </html>
  )
}
