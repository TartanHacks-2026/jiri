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
      <body>
        <div className="jiri-bg-grid" aria-hidden />
        <div className="jiri-bg-orbit jiri-bg-orbit-a" aria-hidden />
        <div className="jiri-bg-orbit jiri-bg-orbit-b" aria-hidden />
        {children}
      </body>
    </html>
  );
}
