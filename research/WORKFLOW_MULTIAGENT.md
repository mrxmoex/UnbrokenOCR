# Multi-agent research workflow (UnbrokenOCR / CONTROL)

**Authorized pattern** after successful three-source Fraktur recon (2026-08-25).  
Use this when dividing independent analyses and steering them together.

## Shape

1. **CONTROL** plans, fetches raw sources into `research/raw/`, writes first-pass synthesis if needed.  
2. **Leaf agents** (`delegate_task`, independent) each own **one source** — no mid-run cross-talk.  
3. **Steer** early when tooling fails (e.g. `web_extract` ddgs-only → curl/ar5iv/gh API).  
4. **On broken/truncated leaf:** CONTROL does **not** wait forever — re-fetch primary artifact, complete the note, mark recovery in the source file.  
5. **Merge** agent reports into `research/SYNTHESIS_*.md`; commit local git; **no hermes upstream** until bulletproof.

## Failure modes → upgrades

| Failure | Seen | Upgrade / auth |
|---------|------|----------------|
| `web_extract` unavailable | ddgs search-only | Prefer `curl` + ar5iv + GitHub API; parent pre-seeds `research/raw/` |
| Leaf max_iterations / broken pipe | Agent 1 paper | Parent completes from PDF; raise `delegation.max_iterations` for PDF-heavy tasks if recurring |
| Steer misses finished child | steer after exit | Steer **immediately** after dispatch; or bake fallbacks into goal text |
| Sibling overwrite same path | concurrent writes | Assign **unique output paths** per agent; CONTROL merges |
| Hallucinated “full paper” from HTML shell | ar5iv abstract-only page | Require **pdftotext on real PDF** for section tables |

## Strengths-to-steal gate

Before coding research ideas into product:

1. Does it **bulletproof** detect/route/plates/eval?  
2. Does it add **ops burden** (legacy TF1, huge weights)? → optional track only  
3. Document in `research/STRENGTHS_ADOPTED.md` with version bump  

## Commands (CONTROL muscle memory)

```text
delegate_task(tasks=[... independent sources ...])
delegate_task(action='steer', subagent_id=..., message='use curl; raw at research/raw/...')
delegate_task(action='list')
# on truncate: parent finishes note + synthesis
```

## Auth

Human (m) authorizes this orchestration style for UnbrokenOCR research.  
Kids profiles: never.  
Hermes upstream PR: still blocked (`NO_UPSTREAM_PUSH.md`).
