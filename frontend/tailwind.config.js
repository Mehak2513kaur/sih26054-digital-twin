/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        avionics: {
          bg: '#080c14',
          panel: '#0f172a',
          card: '#131e33',
          cardHover: '#182640',
          border: '#1e293b',
          accent: '#0284c7',
          cyan: '#06b6d4',
          healthy: '#10b981',
          warning: '#f59e0b',
          critical: '#ef4444'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
      }
    },
  },
  plugins: [],
}
