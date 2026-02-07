"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

// Module positions (radial layout around center)
const MODULE_POSITIONS = {
    trace: { left: "80%", top: "30%" },
    tools: { left: "20%", top: "30%" },
    artifacts: { left: "30%", top: "70%" },
    plan: { left: "70%", top: "70%" },
    stateRail: { left: "50%", top: "75%" },
} as const;

interface FloatingModuleProps {
    position: keyof typeof MODULE_POSITIONS;
    isFocused: boolean;
    children: ReactNode;
    className?: string;
}

/**
 * Floating module wrapper for radial layout around central orb
 * Blurs and fades to 20% opacity when focus mode is inactive
 */
export function FloatingModule({
    position,
    isFocused,
    children,
    className,
}: FloatingModuleProps) {
    const pos = MODULE_POSITIONS[position];

    return (
        <motion.div
            className={cn(
                "absolute max-w-md rounded-xl border border-border/40 bg-card/30 p-4 backdrop-blur-xl shadow-[0_0_20px_rgba(0,217,255,0.08)]",
                className
            )}
            style={{
                left: pos.left,
                top: pos.top,
                transform: "translate(-50%, -50%)",
            }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{
                opacity: isFocused ? 1 : 0.7,
                scale: 1,
                filter: isFocused ? "blur(0px)" : "blur(2px)",
            }}
            transition={{ duration: 0.3, ease: "easeOut" }}
        >
            {children}
        </motion.div>
    );
}

// Export positions for use in TechLines component
export { MODULE_POSITIONS };
