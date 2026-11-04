"use client";

import React, { useState, useEffect } from "react";
import { news, type NewsArticle, type CategoryCount, ApiError } from "@/services/api";
import {
  Newspaper,
  Search,
  RefreshCw,
  ExternalLink,
  Tag,
  Sparkles,
  TrendingUp,
  Clock,
  Layers,
} from "lucide-react";

const CATEGORIES = [
  { id: "", label: "All News" },
  { id: "instagram", label: "Instagram Updates" },
  { id: "reels", label: "Reels & Formats" },
  { id: "marketing", label: "Social Marketing" },
  { id: "ai", label: "AI & Creator Tech" },
  { id: "policy", label: "Algorithm & Policy" },
  { id: "general", label: "Industry Trends" },
];

export default function TrendsPage() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [selectedCat, setSelectedCat] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadNews = async () => {
    setLoading(true);
    try {
      const data = await news.getArticles({
        category: selectedCat || undefined,
        q: searchQuery || undefined,
        limit: 30,
      });
      setArticles(data || []);
    } catch {
      // not loaded
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNews();
  }, [selectedCat]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadNews();
  };

  const handleRefreshFeed = async () => {
    setRefreshing(true);
    try {
      await news.refresh();
      await loadNews();
    } catch {
      // failed refresh
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
            Social Media Trends & Industry Intelligence
          </h1>
          <p className="text-xs text-[#636E72] mt-1">
            Pinterest-style live masonry feed of algorithm updates, viral formats, and creator economy news
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleRefreshFeed}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-white border border-gray-200 text-[#17212B] hover:bg-gray-50 shadow-sm transition-colors disabled:opacity-50"
          >
            <RefreshCw size={13} className={refreshing ? "animate-spin" : ""} />
            {refreshing ? "Fetching RSS..." : "Refresh Feeds"}
          </button>
        </div>
      </div>

      {/* Search & Category Filter Pills */}
      <div className="space-y-4">
        <form onSubmit={handleSearch} className="relative max-w-lg">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search Instagram algorithms, Reels features, monetization..."
            className="w-full pl-10 pr-24 py-2.5 bg-white border border-gray-200 rounded-full text-xs text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] shadow-sm transition-all"
          />
          <button
            type="submit"
            className="absolute right-1.5 top-1/2 -translate-y-1/2 px-4 py-1.5 rounded-full text-xs font-semibold bg-[#2A9D8F] text-white hover:bg-[#238478] transition-colors"
          >
            Search
          </button>
        </form>

        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCat(cat.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all shadow-sm ${
                selectedCat === cat.id
                  ? "bg-[#17212B] text-white"
                  : "bg-white text-[#636E72] border border-gray-200 hover:border-[#2A9D8F] hover:text-[#17212B]"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Masonry Grid Feed */}
      {loading ? (
        <div className="py-20 text-center text-xs text-[#636E72]">
          <RefreshCw size={28} className="animate-spin mx-auto mb-2 text-[#2A9D8F]" />
          Aggregating verified industry publications...
        </div>
      ) : articles.length === 0 ? (
        <div className="py-20 text-center text-xs text-[#636E72] bg-white rounded-3xl border border-gray-100 p-8">
          <Newspaper size={36} className="mx-auto mb-3 text-gray-300" />
          <p className="font-semibold text-sm text-[#17212B]">No articles match your query</p>
          <p className="mt-1">Try switching categories or click &ldquo;Refresh Feeds&rdquo; to pull latest dispatches.</p>
        </div>
      ) : (
        <div className="columns-1 sm:columns-2 lg:columns-3 xl:columns-4 gap-6 space-y-6">
          {articles.map((item) => (
            <div
              key={item.id}
              className="break-inside-avoid p-5 bg-white rounded-3xl border border-gray-100 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-[#2A9D8F]/10 text-[#2A9D8F]">
                    {item.category}
                  </span>
                  <span className="text-[10px] text-gray-400 font-medium">
                    {item.source}
                  </span>
                </div>

                <a
                  href={item.article_url}
                  target="_blank"
                  rel="noreferrer"
                  className="font-bold text-sm text-[#17212B] group-hover:text-[#2A9D8F] transition-colors leading-snug line-clamp-3"
                >
                  {item.title}
                </a>

                {item.description && (
                  <p className="text-xs text-[#636E72] mt-2.5 leading-relaxed line-clamp-4">
                    {item.description}
                  </p>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between text-[11px] text-[#636E72]">
                <span className="flex items-center gap-1 text-gray-400">
                  <Clock size={12} />
                  {item.published_at ? new Date(item.published_at).toLocaleDateString() : "Recent"}
                </span>

                <a
                  href={item.article_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 font-semibold text-[#2A9D8F] hover:underline"
                >
                  Read Source <ExternalLink size={11} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

