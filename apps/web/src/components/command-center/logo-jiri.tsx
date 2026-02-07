import { cn } from "@/lib/utils";

interface LogoJiriProps {
  className?: string;
}

export function LogoJiri({ className }: LogoJiriProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      <div className="relative h-9 w-9 rounded-lg border border-accent/40 bg-card/90 shadow-glow transition-all duration-300 hover:shadow-[0_0_30px_rgba(0,255,136,0.6)] hover:scale-105">
        <svg
          viewBox="0 0 36 36"
          className="absolute inset-0 h-full w-full"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden
        >
          <circle cx="18" cy="18" r="14" stroke="hsl(var(--accent))" strokeOpacity="0.45" />
          <path d="M8 20C12 10 24 9 28 19" stroke="hsl(var(--primary))" strokeWidth="2.2" />
          <circle cx="11" cy="17" r="2.2" fill="hsl(var(--primary))" />
          <circle cx="25" cy="15" r="1.8" fill="hsl(var(--accent))" />
        </svg>
      </div>
      <div>
        <div className="text-sm font-semibold uppercase tracking-[0.28em] text-foreground">JIRI</div>
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
          Command Center
        </div>
      </div>
    </div>
  );
}
