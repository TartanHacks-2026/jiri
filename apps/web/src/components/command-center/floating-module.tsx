"use client";

import { motion } from "framer-motion";
import { ReactNode, useState, useEffect } from "react";
import { cn } from "@/lib/utils";

// Centered layout: All positions relative to TRUE CENTER (50%, 50%)
// Using safer 20%-80% range to prevent overflow on narrower screens
const MODULE_POSITIONS_DESKTOP = {
    tools: { left: "18%", top: "26%" },      // Top-left quadrant
    trace: { left: "82%", top: "26%" },      // Top-right quadrant
    voice: { left: "18%", top: "65%" },      // Bottom-left quadrant (moved higher)
    plan: { left: "82%", top: "65%" },       // Bottom-right quadrant (moved higher)
    stateRail: { left: "50%", top: "85%" },  // Bottom-center (moved higher)
} as const;

const MODULE_POSITIONS_MOBILE = {
    trace: { left: "50%", top: "40%" },
    tools: { left: "50%", top: "52%" },
    voice: { left: "50%", top: "64%" },
    plan: { left: "50%", top: "76%" },
    stateRail: { left: "50%", top: "88%" },
} as const;

interface FloatingModuleProps {
    position: keyof typeof MODULE_POSITIONS_DESKTOP;
    isFocused: boolean;
    children: ReactNode;
    className?: string;
}

/**
 * Floating module wrapper for radial layout around central orb
 * Uses subtle focus falloff instead of aggressive blur.
 */
export function FloatingModule({
    position,
    isFocused,
    children,
    className,
}: FloatingModuleProps) {
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const checkMobile = () => setIsMobile(window.innerWidth < 768);
        checkMobile();
        window.addEventListener("resize", checkMobile);
        return () => window.removeEventListener("resize", checkMobile);
    }, []);

    // On mobile (< 768px), modules stack vertically so we still need absolute positioning
    // On desktop, CSS Grid handles positioning, so we use relative
    const useAbsolutePositioning = isMobile;

    return (
        <motion.div
            className={cn(
                useAbsolutePositioning
                    ? "absolute max-w-md rounded-xl border border-border/40 bg-card/30 p-4 backdrop-blur-xl shadow-[0_0_20px_rgba(0,217,255,0.08)]"
                    : "relative max-w-md rounded-xl border border-border/40 bg-card/30 p-4 backdrop-blur-xl shadow-[0_0_20px_rgba(0,217,255,0.08)]",
                className
            )}
            style={useAbsolutePositioning ? {
                left: pos.left,
                top: pos.top,
                transform: "translate(-50%, -50%)",
            } : undefined}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{
                opacity: isFocused ? 1 : 0.82,
                scale: 1,
                filter: isFocused ? "blur(0px)" : "blur(0.8px)",
            }}
            transition={{ duration: 0.3, ease: "easeOut" }}
        >
            {children}
        </motion.div>
    );
}

// Export mobile positions for use in TechLines fallbacks.
export { MODULE_POSITIONS_MOBILE };
