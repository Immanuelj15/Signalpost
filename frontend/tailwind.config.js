/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#090D16",
        surface: {
          DEFAULT: "#0F1626",
          elevated: "#151F32",
          card: "#111827",
          hover: "#1A263D",
          border: "#1E293B",
        },
        brand: {
          50: "#EFF6FF",
          100: "#DBEAFE",
          200: "#BFDBFE",
          300: "#93C5FD",
          400: "#60A5FA",
          500: "#3B82F6",
          600: "#2563EB",
          700: "#1D4ED8",
          800: "#1E40AF",
          900: "#1E3A8A",
          cyan: "#38BDF8",
        },
        status: {
          verified: "#10B981",
          partial: "#F59E0B",
          error: "#EF4444",
          neutral: "#64748B",
        }
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "Inter", "-apple-system", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 4px 20px -2px rgba(0, 0, 0, 0.4), 0 2px 6px -1px rgba(15, 23, 42, 0.3)",
        glow: "0 0 20px -4px rgba(59, 130, 246, 0.3)",
      }
    },
  },
  plugins: [],
}
