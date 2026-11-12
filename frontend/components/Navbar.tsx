"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, UserProfile, ProviderItem } from "@/lib/api";
import { KeyRound, User, LogOut, CheckCircle2, AlertCircle } from "lucide-react";

export function Navbar() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [activeProvider, setActiveProvider] = useState<ProviderItem | null>(null);

  useEffect(() => {
    async function loadStatus() {
      try {
        const token = api.getToken();
        if (!token) {
          // Attempt default test registration/login for immediate out-of-the-box SaaS access
          try {
            const authRes = await api.login("student@exampilot.com", "Password123!");
            setProfile(authRes.user);
          } catch {
            try {
              const regRes = await api.register("student@exampilot.com", "Password123!", "Demo Student");
              setProfile(regRes.user);
            } catch {
              // Ignore
            }
          }
        } else {
          const p = await api.getProfile();
          setProfile(p);
        }

        const provs = await api.getProviders();
        const def = provs.find(p => p.is_default) || provs[0];
        if (def) setActiveProvider(def);
      } catch {
        // Silently handle
      }
    }
    loadStatus();
  }, []);

  return (
    <header className="h-16 border-b border-cardBorder bg-[#0c111e]/80 backdrop-blur sticky top-0 z-40 px-6 flex items-center justify-between">
      {/* Search / Status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-card border border-cardBorder text-xs text-muted">
          <span className="text-foreground font-medium">ExamPilot 2.0</span>
          <span>&bull;</span>
          <span>Production AI Learning Hub</span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Active Provider Pill */}
        <Link 
          href="/providers"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-cardBorder bg-card text-xs hover:border-primary transition-colors"
        >
          <KeyRound className="w-3.5 h-3.5 text-primary" />
          <span className="text-muted">Provider:</span>
          {activeProvider ? (
            <span className="font-semibold text-foreground flex items-center gap-1.5 capitalize">
              {activeProvider.provider} ({activeProvider.default_model || "default"})
              <CheckCircle2 className="w-3 h-3 text-success" />
            </span>
          ) : (
            <span className="text-warning flex items-center gap-1">
              Configure Key
              <AlertCircle className="w-3 h-3 text-warning" />
            </span>
          )}
        </Link>

        {/* User Pill */}
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-card border border-cardBorder text-xs">
          <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center font-bold text-[10px]">
            {profile ? profile.display_name.charAt(0).toUpperCase() : <User className="w-3.5 h-3.5" />}
          </div>
          <span className="text-foreground font-medium">{profile?.display_name || "Active Session"}</span>
        </div>
      </div>
    </header>
  );
}

