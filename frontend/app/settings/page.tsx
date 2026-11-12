"use client";

import { useEffect, useState } from "react";
import { api, UserProfile } from "@/lib/api";
import { 
  Settings, 
  User, 
  Download, 
  Trash2, 
  Save, 
  ShieldAlert, 
  CheckCircle2,
  DollarSign,
  Palette
} from "lucide-react";

export default function SettingsPage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [settingsMap, setSettingsMap] = useState<Record<string, string>>({
    theme: "dark",
    monthly_budget_usd: "25.0"
  });

  const [confirmEmail, setConfirmEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const p = await api.getProfile();
      setProfile(p);
      setDisplayName(p.display_name || "");
      const s = await api.getSettings();
      setSettingsMap(s);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      await api.saveSetting("monthly_budget_usd", settingsMap.monthly_budget_usd);
      await api.saveSetting("theme", settingsMap.theme);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err: any) {
      alert("Failed to save settings: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleExportData = async () => {
    try {
      const data = await api.exportData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `exampilot_export_${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert("Failed to export data: " + err.message);
    }
  };

  const handleDeleteAccount = async () => {
    if (!profile) return;
    if (confirmEmail.trim().toLowerCase() !== profile.email.toLowerCase()) {
      alert("Email does not match your registered email address.");
      return;
    }
    if (!confirm("This will PERMANENTLY delete your account and all history. Are you completely sure?")) {
      return;
    }

    try {
      await api.deleteAccount(confirmEmail.trim());
      api.clearToken();
      window.location.href = "/";
    } catch (err: any) {
      alert("Failed to delete account: " + err.message);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Settings className="w-6 h-6 text-primary" />
          Settings & Account Management
        </h1>
        <p className="text-sm text-muted">
          Manage your account preferences, configure usage budgets, and export or delete your data.
        </p>
      </div>

      {/* Account Profile Card */}
      <div className="bg-card border border-cardBorder rounded-xl p-6 space-y-4">
        <h2 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-2">
          <User className="w-4 h-4 text-primary" />
          User Profile
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-muted block mb-1">Email Address</label>
            <input
              type="text"
              disabled
              value={profile?.email || ""}
              className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-muted cursor-not-allowed"
            />
          </div>

          <div>
            <label className="text-muted block mb-1">Display Name</label>
            <input
              type="text"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-foreground focus:outline-none focus:border-primary"
            />
          </div>
        </div>
      </div>

      {/* Preferences Form */}
      <form onSubmit={handleSavePreferences} className="bg-card border border-cardBorder rounded-xl p-6 space-y-5">
        <h2 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-2">
          <Palette className="w-4 h-4 text-secondary" />
          Preferences & Spending Thresholds
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-muted block mb-1">Application Theme</label>
            <select
              value={settingsMap.theme}
              onChange={(e) => setSettingsMap(prev => ({ ...prev, theme: e.target.value }))}
              className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-foreground focus:outline-none focus:border-primary"
            >
              <option value="dark">Dark Theme (Default SaaS)</option>
              <option value="light">Light Theme</option>
            </select>
          </div>

          <div>
            <label className="text-muted block mb-1">Monthly API Budget Threshold ($ USD)</label>
            <div className="relative">
              <input
                type="number"
                step="5"
                min="5"
                max="500"
                value={settingsMap.monthly_budget_usd}
                onChange={(e) => setSettingsMap(prev => ({ ...prev, monthly_budget_usd: e.target.value }))}
                className="w-full bg-[#101726] border border-cardBorder rounded-lg pl-7 pr-3 py-2 text-foreground focus:outline-none focus:border-primary font-mono"
              />
              <DollarSign className="w-3.5 h-3.5 text-muted absolute left-2.5 top-2.5" />
            </div>
          </div>
        </div>

        {saveSuccess && (
          <div className="p-3 rounded-lg bg-success/10 border border-success/30 text-success text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" /> Preferences updated successfully!
          </div>
        )}

        <button
          type="submit"
          disabled={saving}
          className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-40"
        >
          <Save className="w-3.5 h-3.5" /> Save Preferences
        </button>
      </form>

      {/* Data Export & Account Deletion */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Export Data */}
        <div className="bg-card border border-cardBorder rounded-xl p-6 space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-muted flex items-center gap-2">
            <Download className="w-4 h-4 text-primary" />
            Export My Data
          </h2>
          <p className="text-xs text-muted leading-relaxed">
            Download a complete portable JSON archive containing your question history, test sessions, and configured providers.
          </p>
          <button
            onClick={handleExportData}
            className="w-full py-2.5 rounded-lg bg-[#101726] border border-cardBorder hover:border-primary text-foreground text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
          >
            <Download className="w-4 h-4" /> Export Complete Archive
          </button>
        </div>

        {/* Delete Account */}
        <div className="bg-card border border-cardBorder rounded-xl p-6 space-y-3">
          <h2 className="text-xs font-bold uppercase tracking-wider text-danger flex items-center gap-2">
            <ShieldAlert className="w-4 h-4" />
            Danger Zone
          </h2>
          <p className="text-xs text-muted leading-relaxed">
            Permanently delete your profile and all associated questions, notes, and encrypted keys.
          </p>
          <input
            type="email"
            value={confirmEmail}
            onChange={(e) => setConfirmEmail(e.target.value)}
            placeholder={`Type ${profile?.email || "your email"} to confirm`}
            className="w-full bg-[#101726] border border-cardBorder rounded-lg px-3 py-2 text-xs text-foreground focus:outline-none focus:border-danger placeholder:text-muted/40"
          />
          <button
            onClick={handleDeleteAccount}
            disabled={!confirmEmail.trim()}
            className="w-full py-2.5 rounded-lg bg-danger/10 hover:bg-danger text-danger hover:text-white border border-danger/30 text-xs font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-40"
          >
            <Trash2 className="w-4 h-4" /> Permanently Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}

