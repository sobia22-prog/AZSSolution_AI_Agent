"use client";

import { KeyRound, Mail, Shield, Sparkles } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { loginApiV1AuthLoginPost } from "@/client/sdk.gen";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await loginApiV1AuthLoginPost({
        body: { email, password },
      });

      if (res.error || !res.data) {
        const detail = (res.error as { detail?: string })?.detail;
        toast.error(detail || "Login failed");
        return;
      }

      // Set httpOnly cookies via server route
      await fetch("/api/auth/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: res.data.token, user: res.data.user }),
      });

      window.location.href = "/after-sign-in";
    } catch {
      toast.error("An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-[#030307] p-4 text-white">
      {/* Background Glowing Orbs */}
      <div className="absolute top-1/4 left-1/4 h-[350px] w-[350px] rounded-full bg-violet-600/10 glow-glow animate-drift-slow" />
      <div className="absolute bottom-1/4 right-1/4 h-[400px] w-[400px] rounded-full bg-fuchsia-600/10 glow-glow animate-drift-medium" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md animate-fade-in-up rounded-2xl glassmorphic-card p-8 md:p-10">
        <div className="flex flex-col items-center text-center">
          {/* Futuristic Audio Wave Branding */}
          <div className="mb-4 flex items-center justify-center gap-1.5 h-10">
            <span className="w-1.5 h-4 rounded-full bg-violet-500 animate-soundwave-1" />
            <span className="w-1.5 h-7 rounded-full bg-violet-400 animate-soundwave-2" />
            <span className="w-1.5 h-10 rounded-full bg-fuchsia-500 animate-soundwave-3" />
            <span className="w-1.5 h-6 rounded-full bg-violet-400 animate-soundwave-4" />
            <span className="w-1.5 h-3 rounded-full bg-violet-500 animate-soundwave-5" />
          </div>

          <h1 className="text-2xl font-black tracking-tight bg-gradient-to-r from-violet-200 via-white to-fuchsia-200 bg-clip-text text-transparent flex items-center gap-2">
            AZS Solution&apos;s AI agent
            <Sparkles className="w-5 h-5 text-fuchsia-400 animate-pulse" />
          </h1>
          <p className="mt-2 text-sm text-zinc-400 font-medium">
            Enter your admin credentials to access the console
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5" />
              Email Address
            </Label>
            <div className="relative">
              <Input
                id="email"
                type="email"
                placeholder="admin@azs-solution.ai"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-white/[0.04] border-white/[0.08] text-white placeholder-zinc-500 focus:bg-white/[0.06] focus:border-violet-500/50 focus:ring-violet-500/20 transition-all duration-300 rounded-lg h-11"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
              <KeyRound className="w-3.5 h-3.5" />
              Password
            </Label>
            <div className="relative">
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-white/[0.04] border-white/[0.08] text-white placeholder-zinc-500 focus:bg-white/[0.06] focus:border-violet-500/50 focus:ring-violet-500/20 transition-all duration-300 rounded-lg h-11"
              />
            </div>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-semibold rounded-lg h-11 transition-all duration-300 shadow-[0_0_20px_rgba(139,92,246,0.35)] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none mt-6 flex items-center justify-center gap-2 cursor-pointer"
          >
            {loading ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Signing in...
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                Sign in to AZS Solution&apos;s AI agent
              </>
            )}
          </Button>
        </form>

        <div className="mt-8 border-t border-white/[0.06] pt-6 text-center">
          <p className="text-xs text-zinc-500 font-medium">
            AZS Solution&apos;s AI agent Voice AI System • Private Console
          </p>
        </div>
      </div>
    </div>
  );
}
