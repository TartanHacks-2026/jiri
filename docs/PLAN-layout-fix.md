# Layout Fix Plan: Command Center Spacing & Positioning

**Created:** 2026-02-07  
**Status:** Awaiting Approval  
**Complexity:** High (CSS positioning, responsive design, multi-file refactor)

---

## Problem Statement

The Jiri Command Center dashboard has persistent layout issues:
1. **Orb Centering:** Central "READY" orb appears at ~55%/65% instead of true 50%/50%
2. **Module Overlap:** Orb overlaps Voice panel and StateRail components
3. **Tech Lines Misalignment:** Dotted connectors start from 50%/50% but orb is elsewhere
4. **Root Cause:** Double translation issue - orb container uses explicit dimensions + internal elements use their own translate-50%, creating cumulative offset

### Current Component Sizes
- **Orb Outer Ring:** 220px mobile / 280px desktop
- **Orb Main Sphere:** 160px mobile / 200px desktop
- **Container:** max-w-[1200px], h-[min(780px,calc(100vh-200px))]
- **Module Positions:** 18%/82% horizontal, 26%/65%/85% vertical

---

## Solution Architecture

### Strategy: Coordinate System Reset
Replace percentage-based positioning with a **CSS Grid layout** for predictable spacing:

```
┌─────────────────────────────────────┐
│  Container (1200px max, grid)       │
│  ┌─────┐         ┌─────┐           │
│  │Tools│         │Trace│           │
│  └─────┘    ╭─────╮    └─────┘     │
│             │ Orb │                │
│  ┌─────┐    ╰─────╯    ┌─────┐     │
│  │Voice│         │Plan │           │
│  └─────┘   ┌─────────┐ └─────┘     │
│            │StateRail│             │
│            └─────────┘             │
└─────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Remove Double Translation (jarvis-orb.tsx)
**Agent:** `frontend-specialist`

**Changes:**
1. Remove explicit dimensions from outer wrapper (current: `h-[220px] w-[220px]`)
2. Keep internal circles with their own centering
3. Simplify to single translation point

**Files:**
- `apps/web/src/components/command-center/jarvis-orb.tsx`

### Phase 2: Implement CSS Grid Layout (command-center-shell.tsx)
**Agent:** `frontend-specialist`

**Changes:**
1. Replace absolute positioning with CSS Grid
2. Define 5x5 grid with orb at center cell (3,3)
3. Place modules in specific grid cells:
   - Tools: cell (2,2)
   - Trace: cell (2,4)
   - Voice: cell (4,2)
   - Plan: cell (4,4)
   - StateRail: cell (5,3)

**Files:**
- `apps/web/src/components/command-center/command-center-shell.tsx`
- `apps/web/src/components/command-center/floating-module.tsx`

### Phase 3: Update Tech Lines for Grid (tech-lines.tsx)
**Agent:** `frontend-specialist`

**Changes:**
1. Calculate module positions from grid cells instead of percentages
2. Sync with actual orb center (grid cell 3,3)
3. Add all 5 modules to connections (currently missing voice/stateRail)

**Files:**
- `apps/web/src/components/command-center/tech-lines.tsx`

### Phase 4: Mobile Responsiveness
**Agent:** `frontend-specialist`

**Changes:**
1. Grid collapses to single column on mobile
2. Orb shrinks to 180px
3. Modules stack vertically below orb

### Phase 5: Verification & Testing
**Agent:** `test-engineer`

**Verification:**
1. Visual regression test (screenshot comparison)
2. Responsive breakpoint testing (375px, 768px, 1200px, 1920px)
3. Focus mode transitions still work
4. No console errors
5. Lighthouse accessibility score maintained

**Scripts:**
- `python .agent/skills/webapp-testing/scripts/playwright_runner.py`
- `python .agent/skills/frontend-design/scripts/ux_audit.py`

---

## Alternative Approach (If Grid Fails)

### Fallback: Fixed Pixel Positioning
- Container: 1000px × 700px fixed size
- Orb: Absolute center at 500px, 350px
- Modules: Fixed pixel offsets from center
- Scale entire container for responsive

---

## Success Criteria

- [ ] Orb visually centered at 50%/50% of container
- [ ] No overlaps between orb and any module
- [ ] Tech lines connect from orb center to all 5 modules
- [ ] Layout symmetric left-right
- [ ] Mobile responsive (stacked layout < 768px)
- [ ] Focus mode still functional
- [ ] Zero console errors
- [ ] Passes UX audit

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Grid breaks existing animations | Keep animation logic, only change layout |
| Module positions shift unexpectedly | Test at each breakpoint |
| Tech lines don't align | Recalculate from grid cell centers |
| Focus mode broken | Preserve existing focus logic |

---

## Estimated Effort

- **Phase 1-3:** 45 minutes (refactoring)
- **Phase 4:** 20 minutes (mobile responsive)
- **Phase 5:** 15 minutes (verification)
- **Total:** ~1.5 hours

---

## Agent Assignments

| Phase | Agent | Rationale |
|-------|-------|-----------|
| 1-4 | `frontend-specialist` | CSS layout expert, React component refactoring |
| 5 | `test-engineer` | Verification scripts, visual regression |
| Optional | `performance-optimizer` | If bundle size increases |
