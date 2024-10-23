/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: [
    './**/templates/*.html',
  ],
  content: ["./core/**/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [],
}

