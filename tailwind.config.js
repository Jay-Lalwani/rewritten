/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2c3e50",
        secondary: "#e74c3c",
        accent: "#f39c12",
        dark: "#1a252f",
        light: "#f8f9fa",
        text: "#333",
        background: "#f5f5f5",
        paper: "#fff8ee",
      },
      fontFamily: {
        serif: ["Playfair Display", "serif"],
        sans: ["Source Sans Pro", "sans-serif"],
      },
    },
  },
  plugins: [],
} 