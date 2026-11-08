import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AROHA – AI-Powered Social Media Analyzer",
  description: "An AI-Assisted Instagram Analytics and Multimedia Content Integrity Monitoring Platform",
  icons: {
    icon: "/logo/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="antialiased">
      <body className="min-h-screen flex flex-col bg-[#F7F8F5] text-[#2D3436] font-sans">
        {children}
      </body>
    </html>
  );
}
