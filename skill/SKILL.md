---
name: cc-tax
description: Measure what your Claude Code config costs per session before you type anything. Use when the context window feels tight or after installing skills.
---

# cc-tax

Every installed skill, agent and command keeps its `description` in the context window
for the whole session, used or not. Bodies load on trigger; descriptions are rent you
pay upfront, every session, forever.

This skill measures that rent.

## Run it

```bash
python3 cc-tax.py              # audits ~/.claude
python3 cc-tax.py ~/other      # another config root
python3 cc-tax.py --selftest   # verifies the frontmatter parser
```

No dependencies, standard library only, one file. Read it before you run it.

## Reading the output

```
skills        107     7,470
agents         38     1,999
commands       15       388
TOTAL         160     9,857
```

The total is what you pay on every session before typing. Below it, the ten heaviest
descriptions — those are what to trim first.

## What it counts

Walks `skills/*/SKILL.md`, `agents/*.md`, `commands/*.md`, extracts `description` from
the YAML frontmatter, estimates tokens as characters ÷ 4. A real tokenizer shifts the
absolute numbers a few percent and reorders nothing.

**Not counted, so your real number is higher:** plugin-provided components, and MCP tool
schemas — those arrive from the server at connection time and are not measurable from disk.

## What to do with the number

Delete anything you have not triggered in a month. A skill that depends on an MCP server
or a hook you never wired up is charging rent for functionality you do not have.

## Note on this skill

Yes, it charges rent too — that is why its own description is two lines instead of a
paragraph. Measuring the cost does not exempt you from paying it.
