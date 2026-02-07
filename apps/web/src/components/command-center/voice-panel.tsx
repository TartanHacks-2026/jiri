"use client";

import { useMemo, useState } from "react";
import { Mic, SendHorizontal, User, Waves, WandSparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatTime } from "@/lib/utils";
import type { TranscriptLine } from "@/store/command-center-store";

interface VoicePanelProps {
  transcript: TranscriptLine[];
  partialTranscript: string;
  onSendText: (value: string) => void;
}

function iconForRole(role: TranscriptLine["role"]) {
  if (role === "assistant") {
    return <WandSparkles className="h-3.5 w-3.5 text-accent" />;
  }
  if (role === "system") {
    return <Waves className="h-3.5 w-3.5 text-warning" />;
  }

  return <User className="h-3.5 w-3.5 text-primary" />;
}

export function VoicePanel({ transcript, partialTranscript, onSendText }: VoicePanelProps) {
  const [input, setInput] = useState("");

  const recent = useMemo(() => transcript.slice(-14).reverse(), [transcript]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }

    onSendText(trimmed);
    setInput("");
  };

  return (
    <Card className="border-accent/20">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm uppercase tracking-[0.16em] text-muted-foreground">
          Voice + Conversation
        </CardTitle>
        <Button size="sm" variant="secondary" aria-label="Mic stub">
          <Mic className="mr-1 h-3.5 w-3.5" />
          Mic Stub
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="max-h-[290px] space-y-2 overflow-auto pr-1">
          {recent.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border/70 p-4 text-sm text-muted-foreground">
              Transcript will appear here.
            </div>
          ) : (
            recent.map((line) => (
              <div
                key={line.id}
                className="rounded-lg border border-border/65 bg-background/40 px-3 py-2"
              >
                <div className="mb-1 flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5 text-xs uppercase tracking-wide text-muted-foreground">
                    {iconForRole(line.role)}
                    {line.role}
                  </div>
                  <span className="font-mono text-[10px] text-muted-foreground">{formatTime(line.ts)}</span>
                </div>
                <p className="text-sm text-foreground">{line.text}</p>
              </div>
            ))
          )}

          {partialTranscript ? (
            <div className="rounded-lg border border-accent/45 bg-accent/10 px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-accent">Partial</p>
              <p className="text-sm text-foreground">{partialTranscript}</p>
            </div>
          ) : null}
        </div>

        <div className="flex items-center gap-2">
          <Input
            placeholder="Type fallback text or judge prompt..."
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleSubmit();
              }
            }}
          />
          <Button size="icon" onClick={handleSubmit}>
            <SendHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
