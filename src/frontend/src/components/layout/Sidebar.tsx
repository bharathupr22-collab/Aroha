"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSidebar } from "@/hooks/useSidebar";
import { useAuth } from "@/hooks/useAuth";
import { notifications, instagram, type InstagramAccount } from "@/services/api";
import {
  Home,
  BarChart3,
  UserMinus,
  TrendingUp,
  LinkIcon,
  Volume2,
  Mic,
  Newspaper,
  Bell,
  Settings,
  User,
  ChevronLeft,
  ChevronRight,
  X,
  LogIn,
} from "lucide-react";
import { InstagramIcon } from "@/components/icons/InstagramIcon";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  requiresAuth?: boolean;
  showBadge?: boolean;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: Home, requiresAuth: true },
  { label: "Analytics", href: "/dashboard/analytics", icon: BarChart3, requiresAuth: true },
  { label: "Unfollowers", href: "/dashboard/unfollowers", icon: UserMinus, requiresAuth: true },
  { label: "Growth Analysis", href: "/dashboard/growth", icon: TrendingUp, requiresAuth: true },
  { label: "Broken Link Analyzer", href: "/dashboard/link-analyzer", icon: LinkIcon, requiresAuth: true },
  { label: "Audio Loss Detector", href: "/dashboard/audio-detector", icon: Volume2, requiresAuth: true },
  { label: "Lip-Sync Analyzer", href: "/dashboard/lipsync", icon: Mic, requiresAuth: true },
  { label: "Trends & News", href: "/dashboard/trends", icon: Newspaper },
  { label: "Notifications", href: "/dashboard/notifications", icon: Bell, requiresAuth: true, showBadge: true },
];

const bottomItems: NavItem[] = [
  { label: "Settings", href: "/dashboard/settings", icon: Settings, requiresAuth: true },
  { label: "Profile", href: "/dashboard/profile", icon: User, requiresAuth: true },
];

export default function Sidebar() {
  const { expanded, toggle, mobileOpen, setMobileOpen } = useSidebar();
  const pathname = usePathname();
  const { user } = useAuth();
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [igAccount, setIgAccount] = useState<InstagramAccount | null>(null);

  useEffect(() => {
    if (!user) return;
    const fetchStatus = () => {
      notifications.getSummary()
        .then((s) => setUnreadCount(s.unread_count))
        .catch(() => {});
      instagram.getAccount()
        .then((acc) => setIgAccount(acc))
        .catch(() => setIgAccount(null));
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, [user, pathname]);

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  };

  const sidebarContent = (
    <div className="flex flex-col h-full bg-[#17212B] text-white">
      {/* Logo area */}
      <div className="flex items-center h-16 px-4 border-b border-white/10 shrink-0">
        <Link href="/dashboard" className="flex items-center gap-3 min-w-0">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#2A9D8F] to-[#A78BFA] flex items-center justify-center shrink-0">
            <svg viewBox="0 0 24 24" className="w-5 h-5" fill="none">
              <path d="M12 3L4 21h3.5l1.5-3.8h6L16.5 21H20L12 3z" fill="white" />
              <path d="M12 9.5L9.5 15.5h5L12 9.5z" fill="#17212B" />
              <rect x="9" y="14" width="6" height="1" rx="0.5" fill="#E9B44C" />
            </svg>
          </div>
          {expanded && (
            <span className="text-lg font-bold tracking-wider whitespace-nowrap overflow-hidden">
              AROHA
            </span>
          )}
        </Link>

        <button
          onClick={toggle}
          className="ml-auto hidden lg:flex items-center justify-center w-7 h-7 rounded-md hover:bg-white/10 transition-colors"
          aria-label={expanded ? "Collapse sidebar" : "Expand sidebar"}
        >
          {expanded ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>

        <button
          onClick={() => setMobileOpen(false)}
          className="ml-auto lg:hidden flex items-center justify-center w-7 h-7 rounded-md hover:bg-white/10 transition-colors"
          aria-label="Close menu"
        >
          <X size={16} />
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          const needsAuth = item.requiresAuth && !user;

          return (
            <Link
              key={item.href}
              href={needsAuth ? "/login" : item.href}
              onClick={() => setMobileOpen(false)}
              className={`
                group relative flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200
                ${active
                  ? "bg-[#2A9D8F]/20 text-[#2A9D8F]"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
                }
              `}
              title={!expanded ? item.label : undefined}
            >
              <div className="relative shrink-0">
                <Icon
                  size={20}
                  className={`${active ? "text-[#2A9D8F]" : "text-gray-400 group-hover:text-white"}`}
                />
                {!expanded && item.showBadge && unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-red-500 border border-[#17212B]" />
                )}
              </div>

              {expanded && (
                <div className="flex items-center justify-between flex-1 min-w-0">
                  <span className="text-sm font-medium whitespace-nowrap overflow-hidden">
                    {item.label}
                  </span>
                  {item.showBadge && unreadCount > 0 && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-500 text-white">
                      {unreadCount}
                    </span>
                  )}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Connect Instagram button & Bottom Items */}
      <div className="px-2 py-2 border-t border-white/10">
        {user && (
          <Link
            href="/dashboard/settings"
            onClick={() => setMobileOpen(false)}
            className={`
              flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200
              ${igAccount ? "text-emerald-400 hover:bg-white/5" : "text-gray-400 hover:bg-white/5 hover:text-white"}
            `}
            title={!expanded ? (igAccount ? `@${igAccount.username} (Connected)` : "Connect Instagram") : undefined}
          >
            <InstagramIcon size={20} className="shrink-0" />
            {expanded && (
              <span className="text-sm font-medium whitespace-nowrap truncate">
                {igAccount ? `@${igAccount.username}` : "Connect Instagram"}
              </span>
            )}
          </Link>
        )}

        {bottomItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          const needsAuth = item.requiresAuth && !user;

          return (
            <Link
              key={item.href}
              href={needsAuth ? "/login" : item.href}
              onClick={() => setMobileOpen(false)}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200
                ${active
                  ? "bg-[#2A9D8F]/20 text-[#2A9D8F]"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
                }
              `}
              title={!expanded ? item.label : undefined}
            >
              <Icon size={20} className="shrink-0" />
              {expanded && (
                <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
              )}
            </Link>
          );
        })}

        {!user && (
          <Link
            href="/login"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-[#E9B44C] hover:bg-[#E9B44C]/10 transition-all duration-200"
            title={!expanded ? "Log In" : undefined}
          >
            <LogIn size={20} className="shrink-0" />
            {expanded && (
              <span className="text-sm font-medium whitespace-nowrap">Log In</span>
            )}
          </Link>
        )}
      </div>
    </div>
  );

  return (
    <>
      <aside
        className={`
          hidden lg:flex flex-col fixed top-0 left-0 h-screen z-40
          transition-all duration-300 ease-in-out
          ${expanded ? "w-64" : "w-[72px]"}
        `}
      >
        {sidebarContent}
      </aside>

      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-screen w-64 z-50 lg:hidden
          transition-transform duration-300 ease-in-out
          ${mobileOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
