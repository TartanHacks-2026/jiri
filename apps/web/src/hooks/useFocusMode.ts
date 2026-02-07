"use client";

import { useEffect, useState } from "react";

interface UseFocusModeOptions {
    /**
     * Time in milliseconds before focus mode activates (peripherals blur)
     * @default 2000
     */
    idleTimeout?: number;
}

/**
 * Hook to detect user activity and toggle focus mode
 * When idle for specified duration, returns false (blur peripherals)
 * When active, returns true (show peripherals clearly)
 */
export function useFocusMode(options: UseFocusModeOptions = {}) {
    const { idleTimeout = 2000 } = options;
    const [isFocused, setIsFocused] = useState(true);

    useEffect(() => {
        let timeout: NodeJS.Timeout;

        const handleActivity = () => {
            setIsFocused(true);
            clearTimeout(timeout);
            timeout = setTimeout(() => setIsFocused(false), idleTimeout);
        };

        // Initialize with first timeout
        timeout = setTimeout(() => setIsFocused(false), idleTimeout);

        // Listen for user activity
        window.addEventListener("mousemove", handleActivity);
        window.addEventListener("mousedown", handleActivity);
        window.addEventListener("keydown", handleActivity);
        window.addEventListener("touchstart", handleActivity);
        window.addEventListener("scroll", handleActivity);

        return () => {
            clearTimeout(timeout);
            window.removeEventListener("mousemove", handleActivity);
            window.removeEventListener("mousedown", handleActivity);
            window.removeEventListener("keydown", handleActivity);
            window.removeEventListener("touchstart", handleActivity);
            window.removeEventListener("scroll", handleActivity);
        };
    }, [idleTimeout]);

    return isFocused;
}
