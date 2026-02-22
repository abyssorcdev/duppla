/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#F3EFFE',  // very light lavender — page background
          100: '#EAD8FD',  // light lavender — tag backgrounds, cards
          200: '#D4AEFC',  // medium lavender
          300: '#AA77F2',  // light purple  — text on dark backgrounds
          400: '#8B5FD8',  // mid purple    — muted text / sidebar nav
          500: '#6B3FBF',  // purple        — progress bars, accents
          600: '#272559',  // dark navy     — secondary text
          700: '#391DF2',  // electric violet — primary CTA, active nav
          800: '#2703A6',  // deep purple   — CTA hover
          900: '#040326',  // near black navy — sidebar
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
