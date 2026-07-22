---
title: Blender Keyboard Shortcuts
created: 2026-07-22
updated: 2026-07-22
type: reference
tags: [blender, modeling, workflow]
sources: [raw/references/blender-quickref-cheatsheet.md, raw/references/bringyourownlaptop-modeling-shortcuts.md]
confidence: high
---

# Blender Keyboard Shortcuts

> Comprehensive Blender hotkey reference (4.x). Organized by workflow category.
> Focus: modeling, navigation, and scene editing — the operations you'll use most in environment design.

## Navigation (3D Viewport)

| Shortcut | Action |
|----------|--------|
| `MMB` drag | Rotate view (orbit) |
| `Alt` + `LMB` drag | Rotate view — 无中键替代方案 |
| `Shift` + `MMB` drag | Pan view |
| `Alt` + `Shift` + `LMB` drag | Pan view — 无中键替代 |
| `Scroll` | Zoom in/out |
| `Alt` + `Ctrl` + `LMB` drag | Zoom — 无滚轮替代 |
| `Numpad 2` / `4` / `6` / `8` | Orbit down / left / right / up (15° steps) |
| `Shift` + `~` | Fly/Walk navigation mode |

### View Switching (Numpad / Number Keys)

| Shortcut | Action |
|----------|--------|
| `Numpad 1` | Front view (`Ctrl` + `1` = Back) |
| `Numpad 3` | Right view (`Ctrl` + `3` = Left) |
| `Numpad 7` | Top view (`Ctrl` + `7` = Bottom) |
| `Numpad 9` | Reverse view (opposite of current) |
| `Numpad 5` | Toggle orthographic / perspective |
| `Numpad 0` | Camera view |
| `Ctrl` + `Numpad 0` | Set active object as camera |
| `Ctrl` + `Alt` + `Numpad 0` | Align active camera to current view |
| `Ctrl` + `Alt` + `Q` | Quad view (front/top/right + perspective) |
| `Numpad .` | Frame selected — 拉近聚焦选中物体 |
| `Home` | Frame all objects |
| `/` (slash) | Local view — isolate selected object |

### Laptop / No Numpad

If your keyboard lacks a numpad, enable **Emulate Numpad** in Preferences → Input. Then the regular number row (`1`–`0`) works as Numpad. `~` (tilde) opens the **View pie menu** as an alternative to numpad views.

## Selection

| Shortcut | Action |
|----------|--------|
| `A` | Select all / deselect all |
| `Alt` + `A` | Deselect all |
| `B` | Box select |
| `C` | Circle select (scroll to resize, `Esc`/`RMB` to exit) |
| `Ctrl` + `LMB` drag | Lasso select |
| `Shift` + `LMB` | Add/remove from selection |
| `Ctrl` + `I` | Invert selection |
| `L` | Select linked (under cursor, in Edit Mode) |
| `Ctrl` + `L` | Select all linked geometry |
| `Alt` + `LMB` (on edge) | Select edge loop |
| `Alt` + `Shift` + `LMB` | Select edge ring / multiple loops |
| `Ctrl` + `Numpad +` | Grow selection |
| `Ctrl` + `Numpad -` | Shrink selection |
| `1` / `2` / `3` | Vertex / Edge / Face select mode (Edit Mode) |

## Transform (Object & Edit Mode)

| Shortcut | Action |
|----------|--------|
| `G` | Grab (move) |
| `R` | Rotate |
| `S` | Scale |
| `G`/`R`/`S` + `X`/`Y`/`Z` | Lock to axis |
| `G`/`R`/`S` + `Shift` + `X`/`Y`/`Z` | Lock to plane (exclude axis) |
| `Alt` + `G` | Clear location |
| `Alt` + `R` | Clear rotation |
| `Alt` + `S` | Clear scale |
| `Ctrl` + `A` | Apply transform (location/rotation/scale) |

## Edit Mode — Core Modeling

| Shortcut | Action |
|----------|--------|
| `Tab` | Toggle Object/Edit mode |
| `E` | Extrude (drag mouse; `RMB` or `Esc` to cancel movement, keep face) |
| `I` | Inset faces |
| `Ctrl` + `R` | Loop cut (scroll to add cuts, `LMB` to confirm, `RMB` to center) |
| `Ctrl` + `B` | Bevel (scroll to add segments) |
| `K` | Knife tool (`Enter` to confirm, `Esc` to cancel) |
| `M` | Merge vertices (menu: at center, at cursor, by distance) |
| `F` | Make face/edge from selection |
| `P` | Separate selection to new object |
| `Ctrl` + `E` | Edge menu (bridge, mark seam, etc.) |
| `Ctrl` + `F` | Face menu |
| `X` | Delete (vertex/edge/face) |
| `Shift` + `D` | Duplicate |
| `Shift` + `D`, then `RMB` | Duplicate in place (cancel move, keep copy) |
| `Alt` + `D` | Linked duplicate (shared mesh data) |
| `Shift` + `R` | Repeat last operation |
| `Alt` + `E` | Extrude menu (individual faces, along normals) |
| `Alt` + `N` | Normals menu (flip, recalculate outside/inside) |
| `Alt` + `S` | Shrink/Fatten (沿法线缩放，Edit Mode) |
| `Alt` + `F` | Beautify faces (优化三角面布局) |
| `Alt` + `J` | Tris to Quads |
| `Ctrl` + `H` | Hook menu (bind vertex to empty/bone) |
| `F9` | Adjust last operation panel |
| `H` | Hide selected geometry |
| `Alt` + `H` | Unhide all hidden geometry |
| `Shift` + `H` | Hide unselected — isolate specific geometry |

