"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";

interface TechLinesProps {
    /**
     * List of active modules to draw lines to
     */
    activeModules: string[];
    /**
     * Center position of the orb (usually 50%, 50%)
     */
    orbCenter: { x: string; y: string };
}

// Module positions matching CSS Grid cells (5x5 grid)
// Grid cells translate to approximate percentages:
// col-2/row-2 ≈ 33%, 33%  |  col-4/row-2 ≈ 67%, 33%
// col-2/row-4 ≈ 33%, 67%  |  col-4/row-4 ≈ 67%, 67%
// col-3/row-5 ≈ 50%, 83%
const MODULE_POSITIONS: Record<string, { x: number; y: number }> = {
    tools: { x: 33, y: 33 },      // Grid cell (2,2) - Top-left
    trace: { x: 67, y: 33 },      // Grid cell (4,2) - Top-right
    voice: { x: 33, y: 67 },      // Grid cell (2,4) - Bottom-left
    plan: { x: 67, y: 67 },       // Grid cell (4,4) - Bottom-right
    stateRail: { x: 50, y: 83 },  // Grid cell (3,5) - Bottom-center
};

/**
 * Generate curved SVG path from orb center to module
 */
function generateCurvedPath(
    fromX: number,
    fromY: number,
    toX: number,
    toY: number
): string {
    const midX = (fromX + toX) / 2;
    const midY = (fromY + toY) / 2;

    // Add curve control point offset for organic feel
    const curveOffset = -50;

    return `M ${fromX},${fromY} Q ${midX},${midY + curveOffset} ${toX},${toY}`;
}

/**
 * Tech Lines component - draws animated SVG lines from orb to active modules
 */
export function TechLines({ activeModules, orbCenter }: TechLinesProps) {
    // Convert percentage strings to viewport coordinates
    const orbX = parseFloat(orbCenter.x);
    const orbY = parseFloat(orbCenter.y);

    const paths = useMemo(() => {
        return activeModules
            .filter((module) => MODULE_POSITIONS[module])
            .map((module) => {
                const pos = MODULE_POSITIONS[module];
                const path = generateCurvedPath(orbX, orbY, pos.x, pos.y);

                return {
                    module,
                    path,
                };
            });
    }, [activeModules, orbX, orbY]);

    if (paths.length === 0) return null;

    return (
        <svg
            className="pointer-events-none absolute inset-0 h-full w-full"
            style={{ zIndex: 1 }}
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
        >
            {paths.map(({ module, path }) => (
                <motion.path
                    key={module}
                    d={path}
                    stroke="rgba(0, 217, 255, 0.4)"
                    strokeWidth="0.2"
                    fill="none"
                    strokeDasharray="2 1"
                    initial={{ strokeDashoffset: 100 }}
                    animate={{ strokeDashoffset: 0 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                />
            ))}
        </svg>
    );
}
