# Vibe Audit

A static codebase audit skill for Claude that generates a styled, interactive HTML report. Analyzes architecture, code quality, security hygiene, and AI-generated technical debt using Clean Code principles and a "Vibe-Coding" pitfall detector.

![Report Preview](/preview.png)
You can look at the full sample report here: [Sample Report](/sample-audit-report.html)

## What It Does

Point Claude at any codebase and ask it to audit. The skill walks through a three-phase process — reconnaissance, targeted analysis, synthesis — and produces a self-contained `audit-report.html` with:

- **Health score** (0–100) with a circular gauge
- **Coverage grid** showing which paths were audited vs. skipped
- **Categorized findings** with severity badges and 1–10 impact scores, tagged with `(Clean Code)` or `(Vibe-Coding)` origin
- **Architecture recommendation** with an incremental migration path
- **Dark / light theme toggle** — defaults to system preference

The report is a single HTML file with zero external dependencies (except Google Fonts). Open it in any browser, share it with your team, or commit it to your repo.

## Install

### Claude Code (CLI)

```bash
# Personal skill (available in all projects)
mkdir -p ~/.claude/skills
cp -r vibe-audit ~/.claude/skills/

# Project skill (available only in this repo)
mkdir -p .claude/skills
cp -r vibe-audit .claude/skills/
```

### Claude Code Plugin Marketplace

```
/plugin install vibe-audit@KangweiLIAO/vibe-audit
```

### Manual (any agent that supports SKILL.md)

Clone this repo and point your agent's skill directory at the `vibe-audit/` folder. The skill uses the open `SKILL.md` standard and works with Claude Code, Codex CLI, Cursor, Windsurf, and other compatible agents.

## Usage

Just ask Claude naturally:

```
Audit this codebase
```

```
Review my repo for code quality and security issues
```

```
What's wrong with this project? Check architecture and patterns.
```

Claude will:

1. **Discover** the file tree, configs, and README without reading all source files.
2. **Gate** the scope — halt and ask you if the codebase is ambiguous or has >80 source files.
3. **Let you pick** which audit categories to run (defaults to Tech Stack, Structure, Security).
4. **Analyze** module by module through two lenses: Robert C. Martin's Clean Code principles and AI "Vibe-Coding" pitfall detection.
5. **Generate** a `findings.json`, validate it, and render `audit-report.html`.

## Audit Categories

| # | Category | What It Catches |
|---|----------|-----------------|
| 1 | Tech Stack Consistency | Mixed package managers, duplicate libraries, dead dependencies |
| 2 | Structure & Design Patterns | SRP violations, Law of Demeter, mixed async paradigms |
| 3 | Security Hygiene | Hardcoded secrets, OWASP Top 10, wildcard CORS |
| 4 | Dependency Health | Outdated or deprecated packages |
| 5 | Test Coverage Consistency | Untested core logic, placeholder tests, missing F.I.R.S.T. |
| 6 | Documentation Consistency | Missing docstrings, obsolete code, stale READMEs |
| 7 | Logging & Observability | Inconsistent levels, PII in logs, brittle hot paths |
| 8 | Code Duplication | Copy-pasted utils, context-window amnesia, orphaned code |

Categories 1–3 are recommended by default. You can select any combination.

## The Dual-Lens Approach

### Lens A: Clean Code (Robert C. Martin)

Evaluates naming clarity, function design (SRP, argument count, side effects), exception-based error handling, and class cohesion.

### Lens B: Vibe-Coding Pitfalls

Catches AI-specific technical debt that traditional linters miss:

- **Context Window Amnesia** — duplicate logic with slightly different names generated across separate AI sessions
- **Deep Architectural Incoherence** — mixing callbacks with async/await, or multiple design patterns in the same module
- **Verbose Debt** — redundant guard clauses and hyper-fragmented files from over-cautious AI generation

## Project Structure

```
vibe-audit/
├── SKILL.md                          # Skill instructions (153 lines)
├── README.md                         # This file
├── scripts/
│   └── generate_audit_report.py      # Report generator with --validate-only
├── assets/
│   └── template.html                 # HTML report template
└── references/
    └── category-checklists.md        # Per-category audit checklists
```

**Progressive disclosure:** Claude loads only `SKILL.md` (~153 lines) when triggered. The checklists and scripts are loaded on-demand during analysis, keeping context usage minimal.

## JSON Schema

The skill produces a `findings.json` before rendering the report. Key fields:

```jsonc
{
  "project_name": "MyApp",
  "generated_date": "2026-04-07",
  "overall_score": 78,                           // 0-100, auto-computed or explicit
  "context": "Brief project description.",
  "tech_stack": ["Python 3.11", "FastAPI"],
  "current_architecture": "Layered monolith.",
  "coverage": {
    "audited": ["src/api", "src/core"],           // rendered as green path tags
    "skipped": ["tests/", "migrations/"]          // rendered as muted path tags
  },
  "categories": {
    "security_hygiene": [
      {
        "description": "DATABASE_URL hardcoded in config.py line 14.",
        "severity": "confirmed",                  // confirmed | likely | uncertain
        "severity_score": 10                      // 1-10 impact rating
      }
    ]
  },
  "target_architecture": {
    "recommendation": "Domain-driven layered structure.",
    "rationale": "Current flat structure leaks cross-cutting concerns.",
    "migration_path": [                           // array of strings
      "Step 1: Extract auth middleware.",
      "Step 2: Create service classes per domain.",
      "Step 3: Add repository interfaces."
    ]
  }
}
```

Run `python3 scripts/generate_audit_report.py --validate-only --findings findings.json` to catch schema errors before rendering.

## Customization

### Changing the color palette

Edit the CSS custom properties in `assets/template.html` under `:root` (dark theme) and `[data-theme="light"]`. The template uses a three-palette system (earth tones, editorial reds, indigo-grey) — swap any of the `--black`, `--brick-red`, `--space-indigo` families.

### Adding audit categories

1. Add the category key to `CATEGORY_TITLES` in `scripts/generate_audit_report.py`.
2. Add the checklist to `references/category-checklists.md`.
3. Add the key to `VALID_CATEGORY_KEYS` in the script.
4. Reference the new category in `SKILL.md` Step 3.

## Limitations

This is a **static** audit. It cannot tell you:

- Runtime behavior, memory leaks, or performance under load
- Whether flagged inconsistencies are intentional (legacy constraints, deliberate divergence)
- Actual test coverage percentages (run your CI tools)
- Whether dependency vulnerabilities are exploitable in your specific context

Always complement this audit with platform linters (`eslint`, `ruff`, `swiftlint`) and vulnerability scanners (`npm audit`, `pip-audit`, OWASP ZAP).

## Requirements

- Python 3.8+ (standard library only — no pip install needed)
- A browser to view the report

## License

MIT

## Contributing

Issues and PRs welcome. If you extend the audit categories or improve the HTML template, please include a sample `findings.json` and the rendered report for review.
