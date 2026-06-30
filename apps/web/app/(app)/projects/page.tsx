"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { useCreateProject, useProjects } from "@/lib/hooks/use-catalog";

export default function ProjectsPage() {
  const { data, isLoading } = useProjects();
  const create = useCreateProject();
  const [name, setName] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!name) return;
    await create.mutateAsync({ name });
    setName("");
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
        <p className="text-sm text-muted-foreground">Group documents and analysis by initiative.</p>
      </div>

      <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <label className="text-xs text-muted-foreground">Project name</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Turnaround 2026" className="w-72" />
        </div>
        <Button type="submit" disabled={create.isPending}>
          {create.isPending ? "Creating…" : "New project"}
        </Button>
      </form>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : (
        <Table>
          <THead>
            <TR>
              <TH>Name</TH>
              <TH>Status</TH>
              <TH>Created</TH>
            </TR>
          </THead>
          <TBody>
            {(data?.items ?? []).map((p) => (
              <TR key={p.id}>
                <TD className="font-medium">{p.name}</TD>
                <TD className="capitalize">{p.status}</TD>
                <TD>{new Date(p.created_at).toLocaleDateString()}</TD>
              </TR>
            ))}
            {data?.items.length === 0 && (
              <TR>
                <TD className="text-muted-foreground" colSpan={3}>
                  No projects yet.
                </TD>
              </TR>
            )}
          </TBody>
        </Table>
      )}
    </div>
  );
}
