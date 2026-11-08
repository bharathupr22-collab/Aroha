"use client";

import React from "react";
import { AuthProvider } from "@/hooks/useAuth";
import { SidebarProvider } from "@/hooks/useSidebar";
import Sidebar from "@/components/layout/Sidebar";
import Navbar from "@/components/layout/Navbar";
import { useSidebar } from "@/hooks/useSidebar";

function DashboardShell({ children }: { children: React.ReactNode }) {
  const { expanded } = useSidebar();

  return (
    <div className="min-h-screen bg-[#F7F8F5]">
      <Sidebar />
      <div
        className={`transition-all duration-300 ease-in-out ${
          expanded ? "lg:ml-64" : "lg:ml-[72px]"
        }`}
      >
        <Navbar />
        <main className="p-4 md:p-6 lg:p-8 max-w-[1400px] mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <SidebarProvider>
        <DashboardShell>{children}</DashboardShell>
      </SidebarProvider>
    </AuthProvider>
  );
}

