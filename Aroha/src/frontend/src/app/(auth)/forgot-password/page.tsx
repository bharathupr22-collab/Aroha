"use client";

import React, { useState } from "react";
import Link from "next/link";
import { auth, ApiError } from "@/services/api";
import { Mail, ArrowLeft, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await auth.forgotPassword(email);
      setSubmitted(true);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to process request. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6 text-center">
        <h3 className="text-xl font-bold text-[#17212B]">Password Reset</h3>
        <p className="text-xs text-[#636E72] mt-1">
          Enter your registered email and we&apos;ll check for your account instructions
        </p>
      </div>

      {submitted ? (
        <div className="text-center py-4">
          <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <CheckCircle2 size={24} />
          </div>
          <h4 className="text-sm font-bold text-[#17212B] mb-1">Check your inbox</h4>
          <p className="text-xs text-[#636E72] leading-relaxed mb-6">
            If an account exists with <span className="font-semibold text-[#17212B]">{email}</span>, password reset instructions have been recorded.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-xs font-semibold text-[#2A9D8F] hover:underline"
          >
            <ArrowLeft size={14} /> Back to Sign In
          </Link>
        </div>
      ) : (
        <>
          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2.5">
              <AlertCircle size={16} className="shrink-0 mt-0.5 text-red-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#17212B] mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@domain.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-[#F7F8F5] border border-gray-200 rounded-xl text-sm text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 rounded-xl font-semibold text-sm text-white bg-[#2A9D8F] hover:bg-[#238478] focus:ring-4 focus:ring-[#2A9D8F]/20 transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Sending instructions...
                </>
              ) : (
                "Send Reset Instructions"
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 text-xs font-semibold text-[#636E72] hover:text-[#17212B] transition-colors"
            >
              <ArrowLeft size={14} /> Back to Sign In
            </Link>
          </div>
        </>
      )}
    </div>
  );
}

