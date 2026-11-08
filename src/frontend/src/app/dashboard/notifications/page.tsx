"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  notifications,
  type IssueNotification,
  type NotificationSummary,
  ApiError,
} from "@/services/api";
import {
  Bell,
  Link as LinkIcon,
  Volume2,
  Mic,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Loader2,
  RefreshCw,
  Eye,
  Check,
  X,
  Sparkles,
  ArrowRight,
  ShieldAlert,
  Clock,
} from "lucide-react";

type FilterStatus = "all" | "broken_link" | "audio_loss" | "lipsync_mismatch" | "unread" | "resolved" | "unresolved";

export default function NotificationsPage() {
  const [items, setItems] = useState<IssueNotification[]>([]);
  const [summary, setSummary] = useState<NotificationSummary | null>(null);
  const [filter, setFilter] = useState<FilterStatus>("all");
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [scanMessage, setScanMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [notifsRes, summaryRes] = await Promise.all([
        notifications.getNotifications(),
        notifications.getSummary(),
      ]);
      setItems(notifsRes || []);
      setSummary(summaryRes);
    } catch {
      // empty
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleScan = async () => {
    setScanning(true);
    setError(null);
    setScanMessage(null);
    try {
      const res = await notifications.triggerScan();
      setScanMessage(
        `Audit complete: Audited ${res.audited_media_count} Reels. Detected ${res.new_issues_detected} new issue(s), updated ${res.existing_issues_updated} existing.`
      );
      await loadData();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to run media integrity audit.");
      }
    } finally {
      setScanning(false);
    }
  };

  const handleMarkRead = async (id: number) => {
    setActionLoadingId(id);
    try {
      const updated = await notifications.markRead(id);
      setItems((prev) => prev.map((item) => (item.id === id ? updated : item)));
      if (summary) {
        setSummary({ ...summary, unread_count: Math.max(0, summary.unread_count - 1) });
      }
    } catch {
      // error
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleToggleResolve = async (item: IssueNotification) => {
    setActionLoadingId(item.id);
    try {
      const updated = item.is_resolved
        ? await notifications.markUnresolved(item.id)
        : await notifications.markResolved(item.id);
      setItems((prev) => prev.map((i) => (i.id === item.id ? updated : i)));
      const s = await notifications.getSummary();
      setSummary(s);
    } catch {
      // error
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDismiss = async (id: number) => {
    setActionLoadingId(id);
    try {
      await notifications.dismiss(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
      const s = await notifications.getSummary();
      setSummary(s);
    } catch {
      // error
    } finally {
      setActionLoadingId(null);
    }
  };

  // Filter items
  const filteredItems = items.filter((item) => {
    if (filter === "all") return true;
    if (filter === "broken_link") return item.issue_category === "broken_link";
    if (filter === "audio_loss") return item.issue_category === "audio_loss";
    if (filter === "lipsync_mismatch") return item.issue_category === "lipsync_mismatch";
    if (filter === "unread") return !item.is_read;
    if (filter === "resolved") return item.is_resolved;
    if (filter === "unresolved") return !item.is_resolved;
    return true;
  });

  const getCategoryBadge = (category: string) => {
    switch (category) {
      case "broken_link":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#A78BFA]/20 text-[#A78BFA] uppercase tracking-wider">
            <LinkIcon size={11} /> Broken Promotional Link
          </span>
        );
      case "audio_loss":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#E9B44C]/20 text-[#E9B44C] uppercase tracking-wider">
            <Volume2 size={11} /> Audio Loss / Change
          </span>
        );
      case "lipsync_mismatch":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#2A9D8F]/20 text-[#2A9D8F] uppercase tracking-wider">
            <Mic size={11} /> Lip-Sync Mismatch
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-gray-100 text-gray-600 uppercase">
            {category}
          </span>
        );
    }
  };

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
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
            Centralized Dashboard Notifications & Issue Monitor
          </h1>
          <p className="text-xs text-[#636E72] mt-1">
            Real-time notifications pinpointing exact affected Instagram Reels across links, audio tracks & lip-sync
          </p>
        </div>

        <button
          onClick={handleScan}
          disabled={scanning}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#2A9D8F] hover:bg-[#238478] shadow-sm transition-all disabled:opacity-50 self-start md:self-auto"
        >
          {scanning ? (
            <>
              <Loader2 size={14} className="animate-spin" /> Auditing Reels Content...
            </>
          ) : (
            <>
              <Sparkles size={14} /> Run Media Integrity Audit
            </>
          )}
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertTriangle size={16} className="shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}
      {scanMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle2 size={16} className="shrink-0 text-emerald-600" />
          <span>{scanMessage}</span>
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-[11px] font-semibold text-[#636E72] uppercase">Total Issues</span>
          <p className="text-xl font-bold text-[#17212B] mt-1">{summary?.total_issues ?? 0}</p>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-[11px] font-semibold text-[#636E72] uppercase">Broken Links</span>
          <p className="text-xl font-bold text-[#A78BFA] mt-1">{summary?.broken_link_issues ?? 0}</p>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-[11px] font-semibold text-[#636E72] uppercase">Audio Issues</span>
          <p className="text-xl font-bold text-[#E9B44C] mt-1">{summary?.audio_issues ?? 0}</p>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-[11px] font-semibold text-[#636E72] uppercase">Lip-Sync Issues</span>
          <p className="text-xl font-bold text-[#2A9D8F] mt-1">{summary?.lipsync_issues ?? 0}</p>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-[11px] font-semibold text-red-600 uppercase">Unresolved</span>
          <p className="text-xl font-bold text-red-600 mt-1">{summary?.unresolved_issues ?? 0}</p>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-[11px] font-semibold text-emerald-600 uppercase">Resolved</span>
          <p className="text-xl font-bold text-emerald-600 mt-1">{summary?.resolved_issues ?? 0}</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-gray-200 pb-3">
        {[
          { id: "all", label: "All Issues" },
          { id: "broken_link", label: "Broken Links" },
          { id: "audio_loss", label: "Audio Issues" },
          { id: "lipsync_mismatch", label: "Lip-Sync Issues" },
          { id: "unread", label: "Unread" },
          { id: "unresolved", label: "Unresolved" },
          { id: "resolved", label: "Resolved" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id as FilterStatus)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              filter === tab.id
                ? "bg-[#17212B] text-white shadow-sm"
                : "bg-white text-[#636E72] border border-gray-200 hover:text-[#17212B]"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Notifications Feed */}
      {loading ? (
        <div className="py-20 text-center text-xs text-[#636E72]">
          <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
          Loading notifications...
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="py-16 text-center text-xs text-[#636E72] bg-white rounded-3xl border border-gray-100 p-8 space-y-3">
          <CheckCircle2 size={36} className="mx-auto text-emerald-500" />
          <p className="font-bold text-sm text-[#17212B]">No issues in this view</p>
          <p className="max-w-md mx-auto text-gray-400">
            Click &ldquo;Run Media Integrity Audit&rdquo; above to inspect Instagram content for link, audio, and sync anomalies.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className={`p-5 rounded-3xl bg-white border transition-all ${
                !item.is_read
                  ? "border-[#2A9D8F]/40 shadow-md ring-1 ring-[#2A9D8F]/20"
                  : "border-gray-100 shadow-sm"
              } ${item.is_resolved ? "opacity-75 bg-gray-50/50" : ""}`}
            >
              <div className="flex flex-col sm:flex-row items-start gap-4">
                {/* Reel Thumbnail */}
                <div className="relative w-24 h-24 rounded-2xl overflow-hidden bg-gray-100 shrink-0 border border-gray-200 shadow-inner">
                  {item.media?.thumbnail_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={item.media.thumbnail_url}
                      alt="Reel Thumbnail"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                      No Preview
                    </div>
                  )}
                  <span className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/70 text-[9px] text-white font-mono">
                    REEL
                  </span>
                </div>

                {/* Issue Details */}
                <div className="flex-1 min-w-0 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {getCategoryBadge(item.issue_category)}
                      {!item.is_read && (
                        <span className="w-2 h-2 rounded-full bg-[#2A9D8F]" title="Unread notification" />
                      )}
                      {item.is_resolved ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Resolved
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-200">
                          Unresolved
                        </span>
                      )}
                    </div>

                    <span className="text-[11px] text-gray-400 flex items-center gap-1">
                      <Clock size={12} /> {new Date(item.analysis_timestamp).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Reel Identification & Title */}
                  <div>
                    <h3 className="text-sm font-bold text-[#17212B] flex items-center gap-2">
                      {item.title}
                    </h3>
                    {item.media?.caption && (
                      <p className="text-xs text-[#636E72] mt-0.5 line-clamp-1 italic">
                        &ldquo;{item.media.caption}&rdquo;
                      </p>
                    )}
                  </div>

                  {/* Diagnostic Context based on Issue Category */}
                  <div className="p-3 rounded-2xl bg-[#F7F8F5] border border-gray-200/60 text-xs space-y-1.5 text-[#2D3436]">
                    <p className="text-xs leading-relaxed">{item.description}</p>

                    {item.issue_category === "broken_link" && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                        <div>
                          <span className="text-gray-400">Target URL: </span>
                          <span className="text-red-600 font-semibold truncate block">
                            {item.detected_url}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Response Status: </span>
                          <span className="font-semibold text-[#17212B]">
                            {item.http_status ? `HTTP ${item.http_status}` : "Unreachable"}
                          </span>
                        </div>
                      </div>
                    )}

                    {item.issue_category === "audio_loss" && (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 text-[11px]">
                        <div>
                          <span className="text-gray-400">Status: </span>
                          <span className="font-semibold text-red-600">{item.audio_status}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Similarity: </span>
                          <span className="font-semibold text-[#17212B]">
                            {item.similarity_score !== null ? `${Math.round(item.similarity_score * 100)}%` : "N/A"}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Reference: </span>
                          <span className="text-[#636E72]">{item.previous_audio_ref || "None"}</span>
                        </div>
                      </div>
                    )}

                    {item.issue_category === "lipsync_mismatch" && (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 text-[11px]">
                        <div>
                          <span className="text-gray-400">Estimated Delay: </span>
                          <span className="font-semibold text-red-600">
                            {item.sync_offset_ms !== null ? `${item.sync_offset_ms} ms` : "—"}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Confidence: </span>
                          <span className="font-semibold text-[#2A9D8F]">
                            {item.confidence_score !== null ? `${Math.round(item.confidence_score * 100)}%` : "—"}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">Problem Window: </span>
                          <span className="text-[#636E72]">{item.problem_timestamps || "—"}</span>
                        </div>
                      </div>
                    )}

                    {item.recommendation && (
                      <p className="text-[11px] text-[#2A9D8F] pt-1">
                        <strong>Remediation:</strong> {item.recommendation}
                      </p>
                    )}
                  </div>

                  {/* Actions & Deep Links */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                    <div className="flex items-center gap-3">
                      {/* Deep Link to Feature Catalog */}
                      <Link
                        href={getFeatureCatalogUrl(item)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors shadow-sm"
                      >
                        <Eye size={13} /> View in Feature Catalog
                      </Link>

                      {/* External Instagram Link */}
                      {item.media?.permalink && (
                        <a
                          href={item.media.permalink}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-[#636E72] hover:text-[#2A9D8F] transition-colors"
                        >
                          Instagram Reel <ExternalLink size={12} />
                        </a>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {!item.is_read && (
                        <button
                          onClick={() => handleMarkRead(item.id)}
                          disabled={actionLoadingId === item.id}
                          className="px-2.5 py-1 rounded-lg text-[11px] font-semibold text-[#636E72] hover:bg-gray-100 transition-colors"
                        >
                          Mark as Read
                        </button>
                      )}

                      <button
                        onClick={() => handleToggleResolve(item)}
                        disabled={actionLoadingId === item.id}
                        className={`inline-flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                          item.is_resolved
                            ? "bg-gray-100 text-[#636E72] hover:bg-gray-200"
                            : "bg-emerald-50 text-emerald-700 hover:bg-emerald-100"
                        }`}
                      >
                        <Check size={12} /> {item.is_resolved ? "Mark Unresolved" : "Mark Resolved"}
                      </button>

                      <button
                        onClick={() => handleDismiss(item.id)}
                        disabled={actionLoadingId === item.id}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                        title="Dismiss notification"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
