#!/usr/bin/env python3
"""cc-tax — what your Claude Code config costs before you type anything.

Every skill, agent and command keeps its `description` in the context window for
the whole session. Bodies load on trigger; descriptions are rent you pay upfront.
This script measures that rent.

Usage:
    python3 cc-tax.py            # audit ~/.claude
    python3 cc-tax.py PATH       # audit another config root
    python3 cc-tax.py --selftest # verify the parser

Token counts are estimates (chars / 4), the standard rule of thumb. Absolute
numbers shift a few percent by tokenizer; the ranking does not.
"""
import pathlib
import re
import sys

CHARS_PER_TOKEN = 4
# Frontmatter is scanned for `description:` up to the next top-level key.
DESC_RE = re.compile(r"^description:[ \t]*(.*?)(?=^[A-Za-z_][\w-]*:|\Z)", re.S | re.M)
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
# Leading YAML block scalar markers (>-, |, |2) and surrounding quotes are noise.
BLOCK_MARKER_RE = re.compile(r"\A[>|][+-]?\d*\s*")


def extract_description(text):
    """Return the description value from a markdown file's YAML frontmatter."""
    fm = FRONTMATTER_RE.search(text)
    if not fm:
        return ""
    found = DESC_RE.search(fm.group(1))
    if not found:
        return ""
    value = BLOCK_MARKER_RE.sub("", found.group(1).strip())
    return value.strip().strip("\"'").strip()


def tokens(text):
    return len(text) / CHARS_PER_TOKEN


def scan(root):
    """Collect (kind, name, description tokens) for every component under root."""
    sources = (
        ("skill", sorted(root.glob("skills/*/SKILL.md")), lambda p: p.parent.name),
        ("agent", sorted(root.glob("agents/*.md")), lambda p: p.stem),
        ("command", sorted(root.glob("commands/*.md")), lambda p: p.stem),
    )
    rows = []
    for kind, paths, name_of in sources:
        for path in paths:
            desc = extract_description(path.read_text(errors="ignore"))
            rows.append((kind, name_of(path), tokens(desc)))
    return rows


def report(root, rows):
    if not rows:
        print(f"No skills, agents or commands found under {root}")
        print("Point the script at a config root: python3 cc-tax.py ~/.claude")
        return

    print(f"\n  Config root: {root}\n")
    print(f"  {'':<10}{'count':>7}{'tokens':>10}")
    print(f"  {'-' * 27}")
    total = 0.0
    for kind in ("skill", "agent", "command"):
        group = [r for r in rows if r[0] == kind]
        if not group:
            continue
        cost = sum(r[2] for r in group)
        total += cost
        print(f"  {kind + 's':<10}{len(group):>7}{cost:>10,.0f}")
    print(f"  {'-' * 27}")
    print(f"  {'TOTAL':<10}{len(rows):>7}{total:>10,.0f}")
    print(f"\n  ~{total:,.0f} tokens are gone before you type anything.")

    heaviest = sorted(rows, key=lambda r: r[2], reverse=True)[:10]
    print("\n  Heaviest descriptions — trim these first:\n")
    for kind, name, cost in heaviest:
        print(f"    {cost:>5,.0f}  {name} ({kind})")
    print("\n  Estimate: chars / 4. Plugin-provided components are not counted.\n")


def selftest():
    cases = [
        ("---\ndescription: plain text\nname: x\n---\nbody", "plain text"),
        ("---\ndescription: >-\n  folded across\n  two lines\nname: x\n---\n",
         "folded across\n  two lines"),
        ('---\ndescription: "quoted value"\n---\n', "quoted value"),
        ("---\nname: x\n---\nno description here", ""),
        ("no frontmatter at all", ""),
        # description last in frontmatter, nothing following it
        ("---\nname: x\ndescription: trailing\n---\n", "trailing"),
    ]
    for text, expected in cases:
        got = extract_description(text)
        assert got == expected, f"expected {expected!r}, got {got!r}"
    assert tokens("abcd") == 1
    print("selftest ok")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        return selftest()
    root = pathlib.Path(args[0]).expanduser() if args else pathlib.Path.home() / ".claude"
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")
    report(root, scan(root))


if __name__ == "__main__":
    main()
