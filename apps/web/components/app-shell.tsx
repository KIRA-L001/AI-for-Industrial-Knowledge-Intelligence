"use client";

import {
  BarChart3,
  Boxes,
  FileText,
  FolderKanban,
  LayoutDashboard,
  MessageSquare,
  Network,
  Settings,
  ShieldCheck,
  Wrench,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { useAuthStore } from "@/lib/auth-store";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/copilot", label: "AI Copilot", icon: MessageSquare },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/graph", label: "Knowledge Graph", icon: Network },
  { href: "/equipment", label: "Equipment", icon: Boxes },
  { href: "/projects", label: "Projects", icon: FolderKanban },
  { href: "/maintenance", label: "Maintenance", icon: Wrench },
  { href: "/compliance", label: "Compliance", icon: ShieldCheck },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
] as const;

/** Authenticated layout: persistent sidebar + top bar. Redirects to /login. */
export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, user, clear } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) router.replace("/login");
  }, [isAuthenticated, router]);

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-64 shrink-0 border-r border-border bg-card md:block">
        <div className="flex h-16 items-center px-6 text-lg font-semibold tracking-tight">
          KIRA
        </div>
        <nav className="space-y-1 px-3 py-2">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-border px-6">
          <span className="text-sm text-muted-foreground">
            {user?.full_name ? `${user.full_name} · ${user.role}` : ""}
          </span>
          <button
            onClick={() => {
              clear();
              router.replace("/login");
            }}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Sign out
          </button>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
