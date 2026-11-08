"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

interface SidebarContextType {
  expanded: boolean;
  toggle: () => void;
  setExpanded: (v: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (v: boolean) => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const [expanded, setExpandedState] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Persist sidebar preference
  useEffect(() => {
    const saved = localStorage.getItem("aroha_sidebar");
    if (saved !== null) setExpandedState(saved === "true");
  }, []);

  const setExpanded = useCallback((v: boolean) => {
    setExpandedState(v);
    localStorage.setItem("aroha_sidebar", String(v));
  }, []);

  const toggle = useCallback(() => {
    setExpanded(!expanded);
  }, [expanded, setExpanded]);

  return (
    <SidebarContext.Provider value={{ expanded, toggle, setExpanded, mobileOpen, setMobileOpen }}>
      {children}
    </SidebarContext.Provider>
  );
}

export function useSidebar() {
  const ctx = useContext(SidebarContext);
  if (!ctx) throw new Error("useSidebar must be used within SidebarProvider");
  return ctx;
}

