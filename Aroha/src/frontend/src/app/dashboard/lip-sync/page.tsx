"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  notifications,
  type IssueNotification,
} from "@/services/api";
import {
  Mic,
  Video,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Loader2,
  Search,
  RefreshCw,
  X,
  Eye,
  BellRing,
  ShieldAlert,
  ShieldCheck,
  RotateCcw,
  Clock,
  Sliders,
  Layers,
} from "lucide-react";

function LipSyncContent() {
  const searchParams = useSearchParams();
  const targetMediaId = searchParams.get("media_id");
  const targetIssueId = searchParams.get("issue_id");

  const [catalogItems, setCatalogItems] = useState<IssueNotification[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [scanningProfile, setScanningProfile] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<IssueNotification | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "unresolved" | "resolved">("all");
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  const loadCatalog = async () => {
    setCatalogLoading(true);
    try {
      const data = await notifications.getCatalog("lipsync_mismatch");
      const items = data || [];
      setCatalogItems(items);

      if (targetIssueId) {
        const found = items.find((i) => i.id === Number(targetIssueId));
        if (found) {
          setSelectedIssue(found);
          if (!found.is_read) {
            notifications.markRead(found.id).catch(() => {});
          }
        }
      } else if (targetMediaId) {
        const found = items.find((i) => i.media_id === Number(targetMediaId));
        if (found) {
          setSelectedIssue(found);
          if (!found.is_read) {
            notifications.markRead(found.id).catch(() => {});
          }
        }
      }
    } catch {
      // ignore error
    } finally {
      setCatalogLoading(false);
    }
  };

  useEffect(() => {
    loadCatalog();
  }, [targetIssueId, targetMediaId]);

  const handleProfileRescan = async () => {
    setScanningProfile(true);
    try {
      await notifications.triggerScan();
      await loadCatalog();
    } catch {
      // ignore error
    } finally {
      setScanningProfile(false);
    }
  };

  const handleOpenIssue = (item: IssueNotification) => {
    setSelectedIssue(item);
    if (!item.is_read) {
      notifications.markRead(item.id).catch(() => {});
      setCatalogItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, is_read: true } : i))
      );
    }
  };

  const handleToggleResolve = async (issueId: number, currentlyResolved: boolean) => {
    setActionLoadingId(issueId);
    try {
      if (currentlyResolved) {
        await notifications.markUnresolved(issueId);
      } else {
        await notifications.markResolved(issueId);
      }
      setCatalogItems((prev) =>
        prev.map((i) =>
          i.id === issueId ? { ...i, is_resolved: !currentlyResolved } : i
        )
      );
      if (selectedIssue && selectedIssue.id === issueId) {
        setSelectedIssue((prev) =>
          prev ? { ...prev, is_resolved: !currentlyResolved } : null
        );
      }
    } catch {
      // ignore error
    } finally {
      setActionLoadingId(null);
    }
  };

  const filteredCatalog = catalogItems.filter((item) => {
    if (statusFilter === "unresolved" && item.is_resolved) return false;
    if (statusFilter === "resolved" && !item.is_resolved) return false;

    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      (item.media?.caption && item.media.caption.toLowerCase().includes(q)) ||
      (item.media?.platform_media_id && item.media.platform_media_id.toLowerCase().includes(q)) ||
      (item.description && item.description.toLowerCase().includes(q))
    );
  });

  const unresolvedCount = catalogItems.filter((i) => !i.is_resolved).length;
  const resolvedCount = catalogItems.filter((i) => i.is_resolved).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#A78BFA]/15 text-[#6D28D9] text-[11px] font-bold mb-2">
            <BellRing size={12} /> Automated Audio-Visual Sync Monitor
          </div>
          <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
            Lip-Sync Mismatch & AV Drift Catalog
          </h1>
          <p className="text-xs text-[#636E72] mt-1">
            Automatically analyzes audio-video timing drift, viseme lip motion desynchronization, and post-transcoding latency across your connected Instagram Reels.
          </p>
        </div>

        <button
          onClick={handleProfileRescan}
          disabled={scanningProfile || catalogLoading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors disabled:opacity-50 shrink-0"
        >
          <RefreshCw size={14} className={scanningProfile ? "animate-spin" : ""} />
          {scanningProfile ? "Auditing Reel Lip-Sync..." : "Sync & Scan Connected Profile"}
        </button>
      </div>

      {/* Catalog Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-purple-50 text-purple-600">
            <Mic size={18} />
          </div>
          <div>
            <h2 className="text-base font-bold text-[#17212B]">
              Flagged Lip-Sync Desyncs ({filteredCatalog.length})
            </h2>
            <p className="text-xs text-[#636E72]">
              Read-only SyncNet temporal viseme diagnostic alerts from your connected Instagram profile
            </p>
          </div>
        </div>

        {/* Filter Pills & Search */}
        <div className="flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="inline-flex p-1 bg-gray-100 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setStatusFilter("all")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                statusFilter === "all"
                  ? "bg-white text-[#17212B] shadow-sm font-bold"
                  : "text-[#636E72] hover:text-[#17212B]"
              }`}
            >
              All ({catalogItems.length})
            </button>
            <button
              onClick={() => setStatusFilter("unresolved")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                statusFilter === "unresolved"
                  ? "bg-white text-red-600 shadow-sm font-bold"
                  : "text-[#636E72] hover:text-red-600"
              }`}
            >
              Unresolved ({unresolvedCount})
            </button>
            <button
              onClick={() => setStatusFilter("resolved")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                statusFilter === "resolved"
                  ? "bg-white text-emerald-600 shadow-sm font-bold"
                  : "text-[#636E72] hover:text-emerald-600"
              }`}
            >
              Resolved ({resolvedCount})
            </button>
          </div>

          <div className="relative w-full sm:w-64">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by caption or drift..."
              className="w-full pl-9 pr-3 py-2 bg-white border border-gray-200 rounded-xl text-xs text-[#2D3436] focus:outline-none focus:ring-1 focus:ring-[#2A9D8F]"
            />
          </div>
        </div>
      </div>

      {/* Catalog Grid */}
      {catalogLoading ? (
        <div className="py-20 text-center text-xs text-[#636E72]">
          <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
          Auditing connected Instagram Reels for audio-video drift and lip desynchronization...
        </div>
      ) : filteredCatalog.length === 0 ? (
        <div className="py-16 text-center text-xs text-[#636E72] bg-white rounded-3xl border border-gray-100 p-8 space-y-2">
          <CheckCircle2 size={36} className="mx-auto text-emerald-500" />
          <p className="font-bold text-sm text-[#17212B]">
            {statusFilter === "resolved"
              ? "No Resolved Lip-Sync Issues"
              : "No Lip-Sync Mismatches Detected"}
          </p>
          <p className="text-gray-400">
            {statusFilter === "resolved"
              ? "You haven't marked any lip-sync drift alerts as resolved yet."
              : "All dialogue and speech tracks across your connected Instagram Reels are perfectly synchronized within perceptual tolerances."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCatalog.map((item) => {
            const isSelected = selectedIssue?.id === item.id;
            const offset = item.sync_offset_ms || 0;

            return (
              <div
                key={item.id}
                id={`issue-${item.id}`}
                className={`p-5 rounded-3xl bg-white border transition-all ${
                  isSelected
                    ? "border-[#2A9D8F] shadow-lg ring-2 ring-[#2A9D8F]/30"
                    : item.is_resolved
                    ? "border-emerald-100 shadow-sm bg-emerald-50/10"
                    : "border-gray-100 shadow-sm hover:shadow-md"
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Reel Thumbnail Preview */}
                  <div className="relative w-24 h-28 rounded-2xl overflow-hidden bg-gray-100 shrink-0 border border-gray-200 shadow-inner">
                    {item.media?.thumbnail_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={item.media.thumbnail_url}
                        alt="Reel Preview"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400 text-[10px] text-center p-2">
                        Instagram Reel
                      </div>
                    )}
                    <span className="absolute bottom-1 right-1 px-1.5 py-0.5 rounded bg-black/70 text-[9px] text-white font-mono uppercase">
                      REEL
                    </span>
                  </div>

                  {/* Notification Details */}
                  <div className="flex-1 min-w-0 space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-mono text-gray-400">
                        {item.media?.platform_media_id || `Media #${item.media_id || item.id}`}
                      </span>
                      {item.is_resolved ? (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-50 text-emerald-700 inline-flex items-center gap-1">
                          <CheckCircle2 size={10} /> Resolved
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-purple-50 text-purple-700 inline-flex items-center gap-1">
                          <AlertTriangle size={10} /> AV Drift Flagged
                        </span>
                      )}
                    </div>

                    <h3 className="font-bold text-sm text-[#17212B] line-clamp-1">
                      {item.title}
                    </h3>

                    {item.media?.caption && (
                      <p className="text-xs text-[#636E72] line-clamp-2 italic">
                        “{item.media.caption}”
                      </p>
                    )}

                    <div className="p-2.5 rounded-xl bg-[#F7F8F5] text-xs font-mono space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-400">Estimated Delay:</span>
                        <span className="font-bold text-purple-700">
                          {item.sync_offset_ms !== null
                            ? `${offset > 0 ? "+" : ""}${offset.toFixed(1)} ms`
                            : "Measurable AV Drift"}
                        </span>
                      </div>
                      {item.confidence_score !== null && (
                        <div className="flex items-center justify-between">
                          <span className="text-gray-400">SyncNet Confidence:</span>
                          <span className="font-bold text-[#17212B]">
                            {(item.confidence_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
                      <button
                        onClick={() => handleOpenIssue(item)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors"
                      >
                        <Eye size={12} /> View Diagnostic Details
                      </button>

                      {item.media?.permalink && (
                        <a
                          href={item.media.permalink}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-[#636E72] hover:text-[#2A9D8F]"
                        >
                          View on Instagram <ExternalLink size={11} />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Read-Only Diagnostic Notification Modal */}
      {selectedIssue && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-gray-100 space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-gray-100 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-800 uppercase tracking-wider">
                    Lip-Sync Temporal Drift Alert
                  </span>
                  {selectedIssue.is_resolved ? (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 uppercase">
                      Resolved
                    </span>
                  ) : (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 uppercase">
                      Unresolved
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-bold text-[#17212B] mt-1">{selectedIssue.title}</h3>
              </div>
              <button
                onClick={() => setSelectedIssue(null)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-3.5 text-xs">
              {/* Reel Metadata */}
              <div>
                <span className="font-semibold text-gray-500">Flagged Instagram Reel:</span>
                <p className="mt-1 font-mono text-[11px] text-[#17212B]">
                  {selectedIssue.media?.platform_media_id || `Media #${selectedIssue.media_id}`}{" "}
                  {selectedIssue.media?.permalink && (
                    <>
                      •{" "}
                      <a
                        href={selectedIssue.media.permalink}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[#2A9D8F] underline inline-flex items-center gap-1 font-sans"
                      >
                        Open Reel on Instagram <ExternalLink size={10} />
                      </a>
                    </>
                  )}
                </p>
                {selectedIssue.media?.caption && (
                  <p className="mt-1 text-gray-600 italic bg-gray-50 p-2.5 rounded-xl">
                    “{selectedIssue.media.caption}”
                  </p>
                )}
              </div>

              {/* Lip-Sync Analysis Diagnostic Box */}
              <div className="p-4 bg-purple-50/60 border border-purple-200 rounded-2xl text-[#17212B] space-y-3">
                <div className="flex items-center gap-2 font-bold text-purple-900">
                  <ShieldAlert size={16} />
                  <span>Audio-Visual Viseme Temporal Analysis:</span>
                </div>
                <p className="text-gray-700 leading-relaxed">{selectedIssue.description}</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1 text-xs">
                  <div className="p-2.5 bg-white rounded-xl border border-purple-100">
                    <span className="text-[10px] text-gray-400 uppercase font-mono block">
                      Estimated Temporal Drift
                    </span>
                    <span className="font-bold text-purple-700 text-sm">
                      {selectedIssue.sync_offset_ms !== null
                        ? `${selectedIssue.sync_offset_ms > 0 ? "+" : ""}${selectedIssue.sync_offset_ms.toFixed(1)} ms`
                        : "Measurable Delay"}
                    </span>
                  </div>

                  <div className="p-2.5 bg-white rounded-xl border border-purple-100">
                    <span className="text-[10px] text-gray-400 uppercase font-mono block">
                      Perceptual Limit Check
                    </span>
                    <span className="font-bold text-red-600">
                      Exceeds ±45 ms Human Threshold
                    </span>
                  </div>
                </div>

                {/* Confidence Score Bar */}
                {selectedIssue.confidence_score !== null && (
                  <div className="p-2.5 bg-white rounded-xl border border-purple-100 space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-gray-500 font-medium">SyncNet Temporal Confidence:</span>
                      <span className="font-mono font-bold text-[#17212B]">
                        {(selectedIssue.confidence_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-600 rounded-full transition-all"
                        style={{ width: `${Math.max(selectedIssue.confidence_score * 100, 5)}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Problem Timestamps */}
                {selectedIssue.problem_timestamps && (
                  <div className="p-2.5 bg-white rounded-xl border border-purple-100 text-[11px] flex items-center justify-between">
                    <span className="text-gray-500 font-medium">Problem Video Segment:</span>
                    <span className="font-mono font-bold text-[#17212B]">
                      {selectedIssue.problem_timestamps}
                    </span>
                  </div>
                )}
              </div>

              {/* Advisory Recommendations */}
              {selectedIssue.recommendation && (
                <div className="p-3.5 bg-teal-50 border border-teal-200 rounded-2xl text-teal-900 space-y-1">
                  <p className="font-bold text-[#2A9D8F] flex items-center gap-1">
                    <ShieldCheck size={14} /> Notification Advisory:
                  </p>
                  <p>{selectedIssue.recommendation}</p>
                </div>
              )}

              {/* Detection Timestamps */}
              <div className="flex items-center justify-between text-gray-400 text-[11px] pt-1">
                <span className="flex items-center gap-1">
                  <Clock size={11} /> Detected: {new Date(selectedIssue.analysis_timestamp).toLocaleString()}
                </span>
                <span>Last Checked: {new Date(selectedIssue.last_checked_at).toLocaleString()}</span>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-gray-100">
              <button
                onClick={() => handleToggleResolve(selectedIssue.id, selectedIssue.is_resolved)}
                disabled={actionLoadingId === selectedIssue.id}
                className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-colors ${
                  selectedIssue.is_resolved
                    ? "bg-amber-50 text-amber-800 hover:bg-amber-100"
                    : "bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                }`}
              >
                {actionLoadingId === selectedIssue.id ? (
                  <Loader2 size={13} className="animate-spin" />
                ) : selectedIssue.is_resolved ? (
                  <RotateCcw size={13} />
                ) : (
                  <CheckCircle2 size={13} />
                )}
                {selectedIssue.is_resolved ? "Reopen Issue" : "Mark as Resolved"}
              </button>

              <button
                onClick={() => setSelectedIssue(null)}
                className="px-5 py-2 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors"
              >
                Close Notification
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function LipSyncPage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-xs text-[#636E72]">
          <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
          Loading Lip-Sync Drift Notifications...
        </div>
      }
    >
      <LipSyncContent />
    </Suspense>
  );
}

