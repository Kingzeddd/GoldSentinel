/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: '#FFD700',
        'night-blue': '#0B1E3F',
        'forest-green': '#1C6B48',
        'alert-red': '#E63946',
      },
      fontFamily: {
        sans: ['Open Sans', 'Roboto', 'sans-serif'],
        heading: ['Montserrat', 'Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
} 