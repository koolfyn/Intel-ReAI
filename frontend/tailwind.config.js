/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'reddit-orange': '#FF4500',
        'reddit-blue': '#0079D3',
        'reddit-dark': '#1A1A1B',
        'reddit-light': '#F6F7F8',
        'reddit-border': '#EDEFF1',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
