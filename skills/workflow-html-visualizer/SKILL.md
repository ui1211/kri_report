---
name: workflow-html-visualizer
description: "Use this skill to analyze a real codebase and generate workflow visualization files (ワークフロー可視化, flows.json, workflows.html, SVG workflow graph). Extract actual package/component flows from source code and render them into a single-page interactive HTML visualization using vanilla SVG and JavaScript."
---

# workflow-html-visualizer

## Purpose

Analyze a real project directory and extract actual workflows from source code.

Generate:

- `docs/flows.json`
- `docs/workflows.html`

The visualization must work with:

- `file://`
- `python -m http.server`

The implementation must use:

- vanilla JavaScript
- pure SVG
- no external libraries

The final output and generated files must preserve all required Japanese labels and structure.

## Core Rules

1. MUST read real source code before generating workflows.
2. MUST extract only real workflows from actual code paths.
3. MUST NOT invent workflows, APIs, events, or components.
4. MUST keep all `from` and `to` references resolvable through `nodes[].id`.
5. MUST generate exactly two deliverables:
   - `docs/flows.json`
   - `docs/workflows.html`
6. MUST use embedded JSON fallback via:
   - `<script type="application/json" id="workflow-data">`
7. MUST support both:
   - `fetch('./flows.json')`
   - embedded fallback mode
8. MUST use pure SVG rendering.
9. MUST NOT use:
   - Cytoscape
   - D3
   - Mermaid
   - external UI libraries
10. MUST implement interactive zoom and pan.
11. MUST implement badge collision avoidance.
12. MUST implement lane offsets for bidirectional edges.
13. MUST keep badge-layer above node-layer.
14. MUST use `mouseover` and `mouseout` instead of `mouseenter`.
15. MUST implement focused animation effects:
   - badge pulse
   - halo burst
   - edge pulse
   - node glow
   - annotation flash
16. MUST aggregate multiple steps on the same edge into one badge.
17. MUST NOT render `passes` text directly on edges.
18. MUST use dark theme with warm gold highlight colors.
19. MUST preserve all required keyboard shortcuts.
20. MUST optimize layout for a single-page workflow overview.

## Required Output Template

Keep this JSON structure exactly.

```json
{
  "viewBox": { "w": 1500, "h": 900 },
  "columns": [
    {
      "id": "...",
      "label": "COL HEADER",
      "x": 160,
      "divider": 300
    }
  ],
  "groups": [
    {
      "id": "...",
      "label": "...",
      "stroke": "#xxx",
      "fill": "#xxx",
      "sub": "#xxx"
    }
  ],
  "nodes": [
    {
      "id": "...",
      "title": "...",
      "subtitle": "...",
      "group": "...",
      "x": 50,
      "y": 200,
      "w": 220,
      "h": 56
    }
  ],
  "flows": [
    {
      "id": "...",
      "icon": "🚀",
      "name": "1. ...",
      "sub": "...",
      "description": "...",
      "steps": [
        {
          "from": "...",
          "to": "...",
          "passes": "...",
          "note": "..."
        }
      ]
    }
  ]
}
```

## Workflow

1. Read:
   - README
   - entrypoints
   - routers
   - services
   - frontend
   - database access
   - CLI
   - APIs

2. Extract:
   - real workflows
   - actual component transitions
   - real payload movement
   - real execution order

3. Build:
   - columns
   - groups
   - nodes
   - flows
   - edge mappings

4. Validate:
   - all node IDs resolve
   - no missing references
   - no invented flows
   - layout fits one page

5. Generate:
   - `flows.json`
   - `workflows.html`

6. Implement:
   - SVG layers
   - badges
   - tooltips
   - animations
   - zoom
   - pan
   - focus system
   - keyboard shortcuts

7. Validate browser compatibility:
   - file://
   - local server
   - Chromium
   - Edge

## SVG Layer Rules

The SVG layer order MUST be:

```txt
defs
→ col-layer
→ edge-layer
→ node-layer
→ badge-layer
```

`badge-layer` MUST always be appended last.

## Edge Rules

1. MUST use bezier curves.
2. MUST separate bidirectional edges using lane offsets.
3. MUST assign deterministic lane direction using lexical comparison.
4. MUST support:
   - vertical routing
   - horizontal routing
5. MUST render active arrows separately.

## Badge Rules

1. MUST aggregate same-edge steps into one badge.
2. MUST implement collision detection.
3. MUST check:
   - badge collisions
   - node bbox overlap
4. MUST implement escape loop fallback.
5. MUST render tether lines when displaced from midpoint.
6. MUST use pill-shaped badges.
7. MUST include transparent hit-area.
8. MUST keep hover styling scoped to visible pill only.

## Tooltip Rules

1. MUST use fixed-position tooltip.
2. MUST support:
   - single-step tooltip
   - multi-step tooltip
3. MUST flip placement near screen edges.
4. MUST suppress node tooltips while flow selection is active.

## Interaction Rules

MUST support:

- wheel zoom
- drag pan
- badge click focus
- multi-step cycling
- annotation click focus
- keyboard shortcuts
- animated fit-to-flow

Keyboard bindings:

- `1-9`, `0` → flow select
- `F` → fit view
- `+` / `-` → zoom
- `Esc` → clear focus

## Animation Rules

Focused state MUST trigger:

1. badge pulse
2. badge color inversion
3. halo burst
4. edge pulse
5. node glow
6. annotation flash

Animations MUST use:

```css
transform-origin: center;
transform-box: fill-box;
```

## CSS Theme Rules

MUST define:

```css
--bg:#0c1117;
--bg-2:#11171f;
--panel:#161d27;
--line:#2a3340;
--text:#d6dde6;
--muted:#8a94a3;
--edge:#2c3441;
--edge-active:#ffd166;
--edge-active-glow:rgba(255,209,102,0.55);
```

## Completion Checks

- `flows.json` exists.
- `workflows.html` exists.
- JSON is valid.
- All node references resolve.
- No invented flows exist.
- SVG layer order is correct.
- Badge collision handling exists.
- Lane offset handling exists.
- Tooltip logic exists.
- Keyboard shortcuts work.
- Zoom and pan work.
- file:// mode works.
- Embedded JSON fallback works.
- No external libraries are used.
- Required dark theme variables exist.
- Focus animations exist.
- Badge hover is not blocked by nodes.

## Do Not

- Do not invent workflows.
- Do not generate placeholder flows.
- Do not render `passes` inline on edges.
- Do not place badge-layer below node-layer.
- Do not omit lane offsets.
- Do not skip node overlap checks.
- Do not use graph libraries.
- Do not require build steps.
- Do not require npm packages.
- Do not require TypeScript compilation.
- Do not require backend services.
- Do not require user confirmation for safe defaults.