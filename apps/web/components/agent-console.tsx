"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useChat, type Citation } from "@/lib/hooks/use-copilot";

interface Props {
  agent: string;
  title: string;
  description: string;
  placeholder: string;
}

/** A focused single-agent Q&A console reused by the maintenance/compliance/RCA pages. */
export function AgentConsole({ agent, title, description, placeholder }: Props) {
  const chat = useChat();
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || chat.isPending) return;
    const res = await chat.mutateAsync({ message: text, agent, history: [] });
    setAnswer(res.answer);
    setConfidence(res.confidence);
    setCitations(res.citations);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <form onSubmit={onSubmit} className="flex gap-2">
        <Input value={input} onChange={(e) => setInput(e.target.value)} placeholder={placeholder} />
        <Button type="submit" disabled={chat.isPending || !input.trim()}>
          {chat.isPending ? "Analyzing…" : "Ask"}
        </Button>
      </form>
      {answer && (
        <Card>
          <CardContent className="space-y-3 pt-6">
            {confidence !== null && (
              <span className="rounded bg-primary/10 px-2 py-0.5 text-xs text-primary">
                Confidence {Math.round(confidence * 100)}%
              </span>
            )}
            <p className="whitespace-pre-wrap text-sm leading-relaxed">{answer}</p>
            {citations.length > 0 && (
              <div className="space-y-1 border-l-2 border-border pl-3">
                <p className="text-xs font-medium text-muted-foreground">Sources</p>
                {citations.map((c) => (
                  <p key={c.chunk_id} className="text-xs text-muted-foreground">
                    [{c.index}] {c.text.slice(0, 160)}
                    {c.text.length > 160 ? "…" : ""}
                  </p>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
