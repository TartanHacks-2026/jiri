# PLAN: Jarvis Central Interface Redesign

> **Goal:** Transform the dashboard grid into a sentient AI system with a central "Eye" orb, focus mode, and tech line aesthetics.

---

## User Requirements

**From:** Current grid-based analytics dashboard  
**To:** Sci-fi "Central Intelligence" interface

### Approved Design Choices
- **Layout:** Option A - The Eye (Central orb dominates, peripherals float)
- **Interaction:** Focus Mode (peripherals fade to 20% opacity when idle)
- **Aesthetic:** Tech Lines (Neural network connectors between core and tools)

---

## Architecture Changes

### Current Structure (Grid-Based)
```
┌──────────────────────────────────────┐
│  TopStatusBar                        │
├─────────────────┬────────────────────┤
│  VoicePanel     │  ToolMarketplace   │
│  PlanCard       │  TracePanel        │
│  StateRail      │                    │
├─────────────────┴────────────────────┤
│  ArtifactsStrip                      │
└──────────────────────────────────────┘
```

### New Structure (Radial "Eye")
```
        [Session ID] [Tools Btn]
              ┌───────┐
              │       │
     ┌────────┤  EYE  ├────────┐
     │        │ (ORB) │        │
[Tools]       └───────┘      [Trace]
  ↑  tech lines   ↓         ↑
[Artifacts]  [StateRail] [Plan]
```

**Key Principles:**
1. **Central Orb:** 300-400px pulsing sphere (Siri breathing animation)
2. **Floating Modules:** Tools/Trace/Plan positioned radially around orb
3. **Focus Detection:** Mouse idle 2s → peripherals blur + fade 20%
4. **Tech Lines:** SVG paths connecting orb to active modules (stroke-dashoffset animation)

---

## Component Breakdown

### 1. Central Orb Component (`jarvis-orb.tsx`)

**NEW FILE**

#### Visual
```typescript
interface OrbState {
  isListening: boolean;
  isThinking: boolean;
  isIdle: boolean;
}
```

- **Listening:** Pulsing cyan glow (0.8s ease-in-out infinite)
- **Thinking:** Rotating inner particles (like ChatGPT loading dots)
- **Idle:** Slow breathing (3s cubic-bezier)

#### Layers (z-index stacking)
1. **Outer ring** (600px) - Faint plasma-cyan border, opacity 0.2
2. **Main sphere** (400px) - Radial gradient (cyber-black → plasma-cyan 40%)
3. **Inner pulse** (350px) - Scale animation 0.95 → 1.05
4. **Audio visualizer** (when active) - Frequency bars radiating from center

#### Transcript Display
- **Inside orb:** Last 2-3 transcript lines fade in/out
- **Typography:** 18px Space Grotesk, center-aligned
- **Animation:** Typewriter effect for partial transcript

---

### 2. Focus Mode System (`useFocusMode.ts` hook)

**NEW FILE**

```typescript
const useFocusMode = () => {
  const [isFocused, setIsFocused] = useState(false);
  
  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    const handleActivity = () => {
      setIsFocused(true);
      clearTimeout(timeout);
      timeout = setTimeout(() => setIsFocused(false), 2000);
    };
    
    window.addEventListener('mousemove', handleActivity);
    // ... cleanup
  }, []);
  
  return isFocused;
};
```

**Applied Styles:**
```css
.peripheral-module {
  transition: opacity 0.5s ease, filter 0.5s ease;
}

.peripheral-module.unfocused {
  opacity: 0.2;
  filter: blur(4px);
}
```

---

### 3. Tech Lines System (`tech-lines.tsx`)

**NEW FILE**

#### SVG Path Generation
```typescript
// Calculate curved path from orb center (50%, 50%) to module
const generateTechLine = (
  fromX: number, fromY: number,
  toX: number, toY: number
) => {
  const midX = (fromX + toX) / 2;
  const midY = (fromY + toY) / 2;
  
  // Quadratic curve for organic feel
  return `M ${fromX},${fromY} Q ${midX},${midY - 50} ${toX},${toY}`;
};
```

#### Styling
- **Stroke:** 2px plasma-cyan with 0.3 opacity
- **Animation:** `stroke-dasharray: 10 5` + `stroke-dashoffset` from 100 → 0 (1.5s)
- **Conditiional:** Only show lines to "active" modules (e.g., trace has new item, tool is executing)

#### Module Position Mapping
```typescript
const MODULE_POSITIONS = {
  trace: { x: '80%', y: '30%' },
  tools: { x: '20%', y: '30%' },
  artifacts: { x: '30%', y: '70%' },
  plan: { x: '70%', y: '70%' },
  stateRail: { x: '50%', y: '75%' },
};
```

---

### 4. Radial Layout (`command-center-shell.tsx` refactor)

**MODIFY EXISTING**

#### Old (Grid)
```tsx
<div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
  <VoicePanel />
  <TracePanel />
</div>
```

#### New (Absolute Positioning)
```tsx
<div className="relative h-screen w-screen overflow-hidden">
  {/* Central Orb */}
  <JarvisOrb 
    className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
    transcript={transcript}
    isListening={connectionStatus === "connected"}
  />
  
  {/* Floating Modules */}
  <FloatingModule position="trace" isFocused={isFocused}>
    <TracePanel trace={trace} />
  </FloatingModule>
  
  <FloatingModule position="tools" isFocused={isFocused}>
    <ToolsQuickView tools={tools} />
  </FloatingModule>
  
  {/* Tech Lines */}
  <TechLines activeModules={['trace', 'tools']} orbCenter={{ x: '50%', y: '50%' }} />
</div>
```

