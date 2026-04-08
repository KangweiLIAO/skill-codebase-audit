#!/usr/bin/env python3
"""
Generate a styled HTML audit report from a findings.json file.

Usage:
    python3 generate_audit_report.py --findings findings.json --output audit-report.html
    python3 generate_audit_report.py --validate-only --findings findings.json
"""

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

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

VALID_SEVERITIES = {"confirmed", "likely", "uncertain"}
REQUIRED_TOP_LEVEL_KEYS = {"project_name", "generated_date", "categories"}
VALID_CATEGORY_KEYS = set(CATEGORY_TITLES.keys())


def load_findings(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_template() -> str:
    """Load the HTML template from the assets directory."""
    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "template.html"
    if not template_path.exists():
        print(f"Error: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def format_text(text: str) -> str:
    """Escape HTML and convert markdown backticks to <code> tags."""
    escaped = escape(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def to_list(value) -> list:
    """Normalize a value to a list of strings. Accepts a list or a numbered string."""
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    text = str(value)
    # Try "Step N" format
    if "Step 1" in text:
        return [s.strip() for s in re.split(r"(?=\bStep \d+)", text) if s.strip()]
    # Try "N." or "N)" format
    parts = re.split(r"(?=\b\d+[\.\)])", text)
    result = [s.strip() for s in parts if s.strip()]
    if len(result) > 1:
        return result
    return [text]


def render_tech_stack(items: list) -> str:
    if not items:
        return "<em>No tech stack detected</em>"
    return "\n".join(
        f'<span class="tech-tag">{escape(item)}</span>' for item in items
    )


def render_coverage_grid(coverage: dict) -> str:
    """Render the two-column coverage grid with audited/skipped path tags."""
    if not coverage:
        return ""

    audited = coverage.get("audited", [])
    skipped = coverage.get("skipped", [])

    if not audited and not skipped:
        return ""

    audited_tags = "".join(
        f'<span class="path-tag">{escape(p)}</span>' for p in audited
    )
    skipped_tags = "".join(
        f'<span class="path-tag">{escape(p)}</span>' for p in skipped
    )

    return (
        '<div class="coverage-grid">\n'
        '    <div class="coverage-box">\n'
        '        <div class="coverage-title audited">'
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        " Paths Audited</div>\n"
        f'        <div class="path-list">{audited_tags}</div>\n'
        "    </div>\n"
        '    <div class="coverage-box">\n'
        '        <div class="coverage-title skipped">'
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>'
        " Paths Skipped</div>\n"
        f'        <div class="path-list">{skipped_tags}</div>\n'
        "    </div>\n"
        "</div>"
    )


def render_category_cards(categories: dict) -> str:
    cards = []
    first = True
    for key, findings in categories.items():
        title = CATEGORY_TITLES.get(key, key.replace("_", " ").title())
        is_open = "open" if first else ""
        first = False

        if not findings:
            continue

        items_html = []
        for f in findings:
            desc = format_text(f.get("description", ""))
            sev = f.get("severity", "uncertain")
            sev_score = f.get("severity_score")

            score_badge = ""
            if sev_score is not None:
                score_badge = (
                    f'<span class="severity-score">Severity: {sev_score}/10</span>'
                )

            items_html.append(
                f"        <li>\n"
                f'            <div class="finding-header">'
                f'<span class="badge {sev}">{sev.title()}</span>'
                f"{score_badge}</div>\n"
                f'            <span style="color: var(--text-body);">{desc}</span>\n'
                f"        </li>"
            )

        cards.append(
            f"<details {is_open}>\n"
            f'    <summary><span class="category-title">{title}</span>'
            f' <span class="item-count">{len(findings)} items</span></summary>\n'
            f'    <div class="details-content"><ul class="finding-list">\n'
            + "\n".join(items_html)
            + "\n    </ul></div>\n"
            f"</details>"
        )
    return "\n".join(cards)


def count_by_severity(categories: dict) -> dict:
    counts = {"confirmed": 0, "likely": 0, "uncertain": 0}
    for findings in categories.values():
        for f in findings:
            sev = f.get("severity", "uncertain")
            counts[sev] = counts.get(sev, 0) + 1
    return counts


def compute_overall_score(categories: dict, explicit_score=None) -> int:
    """
    If an explicit score is provided, use it.
    Otherwise: 100 - (confirmed * 5) - (likely * 2) - (uncertain * 1), clamped [0, 100].
    """
    if explicit_score is not None:
        return max(0, min(100, int(explicit_score)))
    counts = count_by_severity(categories)
    score = (
        100
        - (counts["confirmed"] * 5)
        - (counts["likely"] * 2)
        - (counts["uncertain"] * 1)
    )
    return max(0, min(100, score))


def render_summary_stats(categories: dict) -> str:
    counts = count_by_severity(categories)
    total = sum(counts.values())
    return (
        f'<div class="stat-box total"><span class="stat-num">{total}</span>'
        f'<span class="stat-label">Total Findings</span></div>\n'
        f'<div class="stat-box confirmed"><span class="stat-num">{counts["confirmed"]}</span>'
        f'<span class="stat-label">Confirmed Issues</span></div>\n'
        f'<div class="stat-box likely"><span class="stat-num">{counts["likely"]}</span>'
        f'<span class="stat-label">Likely Risks</span></div>\n'
        f'<div class="stat-box uncertain"><span class="stat-num">{counts["uncertain"]}</span>'
        f'<span class="stat-label">Uncertain / Review</span></div>\n'
    )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_findings(data: dict) -> list[str]:
    errors = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"Missing required top-level key: '{key}'")

    categories = data.get("categories", {})
    if not isinstance(categories, dict):
        errors.append("'categories' must be a JSON object (dict)")
    else:
        for cat_key, findings in categories.items():
            if cat_key not in VALID_CATEGORY_KEYS:
                errors.append(
                    f"Unknown category key: '{cat_key}'. "
                    f"Valid: {', '.join(sorted(VALID_CATEGORY_KEYS))}"
                )
            if not isinstance(findings, list):
                errors.append(f"Category '{cat_key}' must be a list")
                continue
            for i, finding in enumerate(findings):
                if not isinstance(finding, dict):
                    errors.append(f"categories.{cat_key}[{i}]: must be an object")
                    continue
                if "description" not in finding:
                    errors.append(f"categories.{cat_key}[{i}]: missing 'description'")
                sev = finding.get("severity")
                if sev and sev not in VALID_SEVERITIES:
                    errors.append(
                        f"categories.{cat_key}[{i}]: invalid severity '{sev}'"
                    )
                sev_score = finding.get("severity_score")
                if sev_score is not None:
                    try:
                        val = int(sev_score)
                        if val < 1 or val > 10:
                            errors.append(
                                f"categories.{cat_key}[{i}]: severity_score "
                                f"must be 1-10, got {val}"
                            )
                    except (ValueError, TypeError):
                        errors.append(
                            f"categories.{cat_key}[{i}]: severity_score must be a number"
                        )

    coverage = data.get("coverage")
    if coverage is not None:
        if not isinstance(coverage, dict):
            errors.append("'coverage' must be an object with 'audited'/'skipped' arrays")
        else:
            for field in ("audited", "skipped"):
                val = coverage.get(field)
                if val is not None and not isinstance(val, list):
                    errors.append(f"coverage.{field} must be an array")

    target = data.get("target_architecture")
    if target is not None:
        if not isinstance(target, dict):
            errors.append("'target_architecture' must be an object")
        else:
            for field in ("recommendation", "rationale", "migration_path"):
                if field not in target:
                    errors.append(f"target_architecture: missing '{field}'")

    score = data.get("overall_score")
    if score is not None:
        try:
            v = int(score)
            if v < 0 or v > 100:
                errors.append(f"'overall_score' must be 0-100, got {v}")
        except (ValueError, TypeError):
            errors.append(f"'overall_score' must be a number, got '{score}'")

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML audit report from findings JSON."
    )
    parser.add_argument("--findings", required=True, help="Path to findings.json")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate findings.json without generating a report",
    )
    args = parser.parse_args()

    try:
        data = load_findings(args.findings)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.findings}: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {args.findings}", file=sys.stderr)
        sys.exit(1)

    errors = validate_findings(data)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print("Validation passed.")

    if args.validate_only:
        sys.exit(0)

    if not args.output:
        print(
            "Error: --output is required when not using --validate-only",
            file=sys.stderr,
        )
        sys.exit(1)

    template = load_template()

    categories = data.get("categories", {})
    target = data.get("target_architecture", {})

    overall_score = compute_overall_score(categories, data.get("overall_score"))

    migration_steps = to_list(target.get("migration_path", []))
    migration_html = "".join(
        f"<li>{format_text(step)}</li>" for step in migration_steps
    )

    html = template.format(
        generated_date=escape(data.get("generated_date", "N/A")),
        project_name=escape(data.get("project_name", "Unknown")),
        overall_score=overall_score,
        context=format_text(data.get("context", "No context provided.")),
        summary_stats=render_summary_stats(categories),
        coverage_grid=render_coverage_grid(data.get("coverage", {})),
        tech_stack_items=render_tech_stack(data.get("tech_stack", [])),
        current_architecture=format_text(
            data.get("current_architecture", "Not determined.")
        ),
        category_cards=render_category_cards(categories),
        arch_recommendation=format_text(
            target.get("recommendation", "None provided.")
        ),
        arch_rationale=format_text(target.get("rationale", "None provided.")),
        arch_migration_steps=migration_html,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()
