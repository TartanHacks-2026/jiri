import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium backdrop-blur-sm",
  {
    variants: {
      variant: {
        default: "border-accent/30 bg-accent/10 text-accent shadow-[0_0_8px_rgba(0,217,255,0.2)]",
        secondary: "border-border/50 bg-card/40 text-foreground",
        success: "border-success/30 bg-success/10 text-success shadow-[0_0_8px_rgba(0,255,136,0.2)]",
        warning: "border-warning/30 bg-warning/10 text-warning",
        danger: "border-danger/30 bg-danger/10 text-danger",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps extends VariantProps<typeof badgeVariants> {
  className?: string;
  children: React.ReactNode;
}

export function Badge({ className, variant, children }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)}>{children}</div>;
}
