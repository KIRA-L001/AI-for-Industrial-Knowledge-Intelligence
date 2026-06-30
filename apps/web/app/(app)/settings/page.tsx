"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore } from "@/lib/auth-store";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);

  const rows: { label: string; value: string }[] = [
    { label: "Name", value: user?.full_name ?? "—" },
    { label: "Email", value: user?.email ?? "—" },
    { label: "Role", value: user?.role ?? "—" },
    { label: "Organization ID", value: user?.organization_id ?? "—" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">Your account and organization.</p>
      </div>
      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle className="text-base">Profile</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {rows.map((r) => (
            <div key={r.label} className="flex justify-between border-b border-border pb-2 text-sm">
              <span className="text-muted-foreground">{r.label}</span>
              <span className="font-medium capitalize">{r.value}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
