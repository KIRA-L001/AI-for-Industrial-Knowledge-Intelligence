import { AgentConsole } from "@/components/agent-console";

export default function MaintenancePage() {
  return (
    <AgentConsole
      agent="maintenance"
      title="Maintenance Intelligence"
      description="Analyze maintenance history, predict failures, and get recommended actions."
      placeholder="e.g. What are the common failure modes for pump P-101?"
    />
  );
}
