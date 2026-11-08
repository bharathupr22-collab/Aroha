import Link from "next/link";
import {
  BarChart3,
  Link as LinkIcon,
  Volume2,
  Mic,
  Newspaper,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  TrendingUp,
  CheckCircle2,
  Lock,
} from "lucide-react";
import { InstagramIcon } from "@/components/icons/InstagramIcon";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#F7F8F5] text-[#2D3436] flex flex-col">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#17212B] flex items-center justify-center p-2 shadow-sm">
              <svg viewBox="0 0 120 120" className="w-full h-full" fill="none">
                <defs>
                  <linearGradient id="nav-grad" x1="20" y1="100" x2="100" y2="20" gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor="#2A9D8F" />
                    <stop offset="100%" stopColor="#A78BFA" />
                  </linearGradient>
                </defs>
                <path d="M60 22L26 98h14l6.5-16h27L80 98h14L60 22z" fill="url(#nav-grad)" />
                <path d="M60 46L48.5 74h23L60 46z" fill="#17212B" />
                <rect x="42" y="68" width="36" height="5" rx="2.5" fill="#E9B44C" />
              </svg>
            </div>
            <span className="text-xl font-bold tracking-wider text-[#17212B]">AROHA</span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#636E72]">
            <a href="#features" className="hover:text-[#2A9D8F] transition-colors">Features</a>
            <a href="#architecture" className="hover:text-[#2A9D8F] transition-colors">AI & Integrity</a>
            <a href="#security" className="hover:text-[#2A9D8F] transition-colors">Security</a>
            <Link href="/dashboard/trends" className="hover:text-[#2A9D8F] transition-colors">Industry News</Link>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-4 py-2 text-sm font-semibold text-[#17212B] hover:text-[#2A9D8F] transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-5 py-2 text-sm font-semibold text-white bg-[#2A9D8F] rounded-full hover:bg-[#238478] shadow-sm transition-all shadow-[#2A9D8F]/20"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#2A9D8F]/10 text-[#2A9D8F] text-xs font-semibold tracking-wide uppercase mb-8">
            <Sparkles size={14} /> MCA Major Project &bull; AI-Powered Multimedia Platform
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#17212B] tracking-tight max-w-4xl mx-auto leading-tight">
            Understand Your Social Media. <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#2A9D8F] via-[#A78BFA] to-[#E9B44C]">
              Discover What Matters.
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-[#636E72] max-w-2xl mx-auto leading-relaxed">
            AROHA empowers creators and businesses with real-time Instagram performance analytics,
            broken promotional link detection, reel audio integrity tracking, and AI-driven lip-sync mismatch analysis.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full text-base font-semibold text-white bg-[#17212B] hover:bg-[#2A9D8F] transition-all shadow-lg shadow-[#17212B]/10 hover:shadow-[#2A9D8F]/20"
            >
              Get Started Free <ArrowRight size={18} />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full text-base font-semibold text-[#17212B] bg-white border border-gray-200 hover:border-[#2A9D8F] hover:bg-gray-50 transition-all shadow-sm"
            >
              <InstagramIcon size={18} className="text-[#2A9D8F]" /> Connect Instagram
            </Link>
          </div>

          {/* Value Highlights */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
            <div className="p-4 rounded-2xl bg-white/70 border border-gray-100 shadow-sm backdrop-blur-sm">
              <p className="text-2xl font-bold text-[#17212B]">360&deg;</p>
              <p className="text-xs text-[#636E72] mt-0.5">Account & Reel Insights</p>
            </div>
            <div className="p-4 rounded-2xl bg-white/70 border border-gray-100 shadow-sm backdrop-blur-sm">
              <p className="text-2xl font-bold text-[#2A9D8F]">SSRF-Safe</p>
              <p className="text-xs text-[#636E72] mt-0.5">Affiliate Link Verification</p>
            </div>
            <div className="p-4 rounded-2xl bg-white/70 border border-gray-100 shadow-sm backdrop-blur-sm">
              <p className="text-2xl font-bold text-[#A78BFA]">MFCC</p>
              <p className="text-xs text-[#636E72] mt-0.5">Audio Fingerprint Loss Detection</p>
            </div>
            <div className="p-4 rounded-2xl bg-white/70 border border-gray-100 shadow-sm backdrop-blur-sm">
              <p className="text-2xl font-bold text-[#E9B44C]">AI AV-Sync</p>
              <p className="text-xs text-[#636E72] mt-0.5">Lip-Sync Offset Analysis</p>
            </div>
          </div>
        </div>

        {/* Ambient decorative gradients */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-[#2A9D8F]/15 via-[#A78BFA]/10 to-transparent rounded-full blur-3xl pointer-events-none -z-0" />
      </section>

      {/* Feature Showcase */}
      <section id="features" className="py-20 bg-white border-y border-gray-200/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold tracking-widest text-[#2A9D8F] uppercase">Core Capabilities</h2>
            <p className="mt-2 text-3xl sm:text-4xl font-extrabold text-[#17212B] tracking-tight">
              Five Centralized Pillars of Content Integrity & Analytics
            </p>
            <p className="mt-4 text-base text-[#636E72]">
              Unlike basic metrics tools, AROHA inspects visual, auditory, and promotional health of your creator ecosystem.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* 1. Analytics */}
            <div className="group p-8 rounded-3xl bg-[#F7F8F5] border border-gray-100 hover:border-[#2A9D8F]/40 hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-2xl bg-[#2A9D8F]/10 text-[#2A9D8F] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <BarChart3 size={24} />
              </div>
              <h3 className="text-xl font-bold text-[#17212B] mb-2">Instagram Analytics & Growth</h3>
              <p className="text-sm text-[#636E72] leading-relaxed mb-4">
                Monitor true engagement rates, reach, net follower growth snapshots, and time-series trends without inflated vanity metrics.
              </p>
              <ul className="text-xs text-[#636E72] space-y-1.5">
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#2A9D8F]" /> Net follower growth & unfollowers estimation</li>
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#2A9D8F]" /> Standardised engagement calculations</li>
              </ul>
            </div>

            {/* 2. Link Detector */}
            <div className="group p-8 rounded-3xl bg-[#F7F8F5] border border-gray-100 hover:border-[#2A9D8F]/40 hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-2xl bg-[#A78BFA]/20 text-[#A78BFA] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <LinkIcon size={24} />
              </div>
              <h3 className="text-xl font-bold text-[#17212B] mb-2">Promotional Link Validator</h3>
              <p className="text-sm text-[#636E72] leading-relaxed mb-4">
                Validate affiliate URLs, bio links, and sponsor landing pages against 404/500 errors, broken redirects, and security threats.
              </p>
              <ul className="text-xs text-[#636E72] space-y-1.5">
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#A78BFA]" /> SSRF-protected multi-hop redirect verification</li>
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#A78BFA]" /> Text extraction and bulk URL analysis</li>
              </ul>
            </div>

            {/* 3. Audio Loss */}
            <div className="group p-8 rounded-3xl bg-[#F7F8F5] border border-gray-100 hover:border-[#2A9D8F]/40 hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-2xl bg-[#E9B44C]/20 text-[#E9B44C] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Volume2 size={24} />
              </div>
              <h3 className="text-xl font-bold text-[#17212B] mb-2">Reel Audio Loss Detector</h3>
              <p className="text-sm text-[#636E72] leading-relaxed mb-4">
                Detect if copyright strikes or platform mute rules disabled your audio. Uses acoustic spectrogram fingerprinting.
              </p>
              <ul className="text-xs text-[#636E72] space-y-1.5">
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#E9B44C]" /> Cosine similarity on acoustic fingerprints</li>
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#E9B44C]" /> Detects silent audio, replaced audio & mutes</li>
              </ul>
            </div>

            {/* 4. Lip-Sync */}
            <div className="group p-8 rounded-3xl bg-[#F7F8F5] border border-gray-100 hover:border-[#2A9D8F]/40 hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-2xl bg-[#17212B]/10 text-[#17212B] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Mic size={24} />
              </div>
              <h3 className="text-xl font-bold text-[#17212B] mb-2">AI Lip-Sync Mismatch Detector</h3>
              <p className="text-sm text-[#636E72] leading-relaxed mb-4">
                Research-grade audio-visual synchronization analysis evaluating temporal correlation between mouth movements and vocal track.
              </p>
              <ul className="text-xs text-[#636E72] space-y-1.5">
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#17212B]" /> Quantifies offset in milliseconds (ms)</li>
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#17212B]" /> Categorizes audio-ahead vs video-ahead</li>
              </ul>
            </div>

            {/* 5. Trends & News */}
            <div className="group p-8 rounded-3xl bg-[#F7F8F5] border border-gray-100 hover:border-[#2A9D8F]/40 hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-2xl bg-[#2A9D8F]/10 text-[#2A9D8F] flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Newspaper size={24} />
              </div>
              <h3 className="text-xl font-bold text-[#17212B] mb-2">Trends & Industry News</h3>
              <p className="text-sm text-[#636E72] leading-relaxed mb-4">
                Pinterest-inspired dynamic visual feed tracking algorithm changes, Reels formats, AI creator tools, and marketing announcements.
              </p>
              <ul className="text-xs text-[#636E72] space-y-1.5">
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#2A9D8F]" /> Categorized RSS feed ingestion</li>
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-[#2A9D8F]" /> Full-text search and trending stories</li>
              </ul>
            </div>

            {/* 6. Privacy & Security */}
            <div className="group p-8 rounded-3xl bg-[#F7F8F5] border border-gray-100 hover:border-[#2A9D8F]/40 hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <ShieldCheck size={24} />
              </div>
              <h3 className="text-xl font-bold text-[#17212B] mb-2">User Privacy & Consent</h3>
              <p className="text-sm text-[#636E72] leading-relaxed mb-4">
                Zero password harvesting. Official Meta OAuth with Fernet token encryption at rest and explicit media retention consent.
              </p>
              <ul className="text-xs text-[#636E72] space-y-1.5">
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-emerald-600" /> Explicit model-training opt-in controls</li>
                <li className="flex items-center gap-2"><CheckCircle2 size={14} className="text-emerald-600" /> Instant one-click token revocation</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Security Statement Banner */}
      <section id="security" className="py-16 bg-[#17212B] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 text-[#E9B44C] text-sm font-semibold mb-2">
                <Lock size={16} /> Official Meta API Compliance
              </div>
              <h3 className="text-2xl sm:text-3xl font-bold">Your Credentials Never Touch Our Database</h3>
              <p className="mt-3 text-sm text-gray-400 leading-relaxed">
                AROHA strictly uses the official Instagram Graph API OAuth protocol. We never ask for your Instagram password,
                never scrape private sessions, and isolate every user&apos;s analytical reports. Public website features remain available without Instagram connection.
              </p>
            </div>
            <Link
              href="/register"
              className="px-8 py-3.5 rounded-full text-sm font-bold text-[#17212B] bg-[#E9B44C] hover:bg-amber-400 transition-colors shrink-0"
            >
              Create Free Account
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto bg-white border-t border-gray-200 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[#17212B] flex items-center justify-center p-1.5">
              <svg viewBox="0 0 120 120" className="w-full h-full" fill="none">
                <path d="M60 22L26 98h14l6.5-16h27L80 98h14L60 22z" fill="#2A9D8F" />
                <path d="M60 46L48.5 74h23L60 46z" fill="#17212B" />
                <rect x="42" y="68" width="36" height="5" rx="2.5" fill="#E9B44C" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-bold text-[#17212B]">AROHA Platform</p>
              <p className="text-xs text-[#636E72]">MCA Major Project Specification &bull; 2026</p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs text-[#636E72]">
            <Link href="/dashboard" className="hover:text-[#2A9D8F] transition-colors">Dashboard</Link>
            <Link href="/dashboard/trends" className="hover:text-[#2A9D8F] transition-colors">News Feed</Link>
            <Link href="/login" className="hover:text-[#2A9D8F] transition-colors">Sign In</Link>
            <Link href="/register" className="hover:text-[#2A9D8F] transition-colors">Register</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
