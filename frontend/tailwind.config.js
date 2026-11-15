/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        solar: {
          blue: "#2563eb",
          cyan: "#06b6d4",
          amber: "#f59e0b",
          heat: "#ef4444"
        }
      }
    },
  },
  plugins: [],
}
