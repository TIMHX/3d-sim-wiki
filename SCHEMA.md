---
title: Wiki Schema
created: 2026-07-22
updated: 2026-07-22
type: meta
tags: [meta]
---

# Wiki Schema

## Domain
3D graphics, simulation, VR/AR, and robotics environments — Blender modeling, Gaussian Splatting, Isaac Sim/Lab, Unity, VRChat, scene design, physics simulation, and their cross-tool workflows.

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `blender-scene-export.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source.
- **Immutable raw/:** Files in `raw/` are never modified. Corrections go in wiki pages.

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary | meta | troubleshooting
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
confidence: high | medium | low
contested: true
contradictions: [other-page-slug]
---
```

## Tag Taxonomy

- **Tools:** blender, isaac-sim, isaac-lab, unity, vrchat, gaussian-splatting, colmap, brush
- **Concepts:** modeling, scene-design, physics, rendering, export-import, asset-management, path-planning
- **Projects:** robot-env, gs-capture, vrchat-avatar
- **Meta:** comparison, troubleshooting, workflow, reference

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines
- **Archive a page** when fully superseded — move to `_archive/`, remove from index

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark in frontmatter: `contradictions: [page-name]`
4. Flag for review in the lint report
