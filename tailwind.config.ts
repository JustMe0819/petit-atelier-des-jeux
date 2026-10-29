import type { Config } from 'tailwindcss';

/**
 * Thème repris de la maquette Google Stitch (mêmes noms de jetons),
 * aligné sur la palette de référence de la boutique :
 * crème #FFF9F0, jaune doux #FFD66B, vert sauge #B9D8B0, bleu ciel #B8DDF5,
 * rose poudré #F4C9D6, texte foncé #34343A.
 */
export default {
  content: ['./index.html', './src/client/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Surfaces (crème)
        background: '#FFF9F0',
        surface: '#FFF9F0',
        'surface-bright': '#FFFCF6',
        'surface-dim': '#EDE6DA',
        'surface-container-lowest': '#FFFFFF',
        'surface-container-low': '#FBF3E7',
        'surface-container': '#F6EDDF',
        'surface-container-high': '#F0E6D6',
        'surface-container-highest': '#E9DECC',
        'surface-variant': '#E9DECC',
        'on-surface': '#34343A',
        'on-background': '#34343A',
        'on-surface-variant': '#544C3E',
        outline: '#7F7664',
        'outline-variant': '#D7CCB8',
        'inverse-surface': '#34343A',
        'inverse-on-surface': '#F7F1E8',
        // Jaune doux
        primary: '#765B00',
        'on-primary': '#FFFFFF',
        'primary-container': '#FFD66B',
        'on-primary-container': '#5E4800',
        'primary-fixed': '#FFE29A',
        'primary-fixed-dim': '#E9C259',
        'on-primary-fixed': '#241A00',
        'inverse-primary': '#E9C259',
        // Vert sauge
        secondary: '#4A6545',
        'on-secondary': '#FFFFFF',
        'secondary-container': '#B9D8B0',
        'on-secondary-container': '#2F4A2B',
        'secondary-fixed': '#CCEBC2',
        'secondary-fixed-dim': '#B0CFA7',
        'on-secondary-fixed': '#082107',
        // Bleu ciel
        tertiary: '#3F6377',
        'on-tertiary': '#FFFFFF',
        'tertiary-container': '#B8DDF5',
        'on-tertiary-container': '#284C60',
        'tertiary-fixed': '#C4E7FF',
        'on-tertiary-fixed': '#001E2C',
        // Rose poudré
        rose: '#F4C9D6',
        'rose-soft': '#FBE6EC',
        'on-rose': '#6E2E44',
        // Titres (bleu ardoise de la planche)
        marine: '#2E4A5C',
        // Erreurs
        error: '#BA1A1A',
        'on-error': '#FFFFFF',
        'error-container': '#FFDAD6',
        'on-error-container': '#93000A',
      },
      borderRadius: { DEFAULT: '0.25rem', lg: '0.5rem', xl: '0.75rem', '2xl': '1rem', '3xl': '1.5rem', full: '9999px' },
      spacing: {
        'space-xs': '0.25rem', 'space-sm': '0.5rem', 'space-md': '1rem', 'space-lg': '1.5rem', 'space-xl': '2.5rem',
        gutter: '1.5rem', 'gutter-mobile': '1rem', margin: '2rem', 'margin-mobile': '1rem',
      },
      fontFamily: {
        titre: ['"Plus Jakarta Sans Variable"', 'system-ui', 'sans-serif'],
        texte: ['"Nunito Sans Variable"', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display-hero': ['44px', { lineHeight: '52px', letterSpacing: '-0.02em', fontWeight: '800' }],
        'display-hero-mobile': ['32px', { lineHeight: '38px', letterSpacing: '-0.01em', fontWeight: '800' }],
        'headline-lg': ['32px', { lineHeight: '40px', letterSpacing: '-0.01em', fontWeight: '700' }],
        'headline-lg-mobile': ['26px', { lineHeight: '32px', fontWeight: '700' }],
        'headline-md': ['24px', { lineHeight: '32px', fontWeight: '700' }],
        'headline-sm': ['20px', { lineHeight: '28px', fontWeight: '700' }],
        'title-md': ['18px', { lineHeight: '26px', fontWeight: '700' }],
        'body-lg': ['18px', { lineHeight: '28px' }],
        'body-md': ['16px', { lineHeight: '24px' }],
        'body-sm': ['14px', { lineHeight: '20px' }],
        'label-lg': ['14px', { lineHeight: '20px', letterSpacing: '0.02em', fontWeight: '700' }],
        'label-md': ['12px', { lineHeight: '16px', letterSpacing: '0.03em', fontWeight: '700' }],
        caption: ['12px', { lineHeight: '16px', fontWeight: '500' }],
      },
      boxShadow: {
        doux: '0 4px 16px rgba(52,52,58,0.06)',
        carte: '0 8px 24px rgba(52,52,58,0.08)',
        fort: '0 12px 32px rgba(52,52,58,0.14)',
      },
      maxWidth: { site: '80rem' },
    },
  },
  plugins: [],
} satisfies Config;
