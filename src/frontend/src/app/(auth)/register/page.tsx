"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { auth, ApiError } from "@/services/api";
import { User, Mail, Lock, Eye, EyeOff, Loader2, AlertCircle, Check } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasLength = password.length >= 8;
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasDigit = /[0-9]/.test(password);
  const passwordsMatch = password.length > 0 && password === confirmPassword;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!hasLength || !hasLetter || !hasDigit) {
      setError("Password must be at least 8 characters and contain both letters and digits.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await auth.register({ name, email, password });
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to create account. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6 text-center">
        <h3 className="text-xl font-bold text-[#17212B]">Create an account</h3>
        <p className="text-xs text-[#636E72] mt-1">
          Join AROHA to start monitoring your multimedia content integrity
        </p>
      </div>

      {error && (
        <div className="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2.5">
          <AlertCircle size={16} className="shrink-0 mt-0.5 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-[#17212B] mb-1.5">
            Full name
          </label>
          <div className="relative">
            <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Alex Parker"
              className="w-full pl-10 pr-4 py-2.5 bg-[#F7F8F5] border border-gray-200 rounded-xl text-sm text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] transition-all"
            />
          </div>
        </div>

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
              placeholder="alex@domain.com"
              className="w-full pl-10 pr-4 py-2.5 bg-[#F7F8F5] border border-gray-200 rounded-xl text-sm text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] transition-all"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#17212B] mb-1.5">
            Password
          </label>
          <div className="relative">
            <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 chars with letters & digits"
              className="w-full pl-10 pr-11 py-2.5 bg-[#F7F8F5] border border-gray-200 rounded-xl text-sm text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] transition-all"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#17212B] mb-1.5">
            Confirm password
          </label>
          <div className="relative">
            <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type={showPassword ? "text" : "password"}
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat password"
              className="w-full pl-10 pr-4 py-2.5 bg-[#F7F8F5] border border-gray-200 rounded-xl text-sm text-[#2D3436] placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#2A9D8F]/30 focus:border-[#2A9D8F] transition-all"
            />
          </div>
        </div>

        {/* Password strength indicators */}
        <div className="grid grid-cols-2 gap-2 text-[11px] text-[#636E72] pt-1">
          <div className={`flex items-center gap-1.5 ${hasLength ? "text-emerald-600" : ""}`}>
            <Check size={12} className={hasLength ? "opacity-100" : "opacity-30"} /> 8+ Characters
          </div>
          <div className={`flex items-center gap-1.5 ${hasLetter && hasDigit ? "text-emerald-600" : ""}`}>
            <Check size={12} className={hasLetter && hasDigit ? "opacity-100" : "opacity-30"} /> Letters & Digits
          </div>
          <div className={`flex items-center gap-1.5 col-span-2 ${passwordsMatch ? "text-emerald-600" : ""}`}>
            <Check size={12} className={passwordsMatch ? "opacity-100" : "opacity-30"} /> Passwords Match
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 py-3 px-4 rounded-xl font-semibold text-sm text-white bg-[#2A9D8F] hover:bg-[#238478] focus:ring-4 focus:ring-[#2A9D8F]/20 transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-70 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 size={16} className="animate-spin" /> Creating account...
            </>
          ) : (
            "Create Account"
          )}
        </button>
      </form>

      <div className="mt-6 text-center text-xs text-[#636E72]">
        Already have an account?{" "}
        <Link href="/login" className="font-semibold text-[#2A9D8F] hover:underline">
          Sign in
        </Link>
      </div>
    </div>
  );
}

