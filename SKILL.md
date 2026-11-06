---
name: skill-stack
description: Run BEFORE starting any task. Picks the right stack of already-installed skills for the prompt via a cheap local index (thousands of skills, ~500 tokens), then optionally searches GitHub/skills.sh for new skills and FREE MCP servers. Use when starting work, or when the user says "find skills", "какие скиллы", "skill stack", "подбери скиллы/MCP".
---

# skill-stack

Goal: find the minimal skill + MCP stack for the task while spending as few tokens as possible.

## Hard token rules
- NEVER open, cat, ls or grep skill folders yourself. Only use the scripts below.
- Never read a found SKILL.md until the user (or the task) actually needs that skill.
- Print results as a compact table; no README dumps; no explanations of each skill beyond 1 line.
- Online waves only after the user says yes.

## Wave 1 — local (always)
1. From the prompt extract 5–12 keywords: domain, stack, action, artifact. Add EN synonyms for RU words (e.g. "тесты" -> test testing jest playwright).
2. Run (the script auto-rebuilds the index only if skill folders changed):
   ```bash
   python3 <this-skill-dir>/scripts/search.py kw1 kw2 kw3 ... --top 8
   ```
3. Show the result table: `name | why (1 line) | path`. Pick the stack (usually 1–4 skills) and say which you will use.
4. Ask one question: "Искать новые скиллы и бесплатные MCP онлайн? (да/нет)". If local coverage is clearly enough, recommend "нет".

## Wave 2 — online skills (only if yes)
Read `references/online.md` (section Skills) and run at most 3 searches. Keep top 5, skip anything already in the local index.

## Wave 3 — free MCP (only if yes)
Read `references/online.md` (section MCP). Keep top 5 free/open-source servers only; drop paid or API-key-only-paid services.

## Output
```
LOCAL:  name — why — path
NEW:    owner/repo@skill — why — stars/installs
MCP:    server — why — free? — install
```
Then ask which to install. Install only after explicit OK, using `references/install.md`.

## Config
Search paths & limits: `config.json` next to this file. Force reindex: `python3 scripts/build_index.py --force`.
