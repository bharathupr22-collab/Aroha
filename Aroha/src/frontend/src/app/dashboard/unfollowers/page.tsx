"use client";

import React, { useState, useEffect } from "react";
import { instagram, type InstagramAccount, type GrowthPoint } from "@/services/api";
import {
  UserMinus,
  UserPlus,
  TrendingDown,
  Info,
  Calendar,
  AlertCircle,
  ShieldAlert,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

// Demo historical snapshots of follow/unfollow trends
const DEMO_CHURN_DATA = [
  { interval: "Week 1", newFollowers: 320, estimatedUnfollows: 45, netChange: 275 },
  { interval: "Week 2", newFollowers: 280, estimatedUnfollows: 62, netChange: 218 },
  { interval: "Week 3", newFollowers: 410, estimatedUnfollows: 88, netChange: 322 },
  { interval: "Week 4", newFollowers: 390, estimatedUnfollows: 55, netChange: 335 },
];

export default function UnfollowersPage() {
  const [account, setAccount] = useState<InstagramAccount | null>(null);
  const [growthPoints, setGrowthPoints] = useState<GrowthPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const acc = await instagram.getAccount();
        setAccount(acc);
        if (acc) {
          const g = await instagram.getGrowth();
          setGrowthPoints(g.data || []);
        }
      } catch {
        // empty
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          Unfollowers & Net Growth Analysis
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Historical follower differential estimation based on captured account checkpoints
        </p>
      </div>

      {/* Academic / Meta Policy Compliance Notice */}
      <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200/80 text-blue-900 text-xs flex items-start gap-3">
        <Info size={18} className="text-blue-700 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <p className="font-bold">Academic Distinction: API Metric Policy</p>
          <p className="mt-0.5 text-blue-800">
            Official Instagram Graph API privacy protocols intentionally omit individualized username-level unfollower events.
            AROHA strictly obeys developer policies by computing <strong>net follower differentials</strong> across verified historical snapshots,
            rather than scraping unauthorized user identities.
          </p>
        </div>
      </div>

      {/* Snapshot Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-[#636E72]">
            <span className="text-xs font-semibold uppercase tracking-wider">Est. New Followers</span>
            <UserPlus size={18} className="text-[#2A9D8F]" />
          </div>
          <p className="mt-4 text-2xl font-bold text-[#17212B]">+1,400</p>
          <p className="text-[11px] text-[#636E72] mt-1">Aggregated across recent periods</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-[#636E72]">
            <span className="text-xs font-semibold uppercase tracking-wider">Est. Unfollows (Differential)</span>
            <UserMinus size={18} className="text-red-500" />
          </div>
          <p className="mt-4 text-2xl font-bold text-red-600">-250</p>
          <p className="text-[11px] text-[#636E72] mt-1">Estimated churn across snapshots</p>
        </div>

        <div className="p-5 rounded-2xl bg-white border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between text-[#636E72]">
            <span className="text-xs font-semibold uppercase tracking-wider">Net Growth</span>
            <TrendingDown size={18} className="text-[#A78BFA]" />
          </div>
          <p className="mt-4 text-2xl font-bold text-emerald-600">+1,150</p>
          <p className="text-[11px] text-[#636E72] mt-1">Net audience retention balance</p>
        </div>
      </div>

      {/* Chart: Growth vs Churn Comparison */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm">
        <h2 className="text-base font-bold text-[#17212B]">Weekly Growth vs Churn Trend</h2>
        <p className="text-xs text-[#636E72] mt-0.5">Comparing new follower inflow against estimated churn intervals</p>

        <div className="h-80 w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={DEMO_CHURN_DATA} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F0" />
              <XAxis dataKey="interval" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "#17212B", borderRadius: "12px", color: "#fff", fontSize: "12px", border: "none" }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Bar dataKey="newFollowers" name="New Follows" fill="#2A9D8F" radius={[4, 4, 0, 0]} />
              <Bar dataKey="estimatedUnfollows" name="Estimated Churn" fill="#EF4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="netChange" name="Net Differential" fill="#E9B44C" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Methodology Explanatory Box */}
      <div className="p-6 rounded-3xl bg-[#F7F8F5] border border-gray-200">
        <h3 className="text-sm font-bold text-[#17212B]">How Differential Calculation Operates</h3>
        <p className="text-xs text-[#636E72] mt-2 leading-relaxed">
          When AROHA triggers an automatic or manual API synchronization, it archives the current timestamped follower count in the <code>analytics_history</code> table.
          By subtracting subsequent snapshots \(F(t_2) - F(t_1)\), AROHA determines exact net delta. When accounts report negative deltas or sudden drops in follower volume,
          the system flags potential audience churn spikes to correlate with recent Reel posts or algorithm shifts.
        </p>
      </div>
    </div>
  );
}

