# cc-tax

**What your Claude Code config costs before you type anything.**

Every skill, agent and command keeps its `description` in the context window for the
whole session — used or not. Bodies load on trigger; descriptions are rent you pay
upfront, on every session, forever.

This script measures that rent.

```bash
curl -O https://raw.githubusercontent.com/Aliwers/cc-tax/main/cc-tax.py
python3 cc-tax.py
```

```
  Config root: /Users/you/.claude

              count    tokens
  ---------------------------
  skills        107     7,470
  agents         38     1,999
  commands       15       388
  ---------------------------
  TOTAL         160     9,857

  ~9,857 tokens are gone before you type anything.

  Heaviest descriptions — trim these first:

      244  loop-design-check (skill)
      209  token-budget-advisor (skill)
      ...
```

## Usage

```bash
python3 cc-tax.py              # audits ~/.claude
python3 cc-tax.py ~/other      # audits another config root
python3 cc-tax.py --selftest   # verifies the frontmatter parser
```

No dependencies, standard library only, single file. Read it before you run it.

## What it counts

Walks `skills/*/SKILL.md`, `agents/*.md` and `commands/*.md`, extracts `description`
from the YAML frontmatter, estimates tokens as characters ÷ 4 — the standard rule of
thumb. A real tokenizer shifts absolute numbers by a few percent and changes no
ranking, which is why there is no dependency.

**Not counted, so your real number is higher:** components provided by installed
plugins, and MCP tool schemas. MCP descriptions arrive from the server at connection
time and are not measurable from disk at all.

## Why

[The write-up](https://dev.to/) — how the measurement works, which popular components
turn out to be dead on arrival, and what to delete first.

MIT.
