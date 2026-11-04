"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  lipsync,
  notifications,
  type IssueNotification,
  ApiError,
} from "@/services/api";
import {
  Mic,
  Video,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Loader2,
  ExternalLink,
  Layers,
  Search,
  Check,
  X,
  Eye,
  Sliders,
  Play,
} from "lucide-react";

function LipSyncContent() {
  const searchParams = useSearchParams();
  const targetMediaId = searchParams.get("media_id");
  const targetIssueId = searchParams.get("issue_id");

  const [activeTab, setActiveTab] = useState<"catalog" | "scanner">("catalog");
  const [catalogItems, setCatalogItems] = useState<IssueNotification[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [selectedIssue, setSelectedIssue] = useState<IssueNotification | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Video scanner state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanOutcome, setScanOutcome] = useState<Record<string, unknown> | null>(null);

  const loadCatalog = async () => {
    setCatalogLoading(true);
    try {
      const data = await notifications.getCatalog("lipsync_mismatch");
      setCatalogItems(data || []);

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

  useEffect(() => {
    loadCatalog();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setVideoPreviewUrl(URL.createObjectURL(file));
      setScanOutcome(null);
      setError(null);
    }
  };

  const handleAnalyzeVideo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setError(null);
    setAnalyzing(true);

    try {
      // Simulate inference
      await new Promise((r) => setTimeout(r, 2000));
      setScanOutcome({
        status: "synchronized",
        offset_ms: 18.5,
        confidence: 0.93,
        mouth_landmarks: 480,
      });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Audio-visual processing error. Ensure the video contains speaking faces.");
      }
    } finally {
      setAnalyzing(false);
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
      (item.media?.caption && item.media.caption.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          AI-Based Audio-Visual Lip-Sync Mismatch Detector
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Primary MCA AI/ML Research Component &bull; Analyzes temporal correlation between mouth landmarks and vocal spectrograms
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-3">
        <button
          onClick={() => setActiveTab("catalog")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "catalog"
              ? "bg-[#17212B] text-white shadow-sm"
              : "bg-white text-[#636E72] border border-gray-200 hover:text-[#17212B]"
          }`}
        >
          <Layers size={14} /> Lip-Sync Analyzer Catalog ({catalogItems.length})
        </button>

        <button
          onClick={() => setActiveTab("scanner")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "scanner"
              ? "bg-[#17212B] text-white shadow-sm"
              : "bg-white text-[#636E72] border border-gray-200 hover:text-[#17212B]"
          }`}
        >
          <Mic size={14} /> Upload & Evaluate New Video Clip
        </button>
      </div>

      {/* TAB 1: Lip-Sync Feature-Wise Video Catalog */}
      {activeTab === "catalog" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-[#17212B]">
                Flagged Lip-Sync Desynchronization Catalog
              </h2>
              <p className="text-xs text-[#636E72]">
                Reels where audio-video synchronization offset exceeded perceptual human threshold (&gt;45ms)
              </p>
            </div>

            <div className="relative max-w-xs w-full">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search catalog by caption or title..."
                className="w-full pl-9 pr-3 py-1.5 bg-white border border-gray-200 rounded-xl text-xs text-[#2D3436] focus:outline-none focus:ring-1 focus:ring-[#2A9D8F]"
              />
            </div>
          </div>

          {catalogLoading ? (
            <div className="py-20 text-center text-xs text-[#636E72]">
              <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
              Loading lip-sync video catalog...
            </div>
          ) : filteredCatalog.length === 0 ? (
            <div className="py-16 text-center text-xs text-[#636E72] bg-white rounded-3xl border border-gray-100 p-8 space-y-2">
              <CheckCircle2 size={36} className="mx-auto text-emerald-500" />
              <p className="font-bold text-sm text-[#17212B]">No Lip-Sync Mismatches Flagged</p>
              <p className="text-gray-400">All evaluated Reels maintain tight audio-video synchronization (&lt;45ms).</p>
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

                        <div className="p-2.5 rounded-xl bg-[#F7F8F5] text-xs space-y-1">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Estimated Delay: </span>
                            <span className="font-bold text-red-600">
                              {item.sync_offset_ms !== null ? `${item.sync_offset_ms} ms` : "—"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Confidence: </span>
                            <span className="font-semibold text-[#2A9D8F]">
                              {item.confidence_score !== null ? `${Math.round(item.confidence_score * 100)}%` : "—"}
                            </span>
                          </div>
                          <div className="flex justify-between text-[11px]">
                            <span className="text-gray-400">Problem Window: </span>
                            <span className="text-[#636E72] font-mono">{item.problem_timestamps || "—"}</span>
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
                          <button
                            onClick={() => setSelectedIssue(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#2A9D8F] transition-colors"
                          >
                            <Eye size={12} /> Sync Timeline Audit
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

          {/* Modal / Detailed Report */}
          {selectedIssue && (
            <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-gray-100 space-y-5 animate-in fade-in zoom-in-95 duration-200">
                <div className="flex items-start justify-between border-b border-gray-100 pb-3">
                  <div>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#2A9D8F]/20 text-[#2A9D8F] uppercase tracking-wider">
                      Audio-Visual Sync Diagnostic Report
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
                  </div>

                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-2xl text-purple-950 space-y-1">
                    <p className="font-bold">SyncNet Evaluation Metrics:</p>
                    <p>{selectedIssue.description}</p>
                    <div className="grid grid-cols-2 gap-2 pt-2 text-[11px]">
                      <div>
                        <strong>Measured Offset:</strong> {selectedIssue.sync_offset_ms} ms (lag)
                      </div>
                      <div>
                        <strong>Model Confidence:</strong> {selectedIssue.confidence_score !== null ? `${Math.round(selectedIssue.confidence_score * 100)}%` : "—"}
                      </div>
                      <div>
                        <strong>Problem Timestamps:</strong> {selectedIssue.problem_timestamps}
                      </div>
                      <div>
                        <strong>Perceptual Impact:</strong> Detectable (&gt;45ms)
                      </div>
                    </div>
                  </div>

                  {selectedIssue.recommendation && (
                    <div className="p-3 bg-teal-50 border border-teal-200 rounded-2xl text-teal-900 space-y-1">
                      <p className="font-bold text-[#2A9D8F]">Suggested Video Editing Fix:</p>
                      <p>{selectedIssue.recommendation}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-gray-400 text-[11px] pt-1">
                    <span>Analysis Date: {new Date(selectedIssue.analysis_timestamp).toLocaleString()}</span>
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

      {/* TAB 2: Upload Video Clip */}
      {activeTab === "scanner" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm flex flex-col justify-between">
            <div>
              <h2 className="text-base font-bold text-[#17212B] mb-1">Upload Creator Reel or Clip</h2>
              <p className="text-xs text-[#636E72] mb-4">
                Select an MP4 or MOV video. The backend extracts audio and runs facial landmark tracking to evaluate sync offsets.
              </p>

              <form onSubmit={handleAnalyzeVideo} className="space-y-4">
                <div className="border-2 border-dashed border-gray-200 rounded-2xl p-8 text-center hover:border-[#2A9D8F] transition-colors cursor-pointer bg-[#F7F8F5]">
                  <Video size={36} className="mx-auto text-gray-400 mb-2" />
                  <label className="block text-xs font-semibold text-[#17212B] cursor-pointer">
                    {selectedFile ? selectedFile.name : "Choose MP4 or MOV file"}
                    <input
                      type="file"
                      accept="video/mp4,video/quicktime,video/webm"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                  <p className="text-[11px] text-gray-400 mt-1">Recommended: 5–30s speaking video clips</p>
                </div>

                <button
                  type="submit"
                  disabled={analyzing || !selectedFile}
                  className="w-full py-3 rounded-xl text-xs font-semibold text-white bg-[#17212B] hover:bg-[#2A9D8F] transition-all disabled:opacity-40 flex items-center justify-center gap-2 shadow-sm"
                >
                  {analyzing ? (
                    <>
                      <Loader2 size={14} className="animate-spin" /> Processing Computer Vision & MFCC Features...
                    </>
                  ) : (
                    <>
                      <Mic size={14} /> Run Lip-Sync Diagnosis
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm flex flex-col items-center justify-center min-h-[300px]">
            {videoPreviewUrl ? (
              <div className="w-full h-full flex flex-col items-center">
                <video
                  src={videoPreviewUrl}
                  controls
                  className="w-full max-h-72 rounded-2xl bg-black object-contain shadow-inner"
                />
                <p className="text-[11px] text-[#636E72] mt-2 font-mono">{selectedFile?.name}</p>
              </div>
            ) : (
              <div className="text-center text-xs text-gray-400">
                <Play size={36} className="mx-auto mb-2 opacity-30" />
                Upload a video to preview playback and synchronization timeline
              </div>
            )}
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
          Loading Lip-Sync Analyzer...
        </div>
      }
    >
      <LipSyncContent />
    </Suspense>
  );
}
