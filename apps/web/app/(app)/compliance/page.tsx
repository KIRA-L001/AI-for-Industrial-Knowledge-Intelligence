import { AgentConsole } from "@/components/agent-console";

export default function CompliancePage() {
  return (
    <AgentConsole
      agent="compliance"
      title="Compliance Intelligence"
      description="Map operations to Factory Act / OISD / PESO requirements and find gaps."
      placeholder="e.g. Are our pressure vessels compliant with OISD-STD-105?"
    />
  );
}
