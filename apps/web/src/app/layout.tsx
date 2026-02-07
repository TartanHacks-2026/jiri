import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Jiri Command Center",
  description: "Voice -> transcript -> plan -> tools -> artifacts",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div className="jiri-bg-grid" aria-hidden />
        <div className="jiri-bg-orbit jiri-bg-orbit-a" aria-hidden />
        <div className="jiri-bg-orbit jiri-bg-orbit-b" aria-hidden />
        {children}
      </body>
    </html>
  );
}
