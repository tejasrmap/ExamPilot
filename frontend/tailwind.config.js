/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#090D18",
        sidebar: "#101625",
        card: "#151D2E",
        cardHover: "#1C263C",
        cardBorder: "#232F47",
        primary: {
          DEFAULT: "#7865F5",
          hover: "#6652E6",
          light: "#9282F8"
        },
        secondary: {
          DEFAULT: "#32B8D6",
          hover: "#25A2BE"
        },
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
        foreground: "#F8FAFC",
        muted: "#94A3B8"
      }
    },
  },
  plugins: [],
}

