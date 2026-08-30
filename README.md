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
python3 cc-tax.py              # audits ~/.claude, plus ./.claude if present
python3 cc-tax.py ~/other      # audits one config root
python3 cc-tax.py --selftest   # verifies the parser and the scanner
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

## Your real number is the sum of two roots

Skills, agents and commands also resolve from a project-level `.claude/` directory, so a
home-install figure is a floor, not a total. The session you are actually in costs the home
install plus whatever the repo you started in contributes:

```bash
python3 cc-tax.py            # both roots at once, from inside the project
python3 cc-tax.py ~/.claude  # just the home install
```

With no arguments the script counts `~/.claude` and, if you are standing in a project
that has one, `./.claude` — then prints each and their sum.

This also changes what you do with the result. A skill that only ever fires in one
repository is not a delete — it is a move. Relocated into that project's `.claude/`, it
stops billing every session that is not that project, and still works where you need it.

Credit for the correction: [@vinhnguyenthanhdn](https://dev.to/vinhnguyenthanhdn) in the
comments on the write-up.

## As a skill

`skill/SKILL.md` packages this as a Claude Code skill. Copy it to
`~/.claude/skills/cc-tax/SKILL.md` and ask Claude what your config costs.

Yes, it charges rent too — which is why its own description is two lines, not a paragraph.

## Why

[The write-up](https://dev.to/amzotec/my-claude-code-config-costs-9857-tokens-before-i-type-anything-3gin)
— how the measurement works, which popular components turn out to be dead on arrival,
and what to delete first.

MIT.
