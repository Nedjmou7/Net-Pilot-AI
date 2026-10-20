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
        cisco: {
          blue: '#049fd9',
          dark: '#0e273c',
          navy: '#005073',
          light: '#6abf40'
        }
      }
    },
  },
  plugins: [],
}
