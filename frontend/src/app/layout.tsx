import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Script from 'next/script';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'BevHub AI — SaaS Platform Builder',
  description: 'Launch, build, and grow your online business using AI agents in one click.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} min-h-screen bg-[#030303] text-white selection:bg-purple-500/30`} suppressHydrationWarning>
        {children}
        
        {/* DOM Patch for React + Google Translate conflict */}
        <Script id="react-google-translate-patch" strategy="beforeInteractive">
          {`
            if (typeof Node === 'function' && Node.prototype) {
              const originalRemoveChild = Node.prototype.removeChild;
              Node.prototype.removeChild = function(child) {
                if (child.parentNode !== this) {
                  return child;
                }
                return originalRemoveChild.apply(this, arguments);
              };

              const originalInsertBefore = Node.prototype.insertBefore;
              Node.prototype.insertBefore = function(newNode, referenceNode) {
                if (referenceNode && referenceNode.parentNode !== this) {
                  return newNode;
                }
                return originalInsertBefore.apply(this, arguments);
              };
              
              const originalConsoleError = console.error;
              console.error = function(...args) {
                if (typeof args[0] === 'string' && (args[0].includes('bis_skin_checked') || args[0].includes('Extra attributes from the server'))) {
                  return;
                }
                return originalConsoleError.apply(console, args);
              };
            }
          `}
        </Script>

        <Script src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit" strategy="afterInteractive" />
        <Script id="google-translate-init" strategy="afterInteractive">
          {`
            function googleTranslateElementInit() {
              new google.translate.TranslateElement({
                pageLanguage: 'en', 
                includedLanguages: 'ru,uz,en',
                layout: google.translate.TranslateElement.InlineLayout.SIMPLE
              }, 'google_translate_element');
            }
          `}
        </Script>
      </body>
    </html>
  );
}
