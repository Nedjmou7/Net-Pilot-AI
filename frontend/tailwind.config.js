/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        clust: {
          bg: '#0a0d14',
          panel: '#10141e',
          card: '#141a26',
          cardHover: '#192030',
          border: '#1f2738',
          borderLight: '#2a354d',
          cyan: '#00e5ff',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#ef4444',
          blue: '#3b82f6',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
