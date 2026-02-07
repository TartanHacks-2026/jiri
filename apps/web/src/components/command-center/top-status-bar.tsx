import { Cable, PlayCircle, Radio, Square, Store } from "lucide-react";

import { LogoJiri } from "@/components/command-center/logo-jiri";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { shortId } from "@/lib/utils";
import type { ConnectionStatus } from "@/store/command-center-store";

interface TopStatusBarProps {
  connectionStatus: ConnectionStatus;
  sessionId: string;
  onStartLive: () => void;
  onStop: () => void;
  onRunDemo: () => void;
  onOpenMarketplace: () => void;
}

function statusBadgeVariant(status: ConnectionStatus): "success" | "warning" | "secondary" {
  switch (status) {
    case "connected":
      return "success";
    case "degraded":
      return "warning";
    case "replay":
      return "secondary";
    default:
      return "secondary";
  }
}

export function TopStatusBar({
  connectionStatus,
  sessionId,
  onStartLive,
  onStop,
  onRunDemo,
  onOpenMarketplace,
}: TopStatusBarProps) {
  return (
    <Card className="border-accent/20 bg-card/70">
      <CardContent className="flex flex-wrap items-center justify-between gap-3 p-3">
        <LogoJiri />

        <div className="flex items-center gap-2">
          <Badge variant={statusBadgeVariant(connectionStatus)} className="uppercase tracking-widest">
            <Cable className="mr-1 h-3 w-3" />
            {connectionStatus}
          </Badge>
          <Badge variant="secondary" className="font-mono uppercase tracking-widest">
            SID {shortId(sessionId, 10)}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="secondary" onClick={onOpenMarketplace}>
            <Store className="mr-1 h-3.5 w-3.5" />
            Tools
          </Button>
          <Button size="sm" variant="outline" onClick={onRunDemo}>
            <PlayCircle className="mr-1 h-3.5 w-3.5" />
            Run Demo
          </Button>
          <Button size="sm" onClick={onStartLive}>
            <Radio className="mr-1 h-3.5 w-3.5" />
            Start Live
          </Button>
          <Button size="sm" variant="danger" onClick={onStop}>
            <Square className="mr-1 h-3.5 w-3.5" />
            Stop
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
