#!/usr/bin/env python3
"""cc-tax — what your Claude Code config costs before you type anything.

Every skill, agent and command keeps its `description` in the context window for
the whole session. Bodies load on trigger; descriptions are rent you pay upfront.
This script measures that rent.

A session bills for two roots: your home install, plus whatever the project you
opened brings with it. With no arguments both are counted.

Usage:
    python3 cc-tax.py            # audit ~/.claude, plus ./.claude if present
    python3 cc-tax.py PATH       # audit one config root
    python3 cc-tax.py --selftest # verify the parser

Token counts are estimates (chars / 4), the standard rule of thumb. Absolute
numbers shift a few percent by tokenizer; the ranking does not.
"""
import pathlib
import re
import sys
import tempfile

CHARS_PER_TOKEN = 4
# Frontmatter is scanned for `description:` up to the next top-level key.
DESC_RE = re.compile(r"^description:[ \t]*(.*?)(?=^[A-Za-z_][\w-]*:|\Z)", re.S | re.M)
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
# Leading YAML block scalar markers (>-, |, |2) and surrounding quotes are noise.
BLOCK_MARKER_RE = re.compile(r"\A[>|][+-]?\d*\s*")
KINDS = ("skill", "agent", "command")


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


def table(label, rows):
    """Print one root's breakdown. Returns its total token cost."""
    print(f"\n  {label}\n")
    print(f"  {'':<10}{'count':>7}{'tokens':>10}")
    print(f"  {'-' * 27}")
    total = 0.0
    for kind in KINDS:
        group = [r for r in rows if r[0] == kind]
        if not group:
            continue
        cost = sum(r[2] for r in group)
        total += cost
        print(f"  {kind + 's':<10}{len(group):>7}{cost:>10,.0f}")
    print(f"  {'-' * 27}")
    print(f"  {'TOTAL':<10}{len(rows):>7}{total:>10,.0f}")
    return total


def heaviest(rows, limit=10):
    print("\n  Heaviest descriptions — trim these first:\n")
    for kind, name, cost in sorted(rows, key=lambda r: r[2], reverse=True)[:limit]:
        print(f"    {cost:>5,.0f}  {name} ({kind})")


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

    # scan() must find all three component kinds, and only those.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "skills" / "demo").mkdir(parents=True)
        (root / "skills" / "demo" / "SKILL.md").write_text("---\ndescription: abcd\n---\n")
        (root / "agents").mkdir()
        (root / "agents" / "a.md").write_text("---\ndescription: abcdabcd\n---\n")
        (root / "commands").mkdir()
        (root / "commands" / "c.md").write_text("---\nname: c\n---\n")
        rows = scan(root)
        assert sorted(r[0] for r in rows) == ["agent", "command", "skill"], rows
        assert sum(r[2] for r in rows) == 3, rows
    print("selftest ok")


def roots_from(args):
    """One explicit root, or the home install plus the project you are standing in."""
    if args:
        return [pathlib.Path(args[0]).expanduser()]
    home = pathlib.Path.home() / ".claude"
    project = pathlib.Path.cwd() / ".claude"
    if project.is_dir() and project.resolve() != home.resolve():
        return [home, project]
    return [home]


def main():
    args = sys.argv[1:]
    if args and args[0] == "--selftest":
        return selftest()

    roots = roots_from(args)
    labels = ["Home install", "This project"][: len(roots)]
    combined, grand = [], 0.0
    for root, label in zip(roots, labels):
        if not root.is_dir():
            sys.exit(f"Not a directory: {root}")
        rows = scan(root)
        if not rows:
            print(f"\n  {label}: {root}\n  No skills, agents or commands found.")
            continue
        grand += table(f"{label}: {root}", rows)
        combined += rows

    if not combined:
        print("\n  Point the script at a config root: python3 cc-tax.py ~/.claude\n")
        return
    if len(roots) > 1:
        print(f"\n  {'BOTH ROOTS':<10}{len(combined):>7}{grand:>10,.0f}")
    print(f"\n  ~{grand:,.0f} tokens are gone before you type anything.")
    heaviest(combined)
    print("\n  Estimate: chars / 4. Plugin-provided components are not counted.\n")


if __name__ == "__main__":
    main()
