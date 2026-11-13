"use client";

import React, { useState, useEffect } from "react";
import { instagram, consent, type InstagramAccount, type ConsentRecord, ApiError } from "@/services/api";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Lock,
  RefreshCw,
  UserPlus,
  KeyRound,
} from "lucide-react";
import { InstagramIcon } from "@/components/icons/InstagramIcon";

export default function SettingsPage() {
  const [account, setAccount] = useState<InstagramAccount | null>(null);
  const [consents, setConsents] = useState<Record<string, ConsentRecord>>({});
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Any-account connection inputs
  const [customUsername, setCustomUsername] = useState("");
  const [customToken, setCustomToken] = useState("");
  const [showSwitchForm, setShowSwitchForm] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      try {
        const acc = await instagram.getAccount();
        setAccount(acc);
      } catch {
        setAccount(null);
      }

      try {
        const c = await consent.getAll();
        setConsents(c || {});
      } catch {
        // empty
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleConnectInstagram = async () => {
    setError(null);
    setActionLoading(true);
    try {
      const res = await instagram.getConnectUrl();
      if (res && res.url) {
        window.location.href = res.url;
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Meta API configuration missing. Ensure META_APP_ID and META_APP_SECRET are configured.");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleConnectCustomAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customUsername.trim() && !customToken.trim()) {
      setError("Please enter an Instagram handle (e.g. @aroha_lmt) or paste a Meta Graph API Access Token.");
      return;
    }
    setError(null);
    setSuccess(null);
    setActionLoading(true);
    try {
      const res = await instagram.connectCustomAccount({
        username: customUsername.trim() || undefined,
        access_token: customToken.trim() || undefined,
      });
      await loadData();
      setCustomUsername("");
      setCustomToken("");
      setShowSwitchForm(false);
      setSuccess(`Successfully connected @${res.username} and completed full multimedia integrity scan!`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to connect Instagram account.");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleSyncAccount = async () => {
    setActionLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await instagram.sync();
      await loadData();
      setSuccess(res.detail || "Synced Instagram metrics and re-audited all Reels & Bio!");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to sync account.");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (!confirm("Are you sure you want to disconnect this Instagram account? Associated OAuth tokens will be permanently erased.")) {
      return;
    }

    setActionLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await instagram.disconnect();
      setAccount(null);
      setSuccess("Instagram account disconnected successfully.");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to disconnect account.");
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleToggleConsent = async (type: "media_retention" | "model_training", currentStatus: boolean) => {
    setError(null);
    setSuccess(null);
    try {
      const updated = await consent.update(type, !currentStatus);
      setConsents((prev) => ({
        ...prev,
        [type]: updated,
      }));
      setSuccess(`Updated ${type === "media_retention" ? "Media Retention" : "Model Research Opt-In"} preference.`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to update consent preferences.");
      }
    }
  };

  const mediaRetentionGranted = consents["media_retention"]?.consent_status === "granted";
  const modelTrainingGranted = consents["model_training"]?.consent_status === "granted";

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          Settings & Account Connections
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Manage official Meta API integrations, multi-account creator connections, and privacy consents
        </p>
      </div>

      {error && (
        <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
          <AlertTriangle size={16} className="shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-700 flex items-center gap-2">
          <CheckCircle2 size={16} className="shrink-0 text-emerald-600" />
          <span>{success}</span>
        </div>
      )}

      {/* Instagram Official Integration */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 text-white flex items-center justify-center shadow-md">
              <InstagramIcon size={24} />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#17212B]">Official Instagram Graph API Connection</h2>
              <p className="text-xs text-[#636E72] mt-0.5">
                Connect any Instagram Creator or Business account via Meta OAuth or Graph API Token
              </p>
            </div>
          </div>
        </div>

        {account && (
          <div className="p-5 rounded-2xl bg-[#F7F8F5] border border-gray-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-[#17212B]">@{account.username}</span>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">
                  Connected
                </span>
              </div>
              <p className="text-xs text-[#636E72] mt-1 font-mono">
                Platform ID: {account.platform_user_id} • Connected {new Date(account.connected_at).toLocaleDateString()}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={handleSyncAccount}
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#2A9D8F] bg-white border border-[#2A9D8F]/30 hover:bg-teal-50 transition-colors disabled:opacity-50"
              >
                <RefreshCw size={13} className={actionLoading ? "animate-spin" : ""} />
                Sync & Audit
              </button>
              <button
                onClick={() => setShowSwitchForm(!showSwitchForm)}
                disabled={actionLoading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#17212B] bg-white border border-gray-200 hover:bg-gray-100 transition-colors disabled:opacity-50"
              >
                <UserPlus size={13} />
                Switch Account
              </button>
              <button
                onClick={handleDisconnect}
                disabled={actionLoading}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold text-red-600 bg-white border border-red-200 hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                Disconnect
              </button>
            </div>
          </div>
        )}

        {(!account || showSwitchForm) && (
          <div className="space-y-5 pt-2">
            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200 text-xs text-[#636E72] space-y-2">
              <div className="flex items-center gap-2 font-semibold text-[#17212B]">
                <Lock size={14} className="text-[#2A9D8F]" /> Multi-Account Creator Connection (Zero Password Required):
              </div>
              <ul className="list-disc pl-5 space-y-1 text-[11px]">
                <li>Connect via one-click Meta OAuth, or enter <strong>any Instagram Creator/Business handle</strong> or <strong>Meta Graph API Token</strong> below.</li>
                <li>Access tokens are encrypted at rest via symmetric Fernet cryptography.</li>
                <li>Connecting an account automatically fetches/seeds its Reels & Bio and executes a full 3-layer integrity scan.</li>
              </ul>
            </div>

            <form onSubmit={handleConnectCustomAccount} className="p-5 rounded-2xl bg-[#F7F8F5] border border-gray-200/80 space-y-4">
              <p className="text-xs font-bold text-[#17212B] uppercase tracking-wider">
                Connect Any Instagram Creator / Business Account
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#17212B] mb-1">
                    Instagram Handle (Any Creator Account)
                  </label>
                  <div className="relative">
                    <UserPlus size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      placeholder="e.g. @aroha_lmt or @creator_handle"
                      value={customUsername}
                      onChange={(e) => setCustomUsername(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 rounded-xl bg-white border border-gray-200 text-xs text-[#17212B] focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F]"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#17212B] mb-1">
                    Meta Graph API Access Token <span className="text-gray-400 font-normal">(Optional)</span>
                  </label>
                  <div className="relative">
                    <KeyRound size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="password"
                      placeholder="IG... or EAA... live token"
                      value={customToken}
                      onChange={(e) => setCustomToken(e.target.value)}
                      className="w-full pl-9 pr-3 py-2 rounded-xl bg-white border border-gray-200 text-xs text-[#17212B] focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F]"
                    />
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-1">
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#2A9D8F] hover:bg-[#238478] transition-all shadow-sm disabled:opacity-50"
                >
                  {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <InstagramIcon size={14} />}
                  Connect Account & Run Audit
                </button>

                <button
                  type="button"
                  onClick={handleConnectInstagram}
                  disabled={actionLoading}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-[#17212B] hover:bg-gray-800 transition-all shadow-sm disabled:opacity-50"
                >
                  {actionLoading ? <Loader2 size={14} className="animate-spin" /> : <InstagramIcon size={14} />}
                  One-Click Meta OAuth (@aroha_lmt)
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Academic Privacy & Informed Consent System */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-6">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck size={20} className="text-[#2A9D8F]" />
            <h2 className="text-base font-bold text-[#17212B]">Data Retention & Informed Consent Policy</h2>
          </div>
          <p className="text-xs text-[#636E72] mt-1">
            AROHA enforces strict academic and ethical compliance. We never store or train on your media without explicit granular consent.
          </p>
        </div>

        <div className="divide-y divide-gray-100">
          {/* Consent 1: Media Retention */}
          <div className="py-4 flex items-center justify-between gap-4">
            <div className="max-w-xl">
              <p className="text-sm font-bold text-[#17212B]">Historical Media Retention</p>
              <p className="text-xs text-[#636E72] mt-0.5 leading-relaxed">
                Allow AROHA to temporarily retain reference WAV audio fingerprints and video checksums so you can perform longitudinal change comparisons over time.
              </p>
            </div>
            <button
              onClick={() => handleToggleConsent("media_retention", mediaRetentionGranted)}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                mediaRetentionGranted ? "bg-[#2A9D8F]" : "bg-gray-200"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  mediaRetentionGranted ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
          </div>

          {/* Consent 2: Model Training */}
          <div className="py-4 flex items-center justify-between gap-4">
            <div className="max-w-xl">
              <p className="text-sm font-bold text-[#17212B]">AI Model Research Opt-In</p>
              <p className="text-xs text-[#636E72] mt-0.5 leading-relaxed">
                Explicitly permit anonymized audio-visual lip synchronization feature vectors to be included in our held-out MCA academic evaluation dataset.
              </p>
            </div>
            <button
              onClick={() => handleToggleConsent("model_training", modelTrainingGranted)}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                modelTrainingGranted ? "bg-[#2A9D8F]" : "bg-gray-200"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  modelTrainingGranted ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
