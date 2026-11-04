"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  audio,
  notifications,
  type AudioReport,
  type IssueNotification,
  ApiError,
} from "@/services/api";
import {
  Volume2,
  VolumeX,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  FileAudio,
  Sparkles,
  ExternalLink,
  Layers,
  Search,
  Check,
  X,
  Eye,
  Clock,
} from "lucide-react";

function AudioDetectorContent() {
  const searchParams = useSearchParams();
  const targetMediaId = searchParams.get("media_id");
  const targetIssueId = searchParams.get("issue_id");

  const [activeTab, setActiveTab] = useState<"catalog" | "scanner">("catalog");
  const [catalogItems, setCatalogItems] = useState<IssueNotification[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [selectedIssue, setSelectedIssue] = useState<IssueNotification | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // Direct Audio upload state
  const [history, setHistory] = useState<AudioReport[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadingRef, setUploadingRef] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [refFile, setRefFile] = useState<File | null>(null);
  const [latestRefId, setLatestRefId] = useState<number | null>(null);
  const [testFile, setTestFile] = useState<File | null>(null);
  const [latestReport, setLatestReport] = useState<AudioReport | null>(null);

  const loadCatalog = async () => {
    setCatalogLoading(true);
    try {
      const data = await notifications.getCatalog("audio_loss");
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

  const loadHistory = async () => {
    try {
      const data = await audio.getHistory();
      setHistory(data || []);
    } catch {
      // empty
    }
  };

  useEffect(() => {
    loadCatalog();
    loadHistory();
  }, []);

  const handleUploadReference = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!refFile) return;

    setError(null);
    setSuccessMsg(null);
    setUploadingRef(true);

    try {
      const res = await audio.uploadReference(refFile);
      setLatestRefId(res.reference_id);
      setSuccessMsg(`Original audio reference #${res.reference_id} fingerprinted successfully.`);
      setRefFile(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to upload reference audio. Please verify it is a valid PCM WAV file.");
      }
    } finally {
      setUploadingRef(false);
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!testFile) return;

    setError(null);
    setSuccessMsg(null);
    setAnalyzing(true);

    try {
      const report = await audio.analyze(testFile, latestRefId || undefined);
      setLatestReport(report);
      setTestFile(null);
      loadHistory();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to analyze audio stream.");
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
      (item.media?.caption && item.media.caption.toLowerCase().includes(q)) ||
      (item.audio_status && item.audio_status.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          Instagram Reel Audio Loss & Change Detector
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Detect copyright mutes, licensed sound replacements, and silent audio corruption using acoustic spectrogram fingerprinting
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
          <Layers size={14} /> Audio Loss Detector Catalog ({catalogItems.length})
        </button>

        <button
          onClick={() => setActiveTab("scanner")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === "scanner"
              ? "bg-[#17212B] text-white shadow-sm"
              : "bg-white text-[#636E72] border border-gray-200 hover:text-[#17212B]"
          }`}
        >
          <Volume2 size={14} /> Master Audio WAV Fingerprint Lab
        </button>
      </div>

      {/* TAB 1: Feature-Wise Audio Catalog */}
      {activeTab === "catalog" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-[#17212B]">
                Reels Audio Disruption Catalog
              </h2>
              <p className="text-xs text-[#636E72]">
                Reels flagged with missing acoustic tracks, unexpected silence, or licensed sound replacements
              </p>
            </div>

            <div className="relative max-w-xs w-full">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search catalog by caption or sound..."
                className="w-full pl-9 pr-3 py-1.5 bg-white border border-gray-200 rounded-xl text-xs text-[#2D3436] focus:outline-none focus:ring-1 focus:ring-[#2A9D8F]"
              />
            </div>
          </div>

          {catalogLoading ? (
            <div className="py-20 text-center text-xs text-[#636E72]">
              <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
              Loading audio video catalog...
            </div>
          ) : filteredCatalog.length === 0 ? (
            <div className="py-16 text-center text-xs text-[#636E72] bg-white rounded-3xl border border-gray-100 p-8 space-y-2">
              <CheckCircle2 size={36} className="mx-auto text-emerald-500" />
              <p className="font-bold text-sm text-[#17212B]">No Audio Disruptions Detected</p>
              <p className="text-gray-400">All creator Reels retain complete and audible soundtrack integrity.</p>
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
                        ? "border-[#E9B44C] shadow-lg ring-2 ring-[#E9B44C]/30"
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
                                : "bg-amber-50 text-amber-800"
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
                            <span className="text-gray-400">Audio Status: </span>
                            <span className="font-semibold text-red-600 uppercase text-[11px]">
                              {item.audio_status || "Missing / Silent"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Comparison Score: </span>
                            <span className="font-bold text-[#17212B]">
                              {item.similarity_score !== null ? `${Math.round(item.similarity_score * 100)}% Match` : "N/A"}
                            </span>
                          </div>
                        </div>

                        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
                          <button
                            onClick={() => setSelectedIssue(item)}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#17212B] text-white hover:bg-[#E9B44C] hover:text-[#17212B] transition-colors"
                          >
                            <Eye size={12} /> Detailed Audio Audit
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

          {/* Modal Report */}
          {selectedIssue && (
            <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl border border-gray-100 space-y-5 animate-in fade-in zoom-in-95 duration-200">
                <div className="flex items-start justify-between border-b border-gray-100 pb-3">
                  <div>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#E9B44C]/20 text-[#E9B44C] uppercase tracking-wider">
                      Reel Audio Integrity Report
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

                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-2xl text-amber-900 space-y-1">
                    <p className="font-bold">Acoustic Diagnostics:</p>
                    <p>{selectedIssue.description}</p>
                    <div className="grid grid-cols-2 gap-2 pt-2 text-[11px]">
                      <div>
                        <strong>Reference Master:</strong> {selectedIssue.previous_audio_ref || "None registered"}
                      </div>
                      <div>
                        <strong>Current Status:</strong> {selectedIssue.current_audio_status || selectedIssue.audio_status}
                      </div>
                      <div>
                        <strong>Spectral Similarity:</strong> {selectedIssue.similarity_score !== null ? `${Math.round(selectedIssue.similarity_score * 100)}%` : "0%"}
                      </div>
                      <div>
                        <strong>Affected Window:</strong> {selectedIssue.problem_timestamps || "Full Duration"}
                      </div>
                    </div>
                  </div>

                  {selectedIssue.recommendation && (
                    <div className="p-3 bg-teal-50 border border-teal-200 rounded-2xl text-teal-900 space-y-1">
                      <p className="font-bold text-[#2A9D8F]">Suggested Creator Action:</p>
                      <p>{selectedIssue.recommendation}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-gray-400 text-[11px] pt-1">
                    <span>Audit Timestamp: {new Date(selectedIssue.analysis_timestamp).toLocaleString()}</span>
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

      {/* TAB 2: Direct Master Audio Fingerprint Lab */}
      {activeTab === "scanner" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-[#17212B]">Register Original Reference Audio</h2>
              <p className="text-xs text-[#636E72]">
                Upload master WAV audio file to compute and store an acoustic spectrogram fingerprint.
              </p>

              <form onSubmit={handleUploadReference} className="space-y-4">
                <div className="border-2 border-dashed border-gray-200 rounded-2xl p-6 text-center hover:border-[#2A9D8F] transition-colors cursor-pointer bg-[#F7F8F5]">
                  <FileAudio size={28} className="mx-auto text-gray-400 mb-2" />
                  <label className="block text-xs font-semibold text-[#17212B] cursor-pointer">
                    {refFile ? refFile.name : "Choose original WAV file"}
                    <input
                      type="file"
                      accept=".wav,audio/wav"
                      onChange={(e) => setRefFile(e.target.files?.[0] || null)}
                      className="hidden"
                    />
                  </label>
                  <p className="text-[11px] text-gray-400 mt-1">Accepts PCM .wav master audio</p>
                </div>

                <div className="flex items-center justify-between">
                  {latestRefId && (
                    <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                      <CheckCircle2 size={13} /> Active Ref: #{latestRefId}
                    </span>
                  )}
                  <button
                    type="submit"
                    disabled={uploadingRef || !refFile}
                    className="ml-auto px-5 py-2 rounded-xl text-xs font-semibold text-white bg-[#17212B] hover:bg-[#2A9D8F] transition-all disabled:opacity-40"
                  >
                    {uploadingRef ? <Loader2 size={13} className="animate-spin" /> : "Fingerprint Reference"}
                  </button>
                </div>
              </form>
            </div>

            <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-[#17212B]">Test Current Audio Integrity</h2>
              <p className="text-xs text-[#636E72]">
                Upload test audio to compare against reference fingerprint or detect silence.
              </p>

              <form onSubmit={handleAnalyze} className="space-y-4">
                <div className="border-2 border-dashed border-gray-200 rounded-2xl p-6 text-center hover:border-[#A78BFA] transition-colors cursor-pointer bg-[#F7F8F5]">
                  <Volume2 size={28} className="mx-auto text-gray-400 mb-2" />
                  <label className="block text-xs font-semibold text-[#17212B] cursor-pointer">
                    {testFile ? testFile.name : "Choose audio to inspect"}
                    <input
                      type="file"
                      accept=".wav,audio/wav"
                      onChange={(e) => setTestFile(e.target.files?.[0] || null)}
                      className="hidden"
                    />
                  </label>
                  <p className="text-[11px] text-gray-400 mt-1">Accepts PCM .wav stream</p>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-[#636E72]">
                    {latestRefId ? `Comparing vs #${latestRefId}` : "Standalone silence detection"}
                  </span>
                  <button
                    type="submit"
                    disabled={analyzing || !testFile}
                    className="px-5 py-2 rounded-xl text-xs font-semibold text-white bg-[#2A9D8F] hover:bg-[#238478] transition-all disabled:opacity-40"
                  >
                    {analyzing ? <Loader2 size={13} className="animate-spin" /> : "Run Check"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AudioDetectorPage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-xs text-[#636E72]">
          <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
          Loading Audio Detector...
        </div>
      }
    >
      <AudioDetectorContent />
    </Suspense>
  );
}
