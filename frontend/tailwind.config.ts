import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Michroma', 'monospace'],
        mono: ['Share Tech Mono', 'monospace'],
      },
      colors: {
        ops: {
          bg:       '#080c10',
          surface:  '#0d1520',
          card:     '#101c2c',
          border:   '#1a2d42',
          'border-bright': '#1e3d5a',
          text:     '#c4d4e0',
          dim:      '#4a6278',
          faint:    '#1e3040',
        },
        signal: {
          green:    '#00ff9d',
          'green-dim': 'rgba(0,255,157,0.08)',
          'green-glow': 'rgba(0,255,157,0.25)',
          red:      '#ff3b5c',
          'red-dim': 'rgba(255,59,92,0.08)',
          amber:    '#ffb800',
          'amber-dim': 'rgba(255,184,0,0.08)',
          blue:     '#38bdf8',
          'blue-dim': 'rgba(56,189,248,0.08)',
          purple:   '#a78bfa',
          'purple-dim': 'rgba(167,139,250,0.08)',
          orange:   '#fb923c',
          'orange-dim': 'rgba(251,146,60,0.08)',
        },
      },
      boxShadow: {
        'glow-green': '0 0 12px rgba(0,255,157,0.3), 0 0 24px rgba(0,255,157,0.1)',
        'glow-red':   '0 0 12px rgba(255,59,92,0.3)',
        'glow-amber': '0 0 12px rgba(255,184,0,0.3)',
      },
      animation: {
        'scan': 'scan 8s linear infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'fade-in': 'fadeIn 0.4s ease forwards',
        'slide-up': 'slideUp 0.3s ease forwards',
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
