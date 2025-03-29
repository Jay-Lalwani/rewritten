import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

// 1. Import Font Awesome CSS
import '@fortawesome/fontawesome-svg-core/styles.css'; 
// 2. Prevent Font Awesome from adding its CSS since we did it manually above:
import { config } from '@fortawesome/fontawesome-svg-core';
config.autoAddCss = false;

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Rewritten: Reshape History',
  description: 'An interactive historical narrative experience',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* 3. Remove the old Font Awesome CDN link */}
        {/* <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" 
        /> */}
        <link 
          href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Source+Sans+Pro:wght@400;600&display=swap" 
          rel="stylesheet"
        />
      </head>
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
} 