"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TBody, TD, TH, THead, TR } from "@/components/ui/table";
import { useCreateEquipment, useEquipment } from "@/lib/hooks/use-catalog";

export default function EquipmentPage() {
  const { data, isLoading } = useEquipment();
  const create = useCreateEquipment();
  const [tag, setTag] = useState("");
  const [name, setName] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!tag || !name) return;
    await create.mutateAsync({ tag, name });
    setTag("");
    setName("");
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Equipment</h1>
        <p className="text-sm text-muted-foreground">Industrial assets in your organization.</p>
      </div>

      <form onSubmit={onSubmit} className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <label className="text-xs text-muted-foreground">Tag</label>
          <Input value={tag} onChange={(e) => setTag(e.target.value)} placeholder="P-101" className="w-40" />
        </div>
        <div className="space-y-1">
          <label className="text-xs text-muted-foreground">Name</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Feed Pump" className="w-64" />
        </div>
        <Button type="submit" disabled={create.isPending}>
          {create.isPending ? "Adding…" : "Add equipment"}
        </Button>
      </form>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : (
        <Table>
          <THead>
            <TR>
              <TH>Tag</TH>
              <TH>Name</TH>
              <TH>Type</TH>
              <TH>Status</TH>
              <TH>Criticality</TH>
            </TR>
          </THead>
          <TBody>
            {(data?.items ?? []).map((e) => (
              <TR key={e.id}>
                <TD className="font-medium">{e.tag}</TD>
                <TD>{e.name}</TD>
                <TD>{e.equipment_type ?? "—"}</TD>
                <TD className="capitalize">{e.status}</TD>
                <TD className="capitalize">{e.criticality}</TD>
              </TR>
            ))}
            {data?.items.length === 0 && (
              <TR>
                <TD className="text-muted-foreground" colSpan={5}>
                  No equipment yet.
                </TD>
              </TR>
            )}
          </TBody>
        </Table>
      )}
    </div>
  );
}
