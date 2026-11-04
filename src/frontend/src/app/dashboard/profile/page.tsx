"use client";

import React, { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { users, ApiError } from "@/services/api";
import {
  User as UserIcon,
  Mail,
  Calendar,
  Save,
  Trash2,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  ShieldAlert,
} from "lucide-react";

export default function ProfilePage() {
  const { user, refreshUser, logout } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [loading, setLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      await users.updateProfile({ name });
      await refreshUser();
      setSuccess("Profile information updated successfully.");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to update profile.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    const confirmed = prompt(
      "Type 'DELETE' to confirm permanent deletion of your AROHA account, associated connected tokens, and analytical records:"
    );

    if (confirmed !== "DELETE") {
      return;
    }

    setDeleteLoading(true);
    setError(null);

    try {
      await users.deleteAccount();
      window.location.href = "/";
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to delete account. Please try again.");
      }
      setDeleteLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-2xl font-extrabold text-[#17212B] tracking-tight">
          User Profile & Security
        </h1>
        <p className="text-xs text-[#636E72] mt-1">
          Manage your personal credentials and platform data rights
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

      {/* Profile Details Card */}
      <div className="p-6 rounded-3xl bg-white border border-gray-100 shadow-sm space-y-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#2A9D8F] to-[#A78BFA] text-white flex items-center justify-center text-2xl font-bold shadow-md">
            {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
          </div>
          <div>
            <h2 className="text-lg font-bold text-[#17212B]">{user?.name || "User"}</h2>
            <p className="text-xs text-[#636E72]">{user?.email}</p>
          </div>
        </div>

        <form onSubmit={handleUpdate} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-[#17212B] mb-1.5">
              Display Name
            </label>
            <div className="relative">
              <UserIcon size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your full name"
                className="w-full pl-10 pr-4 py-2.5 bg-[#F7F8F5] border border-gray-200 rounded-xl text-xs text-[#2D3436] focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F]"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#17212B] mb-1.5">
              Email Address (Immutable)
            </label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="email"
                disabled
                value={user?.email || ""}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-100 border border-gray-200 rounded-xl text-xs text-gray-500 cursor-not-allowed"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 rounded-xl text-xs font-semibold text-white bg-[#2A9D8F] hover:bg-[#238478] transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              {loading ? <Loader2 size={13} className="animate-spin" /> : <Save size={13} />}
              Save Changes
            </button>
          </div>
        </form>
      </div>

      {/* Account Deletion / Danger Zone */}
      <div className="p-6 rounded-3xl bg-red-50/60 border border-red-200/80 shadow-sm space-y-4">
        <div className="flex items-center gap-2 text-red-900 font-bold text-sm">
          <ShieldAlert size={18} className="text-red-600" />
          <span>Danger Zone: Permanent Account Deletion</span>
        </div>
        <p className="text-xs text-red-700 leading-relaxed">
          Deleting your account immediately purges your profile, associated Instagram OAuth tokens, media references, and link inspection history in compliance with privacy regulations.
        </p>

        <button
          onClick={handleDeleteAccount}
          disabled={deleteLoading}
          className="px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-red-600 hover:bg-red-700 transition-colors flex items-center gap-1.5 disabled:opacity-50"
        >
          {deleteLoading ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
          Permanently Delete Account
        </button>
      </div>
    </div>
  );
}

