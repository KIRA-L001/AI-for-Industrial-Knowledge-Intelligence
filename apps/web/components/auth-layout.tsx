"use client";

import { ArrowRight, BrainCircuit, FileSearch, Network, ShieldCheck } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { AuthSlideshow } from "@/components/auth-slideshow";

const HIGHLIGHTS = [
  { icon: FileSearch, text: "Citation-backed answers from your own documents" },
  { icon: Network, text: "A live industrial knowledge graph" },
  { icon: ShieldCheck, text: "Automated compliance & maintenance intelligence" },
];

/**
 * Split-screen authentication shell.
 * Left: KIRA brand/visual panel. Right: the form (passed as children).
 * Purely presentational — wraps existing auth forms without touching logic.
 */
export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: ReactNode;
  children: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-background p-3 sm:p-4">
      <div className="grid min-h-[calc(100vh-1.5rem)] overflow-hidden rounded-2xl border border-border/70 lg:grid-cols-2">
        {/* ── Visual panel ── */}
        <aside className="relative hidden flex-col justify-between overflow-hidden p-10 lg:flex">
          {/* Auto-sliding image backdrop */}
          <AuthSlideshow />

          <div className="relative z-10 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 text-lg font-semibold tracking-tight">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary text-primary-foreground">
                <BrainCircuit className="h-4.5 w-4.5" />
              </span>
              KIRA
            </Link>
            <Link
              href="/"
              className="group inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-medium backdrop-blur transition hover:bg-white/15"
            >
              Back to website
              <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-0.5" />
            </Link>
          </div>

          <div className="relative z-10 max-w-md">
            <h2 className="text-balance text-4xl font-semibold leading-tight tracking-tight">
              Turn plant documents into decisions you can trust.
            </h2>
            <ul className="mt-8 space-y-4">
              {HIGHLIGHTS.map(({ icon: Icon, text }) => (
                <li key={text} className="flex items-center gap-3 text-sm text-foreground/90">
                  <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-white/15 bg-white/10 text-primary backdrop-blur">
                    <Icon className="h-4 w-4" />
                  </span>
                  {text}
                </li>
              ))}
            </ul>
            <p className="mt-10 text-xs uppercase tracking-[0.2em] text-muted-foreground">
              Industrial AI Operating System
            </p>
          </div>
        </aside>

        {/* ── Form panel ── */}
        <section className="relative flex items-center justify-center overflow-y-auto bg-card px-6 py-10 sm:px-10">
          {/* Mobile brand + back link */}
          <div className="absolute left-6 right-6 top-6 flex items-center justify-between lg:hidden">
            <Link href="/" className="flex items-center gap-2 font-semibold">
              <span className="grid h-7 w-7 place-items-center rounded-lg bg-primary text-primary-foreground">
                <BrainCircuit className="h-4 w-4" />
              </span>
              KIRA
            </Link>
            <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
              Back to website →
            </Link>
          </div>

          <div className="w-full max-w-md">
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
            <div className="mt-8">{children}</div>
          </div>
        </section>
      </div>
    </main>
  );
}
