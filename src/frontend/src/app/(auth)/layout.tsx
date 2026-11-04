import React from "react";
import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#F7F8F5] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-[#17212B] flex items-center justify-center p-2.5 shadow-md">
            <svg viewBox="0 0 120 120" className="w-full h-full" fill="none">
              <defs>
                <linearGradient id="auth-grad" x1="20" y1="100" x2="100" y2="20" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#2A9D8F" />
                  <stop offset="100%" stopColor="#A78BFA" />
                </linearGradient>
              </defs>
              <path d="M60 22L26 98h14l6.5-16h27L80 98h14L60 22z" fill="url(#auth-grad)" />
              <path d="M60 46L48.5 74h23L60 46z" fill="#17212B" />
              <rect x="42" y="68" width="36" height="5" rx="2.5" fill="#E9B44C" />
            </svg>
          </div>
        </Link>
        <h2 className="mt-3 text-2xl font-extrabold text-[#17212B] tracking-tight">AROHA</h2>
        <p className="text-xs text-[#636E72] mt-0.5">AI-Powered Social Media Analyzer</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-8 px-6 shadow-xl shadow-black/5 rounded-3xl border border-gray-100 sm:px-10">
          {children}
        </div>
      </div>
    </div>
  );
}

