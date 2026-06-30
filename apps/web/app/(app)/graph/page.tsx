"use client";

import { useMemo } from "react";
import ReactFlow, { Background, Controls, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";

import { Button } from "@/components/ui/button";
import { useGraph, useSyncGraph } from "@/lib/hooks/use-graph";

const LABEL_COLORS: Record<string, string> = {
  equipment: "#2563eb",
  standard: "#16a34a",
};

export default function GraphPage() {
  const { data, isLoading } = useGraph();
  const sync = useSyncGraph();

  const { nodes, edges } = useMemo(() => {
    const view = data ?? { nodes: [], edges: [] };
    const flowNodes: Node[] = view.nodes.map((n, i) => ({
      id: n.id,
      data: { label: `${n.name}` },
      position: { x: (i % 6) * 180, y: Math.floor(i / 6) * 120 },
      style: {
        background: LABEL_COLORS[n.label] ?? "hsl(var(--muted))",
        color: "white",
        border: "none",
        borderRadius: 8,
        fontSize: 12,
        padding: 8,
      },
    }));
    const flowEdges: Edge[] = view.edges.map((e, i) => ({
      id: `e-${i}`,
      source: e.source,
      target: e.target,
      label: e.rel_type,
      animated: true,
      style: { stroke: "hsl(var(--muted-foreground))" },
    }));
    return { nodes: flowNodes, edges: flowEdges };
  }, [data]);

  return (
    <div className="flex h-[calc(100vh-7rem)] flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Knowledge Graph</h1>
          <p className="text-sm text-muted-foreground">
            Equipment, standards, and their relationships.
          </p>
        </div>
        <Button onClick={() => sync.mutate()} disabled={sync.isPending}>
          {sync.isPending ? "Syncing…" : "Rebuild graph"}
        </Button>
      </div>
      <div className="flex-1 overflow-hidden rounded-xl border border-border bg-card">
        {isLoading ? (
          <p className="p-6 text-sm text-muted-foreground">Loading…</p>
        ) : nodes.length === 0 ? (
          <p className="p-6 text-sm text-muted-foreground">
            No graph yet. Analyze documents, then rebuild the graph.
          </p>
        ) : (
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background />
            <Controls />
          </ReactFlow>
        )}
      </div>
    </div>
  );
}
