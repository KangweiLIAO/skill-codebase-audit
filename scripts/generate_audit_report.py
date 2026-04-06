#!/usr/bin/env python3
"""
Generate a styled HTML audit report from a findings.json file.

Usage:
    python3 generate_audit_report.py --findings findings.json --output audit-report.html
"""

import argparse
import json
import sys
from html import escape

SEVERITY_BADGE = {
    "confirmed": '<span class="badge confirmed">Confirmed</span>',
    "likely": '<span class="badge likely">Likely</span>',
    "uncertain": '<span class="badge uncertain">Uncertain</span>',
}

CATEGORY_TITLES = {
    "tech_stack_consistency": "Tech Stack Consistency",
    "structure_patterns": "Structure &amp; Design Patterns",
    "security_hygiene": "Security Hygiene",
    "dependency_health": "Dependency Health",
    "test_coverage": "Test Coverage Consistency",
    "documentation": "Documentation Consistency",
    "logging_observability": "Logging &amp; Observability",
    "code_duplication": "Code Duplication",
}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Codebase Audit Report</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --border: #334155;
            --confirmed: #ef4444;
            --likely: #f59e0b;
            --uncertain: #3b82f6;
            --green: #22c55e;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{ border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }}
        h1 {{ margin: 0 0 0.5rem 0; font-size: 2rem; color: var(--accent); }}
        h2 {{ font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-top: 2.5rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }}
        .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }}
        .card h3 {{ margin-top: 0; color: var(--accent); }}
        ul {{ padding-left: 1.5rem; margin: 0.5rem 0; }}
        li {{ margin-bottom: 0.5rem; }}
        .badge {{
            display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px;
            font-size: 0.75rem; font-weight: bold; text-transform: uppercase;
            letter-spacing: 0.05em; margin-left: 0.5rem;
        }}
        .badge.confirmed {{ background: rgba(239, 68, 68, 0.2); color: var(--confirmed); }}
        .badge.likely {{ background: rgba(245, 158, 11, 0.2); color: var(--likely); }}
        .badge.uncertain {{ background: rgba(59, 130, 246, 0.2); color: var(--uncertain); }}
        code {{
            background: #0b1120; padding: 0.2rem 0.4rem; border-radius: 4px;
            font-family: ui-monospace, monospace; font-size: 0.9em;
        }}
        .limitations {{
            background: #451a03; border: 1px solid #78350f;
            border-radius: 8px; padding: 1.5rem; margin-top: 3rem;
        }}
        .limitations h3 {{ color: #fbbf24; margin-top: 0; }}
        .coverage-note {{
            background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 8px; padding: 1rem 1.5rem; margin: 1rem 0;
            color: var(--green);
        }}
        .file-block {{ margin-bottom: 1.5rem; }}
        .file-block h4 {{ color: var(--accent); margin-bottom: 0.25rem; }}
        .file-block p {{ margin: 0.25rem 0; }}
        .summary-stat {{
            display: inline-block; text-align: center; padding: 0.75rem 1.5rem;
            background: var(--card-bg); border: 1px solid var(--border);
            border-radius: 8px; margin-right: 0.75rem; margin-bottom: 0.75rem;
        }}
        .summary-stat .num {{ font-size: 1.75rem; font-weight: bold; color: var(--accent); }}
        .summary-stat .label {{ font-size: 0.8rem; color: var(--text-muted); }}
        .empty-category {{ color: var(--text-muted); font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Codebase Insight Report</h1>
            <p style="color: var(--text-muted)">Generated: {generated_date} | Project: {project_name}</p>
            <p><strong>Context:</strong> {context}</p>
        </header>

        {summary_stats}

        {coverage_note}

        <h2>High-Level Overview</h2>
        <div class="grid">
            <div class="card">
                <h3>Tech Stack Detected</h3>
                <ul>{tech_stack_items}</ul>
            </div>
            <div class="card">
                <h3>Current Architecture</h3>
                <p>{current_architecture}</p>
            </div>
        </div>

        <h2>Audit Findings</h2>
        {category_cards}

        <h2>Clean Code Pass (Top Problematic Files)</h2>
        {clean_code_section}

        <h2>Target Architecture Recommendation</h2>
        <div class="card">
            <p><strong>Recommendation:</strong> {arch_recommendation}</p>
            <p><strong>Rationale:</strong> {arch_rationale}</p>
            <p><strong>Migration Path:</strong> {arch_migration}</p>
        </div>

        <h2>Manual Verification Required</h2>
        <div class="card">
            <ul>
                <li>Run platform-specific vulnerability scanners (e.g., OWASP, <code>npm audit</code>, <code>pip-audit</code>)</li>
                <li>Run platform linters (e.g., SwiftLint, Ktlint, ESLint, Ruff)</li>
                <li>Check actual test coverage percentages with CI tools</li>
            </ul>
        </div>

        <div class="limitations">
            <h3>&#9888;&#65039; What This Audit Cannot Tell You</h3>
            <ul>
                <li>Runtime behavior, memory leaks, or performance bottlenecks under load.</li>
                <li>Whether flagged inconsistencies are deliberate (legacy constraints, intentional divergence).</li>
                <li>Actual test coverage execution percentages.</li>
                <li>Whether static dependency vulnerabilities are actually exploitable in this app's context.</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""


def load_findings(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_tech_stack(items: list) -> str:
    if not items:
        return "<li><em>No tech stack detected</em></li>"
    return "\n".join(f"                    <li>{escape(item)}</li>" for item in items)


def render_category_cards(categories: dict) -> str:
    cards = []
    for key, findings in categories.items():
        title = CATEGORY_TITLES.get(key, key.replace("_", " ").title())
        if not findings:
            cards.append(
                f'<div class="card">\n'
                f"    <h3>{title}</h3>\n"
                f'    <p class="empty-category">No issues found.</p>\n'
                f"</div>"
            )
            continue
        items = []
        for f in findings:
            desc = escape(f["description"])
            sev = f.get("severity", "uncertain")
            badge = SEVERITY_BADGE.get(sev, SEVERITY_BADGE["uncertain"])
            items.append(f"        <li>{desc} {badge}</li>")
        cards.append(
            f'<div class="card">\n'
            f"    <h3>{title}</h3>\n"
            f"    <ul>\n" + "\n".join(items) + "\n    </ul>\n"
            f"</div>"
        )
    return "\n".join(cards)


def render_clean_code(files: list) -> str:
    if not files:
        return '<div class="card"><p class="empty-category">No specific files flagged.</p></div>'
    blocks = []
    for entry in files:
        blocks.append(
            f'<div class="file-block">\n'
            f'    <h4><code>{escape(entry["file"])}</code></h4>\n'
            f'    <p><strong>Issues:</strong> {escape(entry["issues"])}</p>\n'
            f'    <p><strong>Proposed changes:</strong> {escape(entry["proposed_changes"])}</p>\n'
            f"</div>"
        )
    return '<div class="card">\n' + "\n".join(blocks) + "\n</div>"


def count_by_severity(categories: dict) -> dict:
    counts = {"confirmed": 0, "likely": 0, "uncertain": 0}
    for findings in categories.values():
        for f in findings:
            sev = f.get("severity", "uncertain")
            counts[sev] = counts.get(sev, 0) + 1
    return counts


def render_summary_stats(categories: dict) -> str:
    counts = count_by_severity(categories)
    total = sum(counts.values())
    cats_audited = len(categories)
    return (
        f'<div style="margin: 1.5rem 0;">\n'
        f'    <div class="summary-stat"><div class="num">{total}</div><div class="label">Total Findings</div></div>\n'
        f'    <div class="summary-stat"><div class="num">{counts["confirmed"]}</div><div class="label">Confirmed</div></div>\n'
        f'    <div class="summary-stat"><div class="num">{counts["likely"]}</div><div class="label">Likely</div></div>\n'
        f'    <div class="summary-stat"><div class="num">{counts["uncertain"]}</div><div class="label">Uncertain</div></div>\n'
        f'    <div class="summary-stat"><div class="num">{cats_audited}</div><div class="label">Categories Audited</div></div>\n'
        f"</div>"
    )


def render_coverage_note(note: str) -> str:
    if not note:
        return ""
    return f'<div class="coverage-note"><strong>Audit Coverage:</strong> {escape(note)}</div>'


def main():
    parser = argparse.ArgumentParser(description="Generate HTML audit report from findings JSON.")
    parser.add_argument("--findings", required=True, help="Path to findings.json")
    parser.add_argument("--output", required=True, help="Output HTML file path")
    args = parser.parse_args()

    data = load_findings(args.findings)

    categories = data.get("categories", {})
    target = data.get("target_architecture", {})
    clean_code = data.get("clean_code_files", [])

    html = HTML_TEMPLATE.format(
        generated_date=escape(data.get("generated_date", "N/A")),
        project_name=escape(data.get("project_name", "Unknown")),
        context=escape(data.get("context", "No context provided.")),
        summary_stats=render_summary_stats(categories),
        coverage_note=render_coverage_note(data.get("coverage_note", "")),
        tech_stack_items=render_tech_stack(data.get("tech_stack", [])),
        current_architecture=escape(data.get("current_architecture", "Not determined.")),
        category_cards=render_category_cards(categories),
        clean_code_section=render_clean_code(clean_code),
        arch_recommendation=escape(target.get("recommendation", "None provided.")),
        arch_rationale=escape(target.get("rationale", "None provided.")),
        arch_migration=escape(target.get("migration_path", "None provided.")),
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
