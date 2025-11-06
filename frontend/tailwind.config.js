/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          0: '#0D0D0D',
          1: '#111111',
          2: '#151515',
          3: '#1C1C1C',
        },
        border: '#212121',
        accent: {
          DEFAULT: '#A5B4FC',
          muted: 'rgba(165, 180, 252, 0.12)',
          subtle: 'rgba(165, 180, 252, 0.25)',
        },
        highlight: '#FFD600',
        text: {
          primary: '#F2F2F2',
          secondary: '#A0A0A0',
          tertiary: '#666666',
        },
        success: '#34D399',
        danger: '#F87171',
      },
      boxShadow: {
        layer: '0 8px 24px rgba(0, 0, 0, 0.35)',
        glow: '0 0 24px rgba(165, 180, 252, 0.25)',
      },
      borderRadius: {
        xl: '18px',
      },
      fontFamily: {
        sans: ['Inter', 'DM Sans', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

