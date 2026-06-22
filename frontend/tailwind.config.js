/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy:  { 900: '#0a0f1e', 800: '#0d1529', 700: '#111d3c', 600: '#172350' },
        pitch: { 500: '#22c55e', 400: '#4ade80', 300: '#86efac' },
        amber: { 500: '#f59e0b', 400: '#fbbf24' },
        danger:{ 500: '#ef4444', 400: '#f87171' },
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [],
}
