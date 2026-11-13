"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { notifications, links, type IssueNotification, type LinkReport } from "@/services/api";
import { Link as LinkIcon, AlertTriangle, CheckCircle2, Loader2, Search, RefreshCw, BellRing, Play, Bug, ExternalLink } from "lucide-react";

function LinkAnalyzerContent() {
  const searchParams = useSearchParams();
  const targetMediaId = searchParams.get("media_id");
  const targetIssueId = searchParams.get("issue_id");

  const [catalogItems, setCatalogItems] = useState<IssueNotification[]>([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [scanningProfile, setScanningProfile] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "unresolved" | "resolved">("all");

  // Manual Tester State
  const [manualInput, setManualInput] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [manualResults, setManualResults] = useState<LinkReport[]>([]);
  const [manualError, setManualError] = useState("");

  const loadCatalog = async () => {
    setCatalogLoading(true);
    try {
      const data = await notifications.getCatalog("broken_link");
      setCatalogItems(data || []);
    } catch {
      // ignore
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
      // ignore
    } finally {
      setScanningProfile(false);
    }
  };

  const handleManualAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualInput.trim()) return;
    setIsAnalyzing(true);
    setManualError("");
    setManualResults([]);
    
    try {
      // If it starts with http, pass as url, otherwise pass as raw caption text
      const isUrl = manualInput.trim().startsWith("http");
      const res = await links.analyze(isUrl ? { urls: [manualInput.trim()] } : { text: manualInput });
      setManualResults(res);
      if (res.length === 0) {
        setManualError("No detectable links found in that text.");
      }
    } catch (err: any) {
      setManualError(err.detail || "Failed to analyze the link. Backend might be unreachable.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const filteredCatalog = catalogItems.filter((item) => {
    if (statusFilter === "unresolved" && item.is_resolved) return false;
    if (statusFilter === "resolved" && !item.is_resolved) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      (item.detected_url && item.detected_url.toLowerCase().includes(q)) ||
      (item.media?.caption && item.media.caption.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-200 pb-5">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#2A9D8F]/10 text-[#2A9D8F] text-[11px] font-bold mb-2">
            <BellRing size={12} /> Automated Link Auditor
          </div>
          <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
            Broken Promotional Link Analyzer
          </h1>
          <p className="text-xs text-[#636E72] mt-1">
            Detect 404s, affiliate redirect loops, and blocked domains in your Bio and Reel captions.
          </p>
        </div>
      </div>

      {/* MANUAL TESTER WIDGET (No followers required) */}
      <div className="p-6 rounded-3xl bg-white border border-[#2A9D8F]/30 shadow-md relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-50 rounded-full blur-3xl opacity-50 -mr-20 -mt-20 pointer-events-none" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-emerald-100 text-emerald-700 rounded-xl">
              <Bug size={20} />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#17212B]">Test Any Link Manually (0 Followers Needed)</h2>
              <p className="text-xs text-[#636E72]">Paste a Bio URL, sponsor link, or full Reel caption below for an instant real-time audit.</p>
            </div>
          </div>
          
          <form onSubmit={handleManualAnalyze} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder="e.g. https://my-affiliate.com/promo or paste full caption..."
              value={manualInput}
              onChange={(e) => setManualInput(e.target.value)}
              className="flex-1 bg-[#F7F8F5] border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] outline-none transition-all"
            />
            <button
              type="submit"
              disabled={isAnalyzing || !manualInput.trim()}
              className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl bg-[#2A9D8F] text-white font-bold text-sm hover:bg-[#238478] transition-all disabled:opacity-50 shrink-0 shadow-sm"
            >
              {isAnalyzing ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
              Analyze Now
            </button>
          </form>

          {manualError && (
            <p className="mt-3 text-xs text-red-600 font-medium">{manualError}</p>
          )}

          {manualResults.length > 0 && (
            <div className="mt-6 space-y-3 border-t border-gray-100 pt-4">
              <p className="text-xs font-bold text-[#17212B] uppercase tracking-wider mb-2">Live Analysis Results</p>
              {manualResults.map((res, idx) => (
                <div key={idx} className={`p-4 rounded-xl border flex items-center justify-between gap-4 ${res.validation_result === 'active' ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'}`}>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold truncate text-[#17212B]">{res.detected_url}</p>
                    <div className="flex items-center gap-3 mt-1 text-[11px] font-mono">
                      <span className={res.validation_result === 'active' ? 'text-emerald-700' : 'text-red-700'}>
                        Status: {res.response_status || 'ERR'} ({res.validation_result.toUpperCase()})
                      </span>
                      {res.final_url && res.final_url !== res.detected_url && (
                        <span className="text-gray-500 truncate">Redirects to: {res.final_url}</span>
                      )}
                    </div>
                  </div>
                  <a href={res.detected_url} target="_blank" rel="noreferrer" className="p-2 bg-white rounded-lg border border-gray-200 hover:bg-gray-50 text-gray-500 transition-colors">
                    <ExternalLink size={16} />
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Connected Profile Automated Catalog */}
      <div className="pt-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-red-50 text-red-600">
              <LinkIcon size={18} />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#17212B]">Automated Profile Alerts ({filteredCatalog.length})</h2>
              <p className="text-xs text-[#636E72]">Syncs automatically with your connected Instagram profile</p>
            </div>
          </div>
          
          <button
            onClick={handleProfileRescan}
            disabled={scanningProfile || catalogLoading}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-[#17212B] text-white hover:bg-gray-800 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={14} className={scanningProfile ? "animate-spin" : ""} />
            {scanningProfile ? "Scanning..." : "Run Profile Scan"}
          </button>
        </div>

        {catalogLoading ? (
          <div className="py-20 text-center text-xs text-[#636E72]">
            <Loader2 size={24} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
            Fetching automated audit history...
          </div>
        ) : filteredCatalog.length === 0 ? (
          <div className="py-16 text-center bg-white rounded-3xl border border-gray-100 p-8 space-y-2">
            <CheckCircle2 size={36} className="mx-auto text-emerald-500" />
            <p className="font-bold text-sm text-[#17212B]">No Broken Links Detected in Profile</p>
            <p className="text-xs text-gray-400">All scanned promotional links across your Reels and Bio are healthy.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredCatalog.map((item) => (
              <div key={item.id} className={`p-4 rounded-2xl bg-white border ${item.is_resolved ? 'border-emerald-100 bg-emerald-50/10' : 'border-gray-200'}`}>
                <div className="flex justify-between items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[10px] font-mono text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                        {item.media?.platform_media_id || "Profile Bio"}
                      </span>
                      {item.is_resolved ? (
                        <span className="text-[10px] font-bold text-emerald-600 flex items-center gap-1"><CheckCircle2 size={12}/> Resolved</span>
                      ) : (
                        <span className="text-[10px] font-bold text-red-600 flex items-center gap-1"><AlertTriangle size={12}/> Flagged</span>
                      )}
                    </div>
                    <h3 className="font-bold text-sm text-[#17212B] truncate">{item.title}</h3>
                    <p className="text-xs text-[#636E72] line-clamp-1 mt-1 break-all">
                      Found: {item.detected_url}
                    </p>
                  </div>
                  {item.media?.thumbnail_url && (
                    <img src={item.media.thumbnail_url} alt="Thumbnail" className="w-12 h-12 rounded-lg object-cover border border-gray-100 shrink-0" />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function LinkAnalyzerPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center"><Loader2 className="animate-spin mx-auto text-[#2A9D8F]" /></div>}>
      <LinkAnalyzerContent />
    </Suspense>
  );
}
