"use client";

import { Loader2, ShieldAlert } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function SignupPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/auth/login");
  }, [router]);

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-[#030307] p-4 text-white">
      {/* Background Glowing Orbs */}
      <div className="absolute top-1/4 left-1/4 h-[350px] w-[350px] rounded-full bg-violet-600/10 glow-glow animate-drift-slow" />
      <div className="absolute bottom-1/4 right-1/4 h-[400px] w-[400px] rounded-full bg-fuchsia-600/10 glow-glow animate-drift-medium" />

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff03_1px,transparent_1px),linear-gradient(to_bottom,#ffffff03_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />

      {/* Message Card */}
      <div className="relative z-10 w-full max-w-md animate-fade-in-up rounded-2xl glassmorphic-card p-8 text-center md:p-10">
        <div className="flex flex-col items-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-amber-500/10 text-amber-500 ring-4 ring-amber-500/5">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Registration Disabled</h1>
          <p className="mt-3 text-sm text-zinc-400 font-medium leading-relaxed">
            Public signups are disabled on this private AZS Solution&apos;s AI agent instance. Please contact your system administrator for access.
          </p>
          <div className="mt-8 flex items-center justify-center gap-2 text-xs text-zinc-500 font-semibold">
            <Loader2 className="h-4.5 w-4.5 animate-spin text-violet-500" />
            Redirecting to sign in page...
          </div>
        </div>
      </div>
    </div>
  );
}
