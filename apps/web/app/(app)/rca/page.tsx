import { AgentConsole } from "@/components/agent-console";

export default function RcaPage() {
  return (
    <AgentConsole
      agent="rca"
      title="Root Cause Analysis"
      description="Analyze incidents, determine probable root causes, and prevent recurrence."
      placeholder="e.g. Why did the compressor trip during startup?"
    />
  );
}
