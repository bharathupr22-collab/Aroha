"use client";

import React, { useState, useEffect } from "react";
import { instagram, type InstagramAccount, type GrowthPoint } from "@/services/api";
import {
  TrendingUp,
  Award,
  Video,
  BarChart,
  Calendar,
  Sparkles,
  ArrowUpRight,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

const TOP_REELS = [
  {
    id: "reel-101",
    caption: "How AI audio fingerprinting catches silent reel glitches #tech #ai",
    views: "48.2K",
    likes: "3.4K",
    shares: "890",
    engagementRate: "8.7%",
    status: "Intact",
  },
  {
    id: "reel-102",
    caption: "3 Signs your affiliate links are broken in bio #creators #marketing",
    views: "36.9K",
    likes: "2.8K",
    shares: "640",
    engagementRate: "7.9%",
    status: "Intact",
  },
  {
    id: "reel-103",
    caption: "Lip-sync errors cost you 40% watch time! Testing with SyncNet #video",
    views: "29.4K",
    likes: "2.1K",
    shares: "510",
    engagementRate: "6.8%",
    status: "Intact",
  },
];

const HISTORICAL_SERIES = [
  { interval: "Jan", followers: 9800, avgReach: 2400 },
  { interval: "Feb", followers: 10500, avgReach: 2800 },
  { interval: "Mar", followers: 11200, avgReach: 3200 },
  { interval: "Apr", followers: 12100, avgReach: 3900 },
  { interval: "May", followers: 12900, avgReach: 4600 },
  { interval: "Jun", followers: 13620, avgReach: 5200 },
];

export default function GrowthPage() {
  const [account, setAccount] = useState<InstagramAccount | null>(null);

  useEffect(() => {
    instagram.getAccount().then(setAccount).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          Growth & Content Performance Analysis
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Longitudinal audience accumulation and top-performing Reel content analytics
        </p>
      </div>

      {/* Growth Metric Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-xs font-semibold text-[#636E72] uppercase tracking-wider">30-Day Growth Velocity</span>
          <p className="mt-3 text-2xl font-bold text-[#17212B]">+1,170</p>
          <div className="mt-1 flex items-center gap-1 text-xs text-emerald-600 font-medium">
            <ArrowUpRight size={14} /> +38.4 followers / day avg
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-xs font-semibold text-[#636E72] uppercase tracking-wider">Avg Reel Reach</span>
          <p className="mt-3 text-2xl font-bold text-[#17212B]">38.1K</p>
          <div className="mt-1 flex items-center gap-1 text-xs text-emerald-600 font-medium">
            <ArrowUpRight size={14} /> +14.2% vs previous period
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <span className="text-xs font-semibold text-[#636E72] uppercase tracking-wider">Overall Engagement Index</span>
          <p className="mt-3 text-2xl font-bold text-[#17212B]">7.8%</p>
          <div className="mt-1 text-xs text-[#636E72]">
            High viral retention benchmark
          </div>
        </div>
      </div>

      {/* Longitudinal Growth Chart */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm">
        <h2 className="text-base font-bold text-[#17212B]">6-Month Growth Trajectory</h2>
        <p className="text-xs text-[#636E72] mt-0.5">Audience volume expansion across monthly milestones</p>

        <div className="h-72 w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={HISTORICAL_SERIES} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F0" />
              <XAxis dataKey="interval" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "#17212B", borderRadius: "12px", color: "#fff", fontSize: "12px", border: "none" }}
              />
              <Line
                type="monotone"
                dataKey="followers"
                stroke="#2A9D8F"
                strokeWidth={3}
                dot={{ fill: "#2A9D8F", r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="avgReach"
                stroke="#A78BFA"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ fill: "#A78BFA", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Best-Performing Content Table */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-[#17212B]">Top Performing Reels</h2>
            <p className="text-xs text-[#636E72] mt-0.5">Content ranked by verified engagement and watch-through metrics</p>
          </div>
          <Award size={20} className="text-[#E9B44C]" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-gray-200 text-[#636E72] font-semibold">
                <th className="py-3 px-2">Content Caption</th>
                <th className="py-3 px-2">Estimated Views</th>
                <th className="py-3 px-2">Likes</th>
                <th className="py-3 px-2">Shares</th>
                <th className="py-3 px-2">Engagement</th>
                <th className="py-3 px-2">Audio State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {TOP_REELS.map((reel) => (
                <tr key={reel.id} className="hover:bg-gray-50/50">
                  <td className="py-3 px-2 font-medium text-[#17212B] max-w-xs truncate">
                    {reel.caption}
                  </td>
                  <td className="py-3 px-2 text-[#636E72]">{reel.views}</td>
                  <td className="py-3 px-2 text-[#636E72]">{reel.likes}</td>
                  <td className="py-3 px-2 text-[#636E72]">{reel.shares}</td>
                  <td className="py-3 px-2 font-bold text-[#2A9D8F]">{reel.engagementRate}</td>
                  <td className="py-3 px-2">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      {reel.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
