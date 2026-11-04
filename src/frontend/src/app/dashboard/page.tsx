"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import {
  instagram,
  notifications,
  type InstagramAccount,
  type IssueNotification,
  type NotificationSummary,
} from "@/services/api";
import {
  Users,
  TrendingUp,
  Link as LinkIcon,
  Volume2,
  Mic,
  Newspaper,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  ExternalLink,
  Bell,
  Clock,
  Eye,
  Check,
  RefreshCw,
  Loader2,
} from "lucide-react";
import { InstagramIcon } from "@/components/icons/InstagramIcon";

type AlertFilter = "all" | "broken_link" | "audio_loss" | "lipsync_mismatch" | "unread" | "resolved" | "unresolved";

export default function DashboardHome() {
  const { user } = useAuth();
  const [account, setAccount] = useState<InstagramAccount | null>(null);
  const [summary, setSummary] = useState<NotificationSummary | null>(null);
  const [recentIssues, setRecentIssues] = useState<IssueNotification[]>([]);
  const [alertFilter, setAlertFilter] = useState<AlertFilter>("all");
  const [loading, setLoading] = useState(true);
  const [auditing, setAuditing] = useState(false);
  const [auditMessage, setAuditMessage] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // 1. Instagram account
      try {
        const acc = await instagram.getAccount();
        setAccount(acc);
      } catch {
        setAccount(null);
      }

      // 2. Notification summary & recent issues
      try {
        const [sum, notifs] = await Promise.all([
          notifications.getSummary(),
          notifications.getNotifications({ limit: 15 }),
        ]);
        setSummary(sum);
        setRecentIssues(notifs || []);
      } catch {
        // empty
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleAudit = async () => {
    setAuditing(true);
    setAuditMessage(null);
    try {
      const res = await notifications.triggerScan();
      setAuditMessage(
        `Audit complete: Inspected ${res.audited_media_count} Reels. Detected ${res.new_issues_detected} new issue(s).`
      );
      await loadDashboardData();
    } catch {
      // error
    } finally {
      setAuditing(false);
    }
  };

  const filteredAlerts = recentIssues.filter((item) => {
    if (alertFilter === "all") return true;
    if (alertFilter === "broken_link") return item.issue_category === "broken_link";
    if (alertFilter === "audio_loss") return item.issue_category === "audio_loss";
    if (alertFilter === "lipsync_mismatch") return item.issue_category === "lipsync_mismatch";
    if (alertFilter === "unread") return !item.is_read;
    if (alertFilter === "resolved") return item.is_resolved;
    if (alertFilter === "unresolved") return !item.is_resolved;
    return true;
  });

  const getFeatureCatalogUrl = (item: IssueNotification) => {
    const mediaParam = item.media_id ? `media_id=${item.media_id}` : "";
    const issueParam = `issue_id=${item.id}`;
    const qs = [mediaParam, issueParam].filter(Boolean).join("&");

    if (item.issue_category === "broken_link") {
      return `/dashboard/link-analyzer?${qs}`;
    }
    if (item.issue_category === "audio_loss") {
      return `/dashboard/audio-detector?${qs}`;
    }
    return `/dashboard/lipsync?${qs}`;
  };

  return (
    <div className="space-y-8">
      {/* Welcome & Integrity Scanner Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-[#17212B] via-[#1f2d3a] to-[#2A9D8F]/80 p-6 md:p-8 rounded-3xl text-white shadow-lg">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-[#E9B44C] text-xs font-semibold mb-2">
            <Sparkles size={14} /> Unified Multimedia Integrity Platform
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Welcome back, {user ? user.name : "Creator"}
          </h1>
          <p className="mt-1 text-xs sm:text-sm text-gray-300">
            Real-time notifications pinpointing exact affected Instagram Reels across links, audio & lip-sync.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-start sm:self-center shrink-0">
          <button
            onClick={handleAudit}
            disabled={auditing}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-bold bg-[#2A9D8F] hover:bg-[#238478] text-white transition-all shadow-md disabled:opacity-50"
          >
            {auditing ? (
              <>
                <Loader2 size={14} className="animate-spin" /> Scanning Reels...
              </>
            ) : (
              <>
                <RefreshCw size={14} /> Audit Content
              </>
            )}
          </button>

          {!account && (
            <Link
              href="/dashboard/settings"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-bold bg-[#E9B44C] hover:bg-amber-400 text-[#17212B] transition-all shadow-md"
            >
              <InstagramIcon size={14} /> Connect IG
            </Link>
          )}
        </div>
      </div>

      {auditMessage && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle2 size={16} className="shrink-0 text-emerald-600" />
          <span>{auditMessage}</span>
        </div>
      )}

      {/* 3. Main Dashboard Summary Cards (as specified in SRS) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-[#636E72]">
            Issue Monitoring Overview
          </h2>
          <Link
            href="/dashboard/notifications"
            className="text-xs font-semibold text-[#2A9D8F] hover:underline flex items-center gap-1"
          >
            All Notifications ({summary?.unread_count ?? 0} unread) <ArrowRight size={12} />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {/* Card 1: Total Issues Detected */}
          <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <span className="text-[11px] font-semibold text-[#636E72] uppercase">Total Issues</span>
            <p className="text-2xl font-bold text-[#17212B] mt-2">
              {summary?.total_issues ?? 0}
            </p>
            <span className="text-[10px] text-gray-400 mt-1">Across all Reels</span>
          </div>

          {/* Card 2: Broken Promotional Links */}
          <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-[#A78BFA]">
              <span className="text-[11px] font-semibold text-[#636E72] uppercase">Broken Links</span>
              <LinkIcon size={14} />
            </div>
            <p className="text-2xl font-bold text-[#A78BFA] mt-2">
              {summary?.broken_link_issues ?? 0}
            </p>
            <span className="text-[10px] text-gray-400 mt-1">404s & Dead URLs</span>
          </div>

          {/* Card 3: Audio Issues */}
          <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-[#E9B44C]">
              <span className="text-[11px] font-semibold text-[#636E72] uppercase">Audio Issues</span>
              <Volume2 size={14} />
            </div>
            <p className="text-2xl font-bold text-[#E9B44C] mt-2">
              {summary?.audio_issues ?? 0}
            </p>
            <span className="text-[10px] text-gray-400 mt-1">Mutes & Discontinuities</span>
          </div>

          {/* Card 4: Lip-Sync Issues */}
          <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-[#2A9D8F]">
              <span className="text-[11px] font-semibold text-[#636E72] uppercase">Lip-Sync Issues</span>
              <Mic size={14} />
            </div>
            <p className="text-2xl font-bold text-[#2A9D8F] mt-2">
              {summary?.lipsync_issues ?? 0}
            </p>
            <span className="text-[10px] text-gray-400 mt-1">Sync offsets &gt;45ms</span>
          </div>

          {/* Card 5: Unresolved Issues */}
          <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-red-500">
              <span className="text-[11px] font-semibold text-[#636E72] uppercase">Unresolved</span>
              <AlertTriangle size={14} />
            </div>
            <p className="text-2xl font-bold text-red-600 mt-2">
              {summary?.unresolved_issues ?? 0}
            </p>
            <span className="text-[10px] text-red-500/80 mt-1">Requires Attention</span>
          </div>

          {/* Card 6: Resolved Issues */}
          <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-emerald-600">
              <span className="text-[11px] font-semibold text-[#636E72] uppercase">Resolved</span>
              <CheckCircle2 size={14} />
            </div>
            <p className="text-2xl font-bold text-emerald-600 mt-2">
              {summary?.resolved_issues ?? 0}
            </p>
            <span className="text-[10px] text-emerald-600/80 mt-1">Fixed by Creator</span>
          </div>
        </div>
      </div>

      {/* Recent Alerts Section (with Filter Tabs) */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-100 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <Bell size={18} className="text-[#2A9D8F]" />
              <h2 className="text-base font-bold text-[#17212B]">Recent Content Alerts</h2>
            </div>
            <p className="text-xs text-[#636E72] mt-0.5">
              Exact Instagram Reels and posts flagged with integrity problems
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center gap-1.5 bg-[#F7F8F5] p-1 rounded-2xl text-xs font-semibold text-[#636E72]">
            {[
              { id: "all", label: "All" },
              { id: "broken_link", label: "Broken Links" },
              { id: "audio_loss", label: "Audio" },
              { id: "lipsync_mismatch", label: "Lip-Sync" },
              { id: "unread", label: "Unread" },
              { id: "unresolved", label: "Unresolved" },
              { id: "resolved", label: "Resolved" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setAlertFilter(tab.id as AlertFilter)}
                className={`px-3 py-1 rounded-xl transition-all ${
                  alertFilter === tab.id
                    ? "bg-[#17212B] text-white shadow-sm"
                    : "hover:text-[#17212B]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Alerts List */}
        {loading ? (
          <div className="py-12 text-center text-xs text-[#636E72]">
            <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
            Loading recent issues...
          </div>
        ) : filteredAlerts.length === 0 ? (
          <div className="py-12 text-center text-xs text-[#636E72] space-y-2">
            <CheckCircle2 size={32} className="mx-auto text-emerald-500" />
            <p className="font-semibold text-sm text-[#17212B]">No alerts in this category</p>
            <p className="text-gray-400">Click &ldquo;Audit Content&rdquo; above to run diagnostics across your Reels.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredAlerts.slice(0, 6).map((item) => (
              <div key={item.id} className="py-4 flex flex-col sm:flex-row items-start gap-4 text-xs">
                {/* Reel Thumbnail */}
                <div className="relative w-20 h-20 rounded-xl overflow-hidden bg-gray-100 shrink-0 border border-gray-200">
                  {item.media?.thumbnail_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={item.media.thumbnail_url}
                      alt="Reel Preview"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-[10px]">
                      No Preview
                    </div>
                  )}
                  <span className="absolute bottom-1 right-1 px-1 py-0.2 rounded bg-black/70 text-[8px] text-white font-mono">
                    REEL
                  </span>
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          item.issue_category === "broken_link"
                            ? "bg-[#A78BFA]/20 text-[#A78BFA]"
                            : item.issue_category === "audio_loss"
                            ? "bg-[#E9B44C]/20 text-[#E9B44C]"
                            : "bg-[#2A9D8F]/20 text-[#2A9D8F]"
                        }`}
                      >
                        {item.issue_category.replace("_", " ")}
                      </span>
                      {item.is_resolved && (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700">
                          Resolved
                        </span>
                      )}
                      {!item.is_read && (
                        <span className="w-2 h-2 rounded-full bg-[#2A9D8F]" title="Unread" />
                      )}
                    </div>
                    <span className="text-[11px] text-gray-400 flex items-center gap-1">
                      <Clock size={11} /> {new Date(item.analysis_timestamp).toLocaleDateString()}
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-[#17212B] line-clamp-1">{item.title}</h3>

                  {item.media?.caption && (
                    <p className="text-xs text-[#636E72] line-clamp-1 italic">
                      &ldquo;{item.media.caption}&rdquo;
                    </p>
                  )}

                  <p className="text-xs text-[#2D3436] mt-1">{item.description}</p>

                  {/* Actions Bar */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                    <div className="flex items-center gap-3">
                      {/* View Details Deep Link */}
                      <Link
                        href={getFeatureCatalogUrl(item)}
                        className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors"
                      >
                        <Eye size={12} /> View Details & Catalog
                      </Link>

                      {item.media?.permalink && (
                        <a
                          href={item.media.permalink}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-[#636E72] hover:text-[#2A9D8F]"
                        >
                          Instagram Reel <ExternalLink size={11} />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Launchpad to Feature Tools */}
      <div>
        <h2 className="text-sm font-bold uppercase tracking-wider text-[#636E72] mb-3">
          Feature Analyzers & Diagnostic Tools
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href="/dashboard/analytics"
            className="p-5 rounded-2xl bg-white border border-gray-100 hover:border-[#2A9D8F] shadow-sm hover:shadow-md transition-all group flex items-start gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-[#2A9D8F]/10 text-[#2A9D8F] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <TrendingUp size={20} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#17212B] group-hover:text-[#2A9D8F] transition-colors">
                Instagram Analytics
              </h3>
              <p className="text-xs text-[#636E72] mt-1 leading-relaxed">
                Review reach, impressions, unfollow snapshots & engagement.
              </p>
            </div>
          </Link>

          <Link
            href="/dashboard/link-analyzer"
            className="p-5 rounded-2xl bg-white border border-gray-100 hover:border-[#2A9D8F] shadow-sm hover:shadow-md transition-all group flex items-start gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-[#A78BFA]/20 text-[#A78BFA] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <LinkIcon size={20} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#17212B] group-hover:text-[#2A9D8F] transition-colors">
                Broken Link Analyzer
              </h3>
              <p className="text-xs text-[#636E72] mt-1 leading-relaxed">
                Explore the Reels Link Catalog and scan promotional links.
              </p>
            </div>
          </Link>

          <Link
            href="/dashboard/audio-detector"
            className="p-5 rounded-2xl bg-white border border-gray-100 hover:border-[#2A9D8F] shadow-sm hover:shadow-md transition-all group flex items-start gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-[#E9B44C]/20 text-[#E9B44C] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <Volume2 size={20} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#17212B] group-hover:text-[#2A9D8F] transition-colors">
                Reel Audio Loss
              </h3>
              <p className="text-xs text-[#636E72] mt-1 leading-relaxed">
                Explore the Reels Audio Catalog and acoustic fingerprints.
              </p>
            </div>
          </Link>

          <Link
            href="/dashboard/lipsync"
            className="p-5 rounded-2xl bg-white border border-gray-100 hover:border-[#2A9D8F] shadow-sm hover:shadow-md transition-all group flex items-start gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-[#17212B]/10 text-[#17212B] flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
              <Mic size={20} />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#17212B] group-hover:text-[#2A9D8F] transition-colors">
                Lip-Sync Analyzer
              </h3>
              <p className="text-xs text-[#636E72] mt-1 leading-relaxed">
                Explore the Reels Lip-Sync Catalog and temporal delay scores.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
