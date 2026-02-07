"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface JarvisOrbProps {
    className?: string;
    transcript?: Array<{ role: string; text: string }>;
    partialTranscript?: string;
    isListening: boolean;
    isThinking?: boolean;
}

export function JarvisOrb({
    className,
    transcript = [],
    partialTranscript,
    isListening,
    isThinking = false,
}: JarvisOrbProps) {
    // Get last 3 transcript lines for display
    const recentLines = transcript.slice(-3);

    return (
        <div className={cn("relative", className)}>
            {/* Outer Ring - Smaller to prevent module overlap */}
            < motion.div
                className="absolute left-1/2 top-1/2 h-[220px] w-[220px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-accent/20 md:h-[280px] md:w-[280px]"
                animate={{
                    rotate: 360,
                }}
                transition={{
                    duration: 120,
                    repeat: Infinity,
                    ease: "linear",
                }}
            />

            {/* Main Sphere - Smaller to prevent overlap */}
            <motion.div
                className={cn(
                    "absolute left-1/2 top-1/2 h-[160px] w-[160px] -translate-x-1/2 -translate-y-1/2 rounded-full md:h-[200px] md:w-[200px]",
                    "bg-gradient-radial from-cyber-black via-accent/30 to-transparent",
                    "border-2 border-accent/40 backdrop-blur-xl",
                    isListening && "shadow-[0_0_60px_rgba(0,217,255,1)]"
                )}
                animate={
                    isListening
                        ? {
                            scale: [1, 1.02, 1],
                            boxShadow: [
                                "0 0 20px rgba(0, 217, 255, 0.6)",
                                "0 0 60px rgba(0, 217, 255, 1)",
                                "0 0 20px rgba(0, 217, 255, 0.6)",
                            ],
                        }
                        : {
                            scale: [1, 1.05, 1],
                            opacity: [0.9, 1, 0.9],
                        }
                }
                transition={{
                    duration: isListening ? 0.8 : 3,
                    repeat: Infinity,
                    ease: isListening ? "easeInOut" : [0.4, 0, 0.2, 1],
                }}
            >
                {/* Inner Pulse - Smaller to match new orb size */}
                <motion.div
                    className="absolute left-1/2 top-1/2 h-[120px] w-[120px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent/10 md:h-[160px] md:w-[160px]"
                    animate={{
                        scale: [0.95, 1.05, 0.95],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        ease: [0.4, 0, 0.2, 1],
                    }}
                />

                {/* Transcript Display */}
                <div className="absolute inset-0 flex flex-col items-center justify-center p-4 text-center md:p-8">
                    {recentLines.length === 0 && !partialTranscript ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-xs uppercase tracking-[0.2em] text-muted-foreground md:text-sm"
                        >
                            {isListening ? "Listening..." : "Ready"}
                        </motion.div>
                    ) : (
                        <div className="space-y-1 md:space-y-2">
                            {recentLines.map((line, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1 - i * 0.3, y: 0 }}
                                    className="text-xs text-foreground/80 md:text-sm"
                                >
                                    <span className="font-mono text-xs text-accent">
                                        {line.role === "user" ? "YOU" : "JIRI"}:
                                    </span>{" "}
                                    {line.text}
                                </motion.div>
                            ))}

                            {partialTranscript && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="text-xs text-accent md:text-sm"
                                >
                                    <span className="font-mono text-[10px] md:text-xs">PARTIAL:</span> {partialTranscript}
                                </motion.div>
                            )}
                        </div>
                    )}

                    {isThinking && (
                        <motion.div
                            className="mt-4 flex gap-1"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            {[0, 1, 2].map((i) => (
                                <motion.div
                                    key={i}
                                    className="h-2 w-2 rounded-full bg-accent"
                                    animate={{
                                        y: [-4, 4, -4],
                                        opacity: [0.4, 1, 0.4],
                                    }}
                                    transition={{
                                        duration: 0.8,
                                        repeat: Infinity,
                                        delay: i * 0.2,
                                    }}
                                />
                            ))}
                        </motion.div>
                    )}
                </div>
            </motion.div>

            {/* Audio Visualizer Placeholder (for future) */}
            {
                isListening && (
                    <div className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                        {/* Future: Add radial frequency bars here */}
                    </div>
                )
            }
        </div >
    );
}