## Object Mode

| Shortcut | Action |
|----------|--------|
| `Shift` + `A` | Add menu (mesh, light, camera, etc.) |
| `Shift` + `D` | Duplicate object |
| `Shift` + `D`, then `RMB` | Duplicate in place (cancel move) |
| `Ctrl` + `J` | Join selected objects |
| `Ctrl` + `P` | Parent selected to active |
| `Alt` + `P` | Clear parent (menu: keep transform / clear) |
| `H` | Hide selected |
| `Alt` + `H` | Unhide all |
| `Shift` + `H` | Hide unselected |
| `Ctrl` + `M` | Mirror (opens axis menu) |
| `Alt` + `G` / `Alt` + `R` / `Alt` + `S` | Clear location / rotation / scale |
| `/` | Local view toggle |

## Modifiers

| Shortcut | Action |
|----------|--------|
| `Ctrl` + `1-5` | Add Subdivision Surface modifier (levels 1–5) |
| From modifier panel: `Ctrl` + `A` | Apply modifier (when hovering over it) |

## Viewport Display

| Shortcut | Action |
|----------|--------|
| `Z` | Shading pie menu (wireframe, solid, material preview, rendered) |
| `Shift` + `Z` | Toggle wireframe/rendered |
| `Alt` + `Z` | Toggle X-ray |
| `Alt` + `B` | Clipping region (render preview isolation) |
| `D` + `LMB` drag | Annotate — freehand draw on viewport |
| `Ctrl` + `Space` | Toggle maximize area |
| `~` (tilde) | View pie menu |
| `,` (comma) | View orientation pie menu |

## Sculpt Mode

| Shortcut | Action |
|----------|--------|
| `Tab` (from Object Mode) | Switch to Sculpt Mode |
| `F` | Adjust brush radius |
| `Shift` + `F` | Adjust brush strength |
| `Ctrl` + `LMB` drag (in empty space) | Rotate view |
| `1` | Draw brush |
| `2` | Clay Strips brush |
| `3` | Grab brush |
| `Shift` smooth | Hold to smooth |
| `Ctrl` invert | Hold to invert brush effect |
| `Alt` + `M` | Mask menu |
| `Alt` + `A` | Auto-masking settings popover |

## Animation / Timeline

| Shortcut | Action |
|----------|--------|
| `I` | Insert keyframe |
| `Alt` + `I` | Delete keyframe |
| `Shift` + `Left` | Go to first frame |
| `Shift` + `Right` | Go to last frame |
| `Left`/`Right` | Previous/next frame |
| `Up`/`Down` | Jump 10 frames forward/back |
| `Space` | Play/pause animation |

## General / File

| Shortcut | Action |
|----------|--------|
| `Ctrl` + `S` | Save |
| `Ctrl` + `O` | Open |
| `Ctrl` + `N` | New file |
| `Ctrl` + `Z` | Undo |
| `Ctrl` + `Shift` + `Z` | Redo |
| `F2` | Rename active object |
| `F3` | Search menu (run any command by name) |
| `F12` | Render image |
| `Ctrl` + `F12` | Render animation |
| `Esc` | Cancel operation |

## Quick Tips

- **`F3` is your lifeline** — if you forget a shortcut, just type the command name
- **`F9` after any operation** — tweak parameters (bevel segments, extrude depth, etc.)
- **Numpad shortcuts work with regular number keys too** — enable "Emulate Numpad" in Preferences → Input
- **On laptop/mac without numpad**: Preferences → Input → Emulate Numpad
- **Middle mouse broken?** See Navigation section — `Alt` + `LMB` / `Shift` + `LMB` / `Ctrl` + `LMB` combinations replace MMB/scroll entirely
- **Isolate geometry fast:** `Shift` + `H` (hide unselected) → work → `Alt` + `H` (unhide all) — works in both Object and Edit Mode
- **Duplicate in place:** `Shift` + `D` then immediately `RMB` — creates a copy at the exact same location
- **Annotate for planning:** `D` + `LMB` to sketch notes directly on the 3D viewport; `D` + `D` to erase all annotations

## See Also

- [[blender-modeling-workflow]] (coming soon)
- [[scene-design-construction-site]] (robot project scene)
