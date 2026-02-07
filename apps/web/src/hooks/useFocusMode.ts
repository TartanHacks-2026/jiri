"use client";

import { useEffect, useState } from "react";

/**
 * Detects user inactivity for focus mode
 * Returns true when user is active, false after idleTimeout ms
 */
export function useFocusMode({ idleTimeout = 2000 }: { idleTimeout?: number }) {
    const [isFocused, setIsFocused] = useState(true);
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        // Check if mobile on mount and window resize
        const checkMobile = () => {
            setIsMobile(window.innerWidth < 768);
        };

        checkMobile();
        window.addEventListener("resize", checkMobile);

        // Mobile is always focused (no blur)
        if (isMobile) {
            setIsFocused(true);
            return () => window.removeEventListener("resize", checkMobile);
        }

        let timeout: NodeJS.Timeout;

        const handleActivity = () => {
            setIsFocused(true);
            clearTimeout(timeout);
            timeout = setTimeout(() => setIsFocused(false), idleTimeout);
        };

        // Trigger initial timeout
        handleActivity();

        window.addEventListener("mousemove", handleActivity);
        window.addEventListener("keydown", handleActivity);
        window.addEventListener("click", handleActivity);
        window.addEventListener("scroll", handleActivity);

        return () => {
            clearTimeout(timeout);
            window.removeEventListener("mousemove", handleActivity);
            window.removeEventListener("keydown", handleActivity);
            window.removeEventListener("click", handleActivity);
            window.removeEventListener("scroll", handleActivity);
            window.removeEventListener("resize", checkMobile);
        };
    }, [idleTimeout, isMobile]);

    return isFocused;
}
