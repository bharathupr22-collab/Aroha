"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  links,
  notifications,
  type LinkReport,
  type IssueNotification,
  ApiError,
} from "@/services/api";
import {
  Link as LinkIcon,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Loader2,
  Download,
  Search,
  Clock,
  Sparkles,
  Layers,
  Filter,
  Check,
  X,
  Eye,
} from "lucide-react";

function LinkAnalyzerContent() {
  const searchParams = useSearchParams();
  const targetMediaId = searchParams.get("media_id");
  const targetIssueId = searchParams.get("issue_id");

  const [activeTab, setActiveTab] = useState<"catalog" | "scanner">(
    targetMediaId || targetIssueId ? "catalog" : "catalog"
  );
  const [catalogItems, setCatalogItems] = useState<IssueNotification[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [selectedIssue, setSelectedIssue] = useState<IssueNotification | null>(null);

  // Scanner state
  const [inputText, setInputText] = useState("");
  const [reports, setReports] = useState<LinkReport[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const loadCatalog = async () => {
    setCatalogLoading(true);
    try {
      const data = await notifications.getCatalog("broken_link");
      setCatalogItems(data || []);

      // If targeted by deep-link query parameter, automatically select & open
      if (targetIssueId) {
        const found = data.find((i) => i.id === Number(targetIssueId));
        if (found) setSelectedIssue(found);
      } else if (targetMediaId) {
        const found = data.find((i) => i.media_id === Number(targetMediaId));
        if (found) setSelectedIssue(found);
      }
    } catch {
      // empty
    } finally {
      setCatalogLoading(false);
    }
  };

  const loadReports = async () => {
    try {
      const data = await links.getReports();
      setReports(data || []);
    } catch {
      // empty
    }
  };

  useEffect(() => {
    loadCatalog();
    loadReports();
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setError(null);
    setLoading(true);

    try {
      const newReports = await links.analyze({ text: inputText });
      setInputText("");
      setReports((prev) => [...newReports, ...prev]);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to analyze promotional links. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleToggleResolve = async (issue: IssueNotification) => {
    try {
      const updated = issue.is_resolved
        ? await notifications.markUnresolved(issue.id)
        : await notifications.markResolved(issue.id);
      setCatalogItems((prev) => prev.map((i) => (i.id === issue.id ? updated : i)));
      if (selectedIssue && selectedIssue.id === issue.id) {
        setSelectedIssue(updated);
      }
    } catch {
      // error
    }
  };

  const filteredCatalog = catalogItems.filter((item) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      (item.detected_url && item.detected_url.toLowerCase().includes(q)) ||
      (item.media?.caption && item.media.caption.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          AI-Powered Broken Promotional Link Detector
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Detect expired affiliate offers, 404 landing pages, broken redirects, and malicious endpoints across Instagram Reels
        </p>
      </div>

      {/* Mode Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-3">
        <button
          onClick={() => setActiveTab("catalog")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "catalog"
              ? "bg-[#17212B] text-white shadow-sm"
              : "bg-white text-[#636E72] border border-gray-200 hover:text-[#17212B]"
          }`}
        >
          <Layers size={14} /> Broken Link Analyzer Catalog ({catalogItems.length})
        </button>

        <button
          onClick={() => setActiveTab("scanner")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "scanner"
              ? "bg-[#17212B] text-white shadow-sm"
              : "bg-white text-[#636E72] border border-gray-200 hover:text-[#17212B]"
          }`}
        >
          <LinkIcon size={14} /> Direct URL & Caption Scanner
        </button>
      </div>

      {/* TAB 1: Broken Link Feature-Wise Video Catalog */}
      {activeTab === "catalog" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-[#17212B]">
                Flagged Promotional Reels Catalog
              </h2>
              <p className="text-xs text-[#636E72]">
                Every Instagram Reel where broken, inaccessible or suspicious promotional links were identified
              </p>
            </div>

            <div className="relative max-w-xs w-full">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search catalog by URL or caption..."
                className="w-full pl-9 pr-3 py-1.5 bg-white border border-gray-200 rounded-xl text-xs text-[#2D3436] focus:outline-none focus:ring-1 focus:ring-[#2A9D8F]"
              />
            </div>
          </div>

          {catalogLoading ? (
            <div className="py-20 text-center text-xs text-[#636E72]">
              <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
              Loading broken link video catalog...
            </div>
          ) : filteredCatalog.length === 0 ? (
            <div className="py-16 text-center text-xs text-[#636E72] bg-white rounded-3xl border border-gray-100 p-8 space-y-2">
              <CheckCircle2 size={36} className="mx-auto text-emerald-500" />
              <p className="font-bold text-sm text-[#17212B]">No Broken Links Flagged</p>
              <p className="text-gray-400">All scanned promotional links in creator Reels are verified healthy.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredCatalog.map((item) => {
                const isSelected = selectedIssue?.id === item.id;
                return (
                  <div
                    key={item.id}
                    id={`issue-${item.id}`}
                    className={`p-5 rounded-3xl bg-white border transition-all ${
                      isSelected
                        ? "border-[#2A9D8F] shadow-lg ring-2 ring-[#2A9D8F]/30"
                        : "border-gray-100 shadow-sm hover:shadow-md"
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Reel Thumbnail */}
                      <div className="relative w-24 h-28 rounded-2xl overflow-hidden bg-gray-100 shrink-0 border border-gray-200 shadow-inner">
                        {item.media?.thumbnail_url ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={item.media.thumbnail_url}
                            alt="Reel Preview"
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

                      {/* Info */}
                      <div className="flex-1 min-w-0 space-y-2">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-[10px] font-mono text-gray-400">
                            {item.media?.platform_media_id || `Reel #${item.media_id || item.id}`}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                              item.is_resolved
                                ? "bg-emerald-50 text-emerald-700"
                                : "bg-red-50 text-red-700"
                            }`}
                          >
                            {item.is_resolved ? "Resolved" : "Unresolved"}
                          </span>
                        </div>

                        <h3 className="font-bold text-sm text-[#17212B] line-clamp-1">{item.title}</h3>

                        {item.media?.caption && (
                          <p className="text-xs text-[#636E72] line-clamp-2 italic">
                            &ldquo;{item.media.caption}&rdquo;
                          </p>
                        )}

                        <div className="p-2.5 rounded-xl bg-[#F7F8F5] text-xs font-mono space-y-1">
                          <div className="truncate">
                            <span className="text-gray-400">URL: </span>
                            <span className="text-red-600 font-semibold">{item.detected_url}</span>
                          </div>
                          <div>
                            <span className="text-gray-400">HTTP: </span>
                            <span className="text-[#17212B] font-bold">
                              {item.http_status ? `HTTP ${item.http_status}` : "Unreachable"}
                            </span>
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
                          <button
                            onClick={() => setSelectedIssue(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors"
                          >
                            <Eye size={12} /> Full Analysis Report
                          </button>

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
                );
              })}
            </div>
          )}

          {/* Modal / Detailed Report for Selected Reel Issue */}
          {selectedIssue && (
            <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-gray-100 space-y-5 animate-in fade-in zoom-in-95 duration-200">
                <div className="flex items-start justify-between border-b border-gray-100 pb-3">
                  <div>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#A78BFA]/20 text-[#A78BFA] uppercase tracking-wider">
                      Broken Promotional Link Audit
                    </span>
                    <h3 className="text-lg font-bold text-[#17212B] mt-1">{selectedIssue.title}</h3>
                  </div>
                  <button
                    onClick={() => setSelectedIssue(null)}
                    className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <span className="font-semibold text-gray-500">Affected Instagram Reel:</span>
                    <p className="mt-1 font-mono text-[11px] text-[#17212B]">
                      {selectedIssue.media?.platform_media_id} &bull;{" "}
                      {selectedIssue.media?.permalink && (
                        <a
                          href={selectedIssue.media.permalink}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[#2A9D8F] underline inline-flex items-center gap-1"
                        >
                          Open on Instagram <ExternalLink size={10} />
                        </a>
                      )}
                    </p>
                    {selectedIssue.media?.caption && (
                      <p className="mt-1 text-gray-600 italic bg-gray-50 p-2 rounded-xl">
                        &ldquo;{selectedIssue.media.caption}&rdquo;
                      </p>
                    )}
                  </div>

                  <div className="p-3 bg-red-50 border border-red-200 rounded-2xl text-red-900 space-y-1">
                    <p className="font-bold">Diagnostic Problem Details:</p>
                    <p>{selectedIssue.description}</p>
                    <div className="pt-1 font-mono text-[11px] text-red-700">
                      <strong>Flagged URL:</strong> {selectedIssue.detected_url}
                      <br />
                      <strong>Response Code:</strong> {selectedIssue.http_status ? `HTTP ${selectedIssue.http_status}` : "Connection Refused / DNS Error"}
                    </div>
                  </div>

                  {selectedIssue.recommendation && (
                    <div className="p-3 bg-teal-50 border border-teal-200 rounded-2xl text-teal-900 space-y-1">
                      <p className="font-bold text-[#2A9D8F]">Suggested Creator Correction:</p>
                      <p>{selectedIssue.recommendation}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-gray-400 text-[11px] pt-1">
                    <span>Audit Date: {new Date(selectedIssue.analysis_timestamp).toLocaleString()}</span>
                    <span>Status: {selectedIssue.is_resolved ? "Resolved" : "Unresolved"}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <button
                    onClick={() => handleToggleResolve(selectedIssue)}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                      selectedIssue.is_resolved
                        ? "bg-gray-100 text-[#636E72] hover:bg-gray-200"
                        : "bg-emerald-600 text-white hover:bg-emerald-700"
                    }`}
                  >
                    <Check size={14} /> {selectedIssue.is_resolved ? "Mark Unresolved" : "Mark as Resolved"}
                  </button>

                  <button
                    onClick={() => setSelectedIssue(null)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-100"
                  >
                    Close Report
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Direct Scanner */}
      {activeTab === "scanner" && (
        <div className="space-y-6">
          <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-[#17212B]">Direct Text or Caption Scanner</h2>
            <p className="text-xs text-[#636E72]">
              Paste promotional captions or raw URLs. Our SSRF-safe engine extracts and validates all links.
            </p>

            {error && (
              <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
                <AlertTriangle size={16} className="shrink-0 text-red-600" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleAnalyze} className="space-y-4">
              <textarea
                rows={4}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="e.g. Check my bio link https://mybrand.shop/discount or use coupon code on https://affiliate.example.com/promo"
                className="w-full p-4 bg-[#F7F8F5] border border-gray-200 rounded-2xl text-xs text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F]"
              />

              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-1">
                <div className="flex items-center gap-2 text-xs text-[#636E72]">
                  <ShieldCheck size={16} className="text-[#2A9D8F]" />
                  <span>Protected with Server-Side Request Forgery (SSRF) verification</span>
                </div>

                <button
                  type="submit"
                  disabled={loading || !inputText.trim()}
                  className="px-6 py-2.5 rounded-xl text-xs font-semibold text-white bg-[#2A9D8F] hover:bg-[#238478] shadow-sm transition-all flex items-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader2 size={14} className="animate-spin" /> Validating Links...
                    </>
                  ) : (
                    <>
                      <LinkIcon size={14} /> Analyze Links
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Past Raw Reports */}
          <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-4">
            <h2 className="text-base font-bold text-[#17212B]">Raw Link Inspection History</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-gray-200 text-[#636E72] font-semibold">
                    <th className="py-3 px-3">Target URL</th>
                    <th className="py-3 px-3">HTTP Status</th>
                    <th className="py-3 px-3">Result</th>
                    <th className="py-3 px-3">Diagnostic Notes</th>
                    <th className="py-3 px-3">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {reports.map((report) => (
                    <tr key={report.id} className="hover:bg-gray-50/60">
                      <td className="py-3 px-3 max-w-xs truncate font-semibold text-[#17212B]">
                        {report.detected_url}
                      </td>
                      <td className="py-3 px-3">
                        {report.response_status ? `HTTP ${report.response_status}` : "N/A"}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            report.validation_result === "working"
                              ? "bg-emerald-50 text-emerald-700"
                              : "bg-red-50 text-red-700"
                          }`}
                        >
                          {report.validation_result}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-[#636E72] max-w-sm truncate">
                        {report.issue_description || "—"}
                      </td>
                      <td className="py-3 px-3 text-gray-400 text-[11px]">
                        {new Date(report.checked_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function LinkAnalyzerPage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-xs text-[#636E72]">
          <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
          Loading Link Analyzer...
        </div>
      }
    >
      <LinkAnalyzerContent />
    </Suspense>
  );
}
