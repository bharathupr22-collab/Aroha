"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useSidebar } from "@/hooks/useSidebar";
import { useAuth } from "@/hooks/useAuth";
import { notifications } from "@/services/api";
import {
  Menu,
  Search,
  Bell,
  User,
  LogOut,
  Settings,
  ChevronDown,
} from "lucide-react";
import { InstagramIcon } from "@/components/icons/InstagramIcon";

export default function Navbar() {
  const { setMobileOpen } = useSidebar();
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user) return;
    notifications.getSummary()
      .then((s) => setUnreadCount(s.unread_count))
      .catch(() => {});
  }, [user]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleLogout = async () => {
    setProfileOpen(false);
    await logout();
    window.location.href = "/";
  };

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-200/60">
      <div className="flex items-center h-16 px-4 gap-4">
        {/* Mobile menu button */}
        <button
          onClick={() => setMobileOpen(true)}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Open menu"
        >
          <Menu size={20} className="text-gray-600" />
        </button>

        {/* Search bar */}
        <div className="flex-1 max-w-xl">
          <div className="relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search AROHA..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#F7F8F5] border border-gray-200 rounded-full text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] transition-all"
            />
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-2">
          {/* Instagram connection status indicator */}
          {user && (
            <Link
              href="/dashboard/settings"
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500 hover:bg-gray-200 transition-colors"
            >
              <InstagramIcon size={14} />
              <span>Connect</span>
            </Link>
          )}

          {/* Notifications */}
          {user && (
            <Link
              href="/dashboard/notifications"
              className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
              aria-label="Notifications"
            >
              <Bell size={20} className="text-gray-600" />
              {unreadCount > 0 ? (
                <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 bg-red-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center">
                  {unreadCount}
                </span>
              ) : (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#2A9D8F] rounded-full" />
              )}
            </Link>
          )}

          {/* Profile dropdown */}
          {user ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#2A9D8F] to-[#A78BFA] flex items-center justify-center text-white text-sm font-semibold">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <ChevronDown size={14} className={`text-gray-400 transition-transform ${profileOpen ? "rotate-180" : ""}`} />
              </button>

              {profileOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-1.5 animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="px-4 py-2.5 border-b border-gray-100">
                    <p className="text-sm font-semibold text-gray-800 truncate">{user.name}</p>
                    <p className="text-xs text-gray-500 truncate">{user.email}</p>
                  </div>
                  <Link
                    href="/dashboard/profile"
                    onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <User size={16} /> Profile
                  </Link>
                  <Link
                    href="/dashboard/settings"
                    onClick={() => setProfileOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <Settings size={16} /> Settings
                  </Link>
                  <hr className="my-1 border-gray-100" />
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2.5 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut size={16} /> Log Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                Log In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium text-white bg-[#2A9D8F] rounded-full hover:bg-[#238b7f] transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

