import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'io.aivox.app',
  appName: 'AIVOX',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    // For native testing, point to live server (replace with your Vercel URL)
    // url: 'https://aivox.vercel.app',
    cleartext: false,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0f0f1a',
      showSpinner: false,
    },
  },
};

export default config;
