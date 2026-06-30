"use client";

import { Bot, Send, User } from "lucide-react";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useAgents, useChat, type Citation, type ChatTurn } from "@/lib/hooks/use-copilot";

interface DisplayMessage extends ChatTurn {
  agent?: string;
  confidence?: number;
  confidenceLabel?: string;
  citations?: Citation[];
}

const CONFIDENCE_STYLES: Record<string, string> = {
  high: "bg-green-500/15 text-green-500",
  medium: "bg-amber-500/15 text-amber-500",
  low: "bg-destructive/15 text-destructive",
};

export default function CopilotPage() {
  const { data: agents } = useAgents();
  const chat = useChat();
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [agent, setAgent] = useState<string>("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || chat.isPending) return;

    const history: ChatTurn[] = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");

    try {
      const res = await chat.mutateAsync({ message: text, agent: agent || null, history });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer,
          agent: res.agent,
          confidence: res.confidence,
          confidenceLabel: res.confidence_label,
          citations: res.citations,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong answering that." },
      ]);
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-3xl flex-col">
      <div className="flex items-center justify-between pb-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">AI Copilot</h1>
          <p className="text-sm text-muted-foreground">Citation-backed industrial intelligence.</p>
        </div>
        <select
          value={agent}
          onChange={(e) => setAgent(e.target.value)}
          className="h-9 rounded-lg border border-border bg-background px-3 text-sm"
        >
          <option value="">Auto-route</option>
          {agents?.map((a) => (
            <option key={a.key} value={a.key}>
              {a.title}
            </option>
          ))}
        </select>
      </div>

      <div className="flex-1 space-y-6 overflow-auto rounded-xl border border-border bg-card p-6">
        {messages.length === 0 && (
          <p className="pt-10 text-center text-sm text-muted-foreground">
            Ask about equipment, maintenance, compliance, or root-cause analysis.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className="flex gap-3">
            <div className="mt-1 shrink-0">
              {m.role === "user" ? (
                <User className="h-5 w-5 text-muted-foreground" />
              ) : (
                <Bot className="h-5 w-5 text-primary" />
              )}
            </div>
            <div className="min-w-0 flex-1 space-y-2">
              {m.role === "assistant" && m.agent && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="rounded bg-primary/10 px-2 py-0.5 capitalize text-primary">
                    {m.agent}
                  </span>
                  {m.confidenceLabel && (
                    <span
                      className={cn(
                        "rounded px-2 py-0.5 capitalize",
                        CONFIDENCE_STYLES[m.confidenceLabel] ?? "",
                      )}
                    >
                      {m.confidenceLabel} confidence ({Math.round((m.confidence ?? 0) * 100)}%)
                    </span>
                  )}
                </div>
              )}
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
              {m.citations && m.citations.length > 0 && (
                <div className="space-y-1 border-l-2 border-border pl-3">
                  <p className="text-xs font-medium text-muted-foreground">Sources</p>
                  {m.citations.map((c) => (
                    <p key={c.chunk_id} className="text-xs text-muted-foreground">
                      [{c.index}] {c.text.slice(0, 140)}
                      {c.text.length > 140 ? "…" : ""}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {chat.isPending && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Bot className="h-5 w-5 text-primary" /> Thinking…
          </div>
        )}
      </div>

      <form onSubmit={onSubmit} className="flex gap-2 pt-4">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the Copilot…"
          disabled={chat.isPending}
        />
        <Button type="submit" size="icon" disabled={chat.isPending || !input.trim()}>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