---

### 5. Floating Module Wrapper (`floating-module.tsx`)

**NEW FILE**

```tsx
interface FloatingModuleProps {
  position: keyof typeof MODULE_POSITIONS;
  isFocused: boolean;
  children: ReactNode;
}

export function FloatingModule({ position, isFocused, children }: FloatingModuleProps) {
  const pos = MODULE_POSITIONS[position];
  
  return (
    <motion.div
      className={cn(
        "absolute glassmorphic-card p-4 rounded-xl",
        !isFocused && "opacity-20 blur-sm"
      )}
      style={{ left: pos.x, top: pos.y, transform: 'translate(-50%, -50%)' }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: isFocused ? 1 : 0.2, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

---

## Color Palette Update

### Current (Jarvis-Grade)
- Background: `#0a0e14` (cyber-black)
- Accent: `#00d9ff` (plasma-cyan)
- Success: `#00ff88` (neon-green)

### Proposed Tweak (Higher Contrast for Orb)
- **Orb Glow:** `#00d9ff` → `#00e5ff` (brighter cyan for visibility)
- **Orb Interior:** Radial gradient `#0a0e14` 0% → `#00d9ff 30%` → transparent
- **Tech Lines:** `#00d9ff` at 0.4 opacity (slightly brighter than cards)

---

## Animation Specifications

### Central Orb Breathing
```css
@keyframes orb-breathe {
  0%, 100% { transform: scale(1); opacity: 0.9; }
  50% { transform: scale(1.05); opacity: 1; }
}

.orb-core {
  animation: orb-breathe 3s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
```

### Listening Pulse (Fast)
```css
@keyframes listening-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(0, 217, 255, 0.6); }
  50% { box-shadow: 0 0 60px rgba(0, 217, 255, 1); }
}

.orb-listening {
  animation: listening-pulse 0.8s ease-in-out infinite;
}
```

### Tech Line Draw
```css
@keyframes line-draw {
  from { stroke-dashoffset: 100; }
  to { stroke-dashoffset: 0; }
}

.tech-line {
  stroke-dasharray: 10 5;
  animation: line-draw 1.5s ease-out forwards;
}
```

---

## Mobile Adaptation

### Breakpoint: < 768px

1. **Orb Size:** 300px → 200px
2. **Modules:** Stack vertically below orb instead of radial
3. **Tech Lines:** Hide entirely (performance + visual clutter)
4. **Focus Mode:** Always "focused" (no blur) on mobile

```tsx
const isMobile = useMediaQuery('(max-width: 768px)');

return isMobile ? (
  <MobileStackedLayout />
) : (
  <RadialLayout />
);
```

---

## Implementation Tasks

| ID  | Task                                   | Files                         | Est. |
| --- | -------------------------------------- | ----------------------------- | ---- |
| 1   | Create `JarvisOrb` component           | `jarvis-orb.tsx`              | 2h   |
| 2   | Create `useFocusMode` hook             | `useFocusMode.ts`             | 30m  |
| 3   | Create `TechLines` SVG component       | `tech-lines.tsx`              | 1.5h |
| 4   | Create `FloatingModule` wrapper        | `floating-module.tsx`         | 1h   |
| 5   | Refactor `command-center-shell` layout | `command-center-shell.tsx`    | 2h   |
| 6   | Adapt `TracePanel` for floating        | `trace-panel.tsx`             | 30m  |
| 7   | Adapt `StateRail` for bottom position  | `state-rail.tsx`              | 30m  |
| 8   | Mobile responsive breakpoints          | All components                | 1h   |
| 9   | Polish animations + accessibility      | CSS + ARIA labels             | 1h   |
| 10  | Browser testing + verification         | Visual QA                     | 1h   |
|     | **TOTAL**                              |                               | ~11h |

---

## Verification Plan

### Visual Checklist
- [ ] Central orb pulses smoothly (3s breathing)
- [ ] Orb changes to fast pulse when `connectionStatus === "connected"`
- [ ] Transcript lines appear inside orb with typewriter effect
- [ ] Peripherals blur + fade to 20% after 2s idle
- [ ] Hover over module → restores focus instantly
- [ ] Tech lines draw from orb to active modules (1.5s animation)
- [ ] Mobile: orb shrinks, vertical stack, no tech lines

### Functional Checklist
- [ ] Focus mode hook doesn't cause re-render storms
- [ ] SVG tech lines don't block pointer events
- [ ] Absolute positioning doesn't break on window resize
- [ ] Accessibility: Orb has `aria-live="polite"` for transcript

### Browser Test
```bash
npm run dev
# → Visit http://localhost:3000
# → Test states: idle, listening, thinking
# → Test mouse idle → focus mode activate
# → Test mobile view (DevTools responsive mode)
```

---

## Risks & Mitigations

| Risk                                    | Mitigation                                     |
| --------------------------------------- | ---------------------------------------------- |
| Absolute positioning breaks on resize  | Use `%` units + `ResizeObserver` for orb size |
| Tech lines cause layout thrashing      | Memoize SVG paths, render in separate layer   |
| Focus mode flickers on rapid movement  | Debounce with 100ms buffer                     |
| Orb animations lag on low-end devices  | Use `will-change: transform` sparingly         |
| Mobile feels cluttered with all modules | Hide inactive modules entirely on mobile       |

---

## Next Steps

1. **Review this plan** - Confirm radial layout + focus mode mechanics
2. **Approve** → I'll start with Task 1 (JarvisOrb component)
3. **Iterate** → After orb works, add modules one by one

---

**Ready for implementation?**
