---
name: codebase-audit
description: Perform a comprehensive, platform-agnostic static audit of an entire codebase. Use this skill whenever the user asks to audit, review, or assess a codebase for quality, consistency, architecture, or security — even if they phrase it casually like "check my code", "review this repo", "find problems in my project", or "what's wrong with this codebase". Also trigger when the user asks for architecture recommendations, code smell detection, dependency health checks, or security hygiene reviews across a project. Do NOT use for single-file code reviews, runtime profiling, or performance benchmarking.
---

# Universal Codebase Audit Skill

Perform a comprehensive, platform-agnostic static audit of the entire codebase. The project is assumed to be runnable — no runtime or build verification needed. Focus on code quality, consistency, architecture, and security standards regardless of the underlying language or framework.

## Step 0: Project Context (Infer First, Ask Only If Needed)

Before reading source code, try to infer what the project does:

1. Read the `README`, any architecture docs, and the top-level config files (e.g., `package.json`, `Podfile`, `build.gradle`, `go.mod`).
2. If these provide a clear picture of the project's purpose, scale, and platform — proceed to Step 1 without asking.
3. If the project's intent or platform is genuinely ambiguous (e.g., no README, generic config), ask the user ONE question:

> "I couldn't determine the project's purpose from the README and configs. Could you briefly describe what this project does, its intended scale, and its target platform (e.g., solo iOS app, enterprise Java microservice, team web app)? This helps me recommend an appropriate target architecture."

Wait for the response only if you asked, then proceed.

## Step 1: Discovery (Read Light First)

Do NOT read all source files immediately. Instead:

1. Use `bash` with `find` or `ls -R` to get the file tree — structure and naming only.
2. Use `view` to read dependency and configuration files (e.g., `package.json`, `Podfile`, `build.gradle`, `pom.xml`, `go.mod`, `CMakeLists.txt`, `Dockerfile`, `.env.example`, CI/CD pipelines).
3. Use `view` to read the `README` or existing architecture docs if present.
4. Use `bash` with `find <root> -name '*.ext' | wc -l` to count source files per language.
5. From this alone, identify:
   - Tech stack (languages, frameworks, native vs. cross-platform, major libraries).
   - Intended architecture (MVC, MVVM, VIPER, Clean Architecture, layered, microservices, etc.).
   - Domain boundaries (e.g., auth, networking, UI, local storage).
   - Total source file count (needed for Step 2 scoping).

## Step 2: Scope and Category Selection

### Codebase Size Guardrails

Based on the file count from Step 1, decide your approach:

- **Small (≤30 source files):** Audit all files across selected categories.
- **Medium (31–80 source files):** Audit all core/business-logic modules fully. For peripheral modules (e.g., generated code, vendored dependencies, test fixtures), scan structure only and flag anything obvious.
- **Large (>80 source files):** Focus on the most critical modules — entry points, core business logic, API surface, and security-sensitive areas. Explicitly list which modules were audited and which were skipped in the final report under a "Coverage" section.

### Audit Category Selection

Present the user with the available audit categories and let them choose which to include. The eight categories are:

1. **Tech Stack Consistency** — Mixed dependency managers, duplicate libraries, dead dependencies.
2. **Structure & Design Patterns** — Folder inconsistencies, mixed patterns, oversized files, naming conventions, leaked business logic, inconsistent error handling.
3. **Security Hygiene** — Hardcoded secrets, unsafe env handling, insecure defaults, injection risks.
4. **Dependency Health** — Outdated or deprecated packages, major version gaps.
5. **Test Coverage Consistency** — Missing test files for core logic, inconsistent testing approaches.
6. **Documentation Consistency** — Missing docstrings on public APIs, outdated architecture docs.
7. **Logging & Observability** — Inconsistent logging, sensitive data in logs, missing log coverage.
8. **Code Duplication** — Copy-pasted utilities, UI components, or extensions across modules.

Default recommendation: for most projects, categories 1–3 (stack, structure, security) give the highest value. Suggest this default but let the user override.

## Step 3: Chunked Codebase Analysis

Analyze the codebase one domain or top-level module at a time. Do NOT try to load the entire codebase into a single analysis pass. For each module:

1. Use `view` to read its source files (respecting the size guardrails from Step 2).
2. Use `bash` with `grep` for targeted searches (e.g., `grep -rn 'TODO\|FIXME\|HACK'`, `grep -rn 'api_key\|secret\|password'` for security scanning).
3. Check only the categories the user selected.

For each selected category, here is what to look for:

### Tech Stack Consistency
- Mixed dependency managers (e.g., CocoaPods + Swift Package Manager, npm + yarn).
- Conflicting or duplicate libraries serving the same purpose.
- Dead dependencies (declared but never imported/used).

### Structure & Design Pattern Consistency
- Folder structure inconsistencies across modules.
- Mixed design patterns in the same layer (e.g., Repository pattern in some services, direct DB queries in others).
- Oversized files — files significantly larger than their module's average line count. A 500-line file in a module averaging 100 lines is a smell; a 500-line file in a module averaging 400 lines is probably fine. Use relative comparison, not a fixed threshold.
- Inconsistent naming conventions (camelCase vs snake_case vs PascalCase).
- Business logic leaking into UI components or network interceptors.
- Missing or inconsistent error handling patterns.

### Security Hygiene (Static Only)
- Hardcoded secrets, API keys, certificates, or tokens in source files.
- Unsafe environment variable or build-config handling.
- Insecure defaults (e.g., allowing cleartext HTTP, logging sensitive user data).
- Obvious injection risks (string-concatenated SQL, unsafe raw HTML rendering).

### Dependency Health
- Flag visibly outdated or deprecated packages from config files.
- Note packages with known major version gaps.

### Test Coverage Consistency
- Modules or core logic files with no corresponding test files.
- Inconsistent testing approaches across the codebase.

### Documentation Consistency
- Public APIs, classes, or exported functions with no docstrings.
- Missing or outdated architecture documentation.

### Logging & Observability
- Modules that log extensively vs modules with no logging.
- Inconsistent log levels or formats across the codebase.
- Sensitive data appearing in log statements.

### Code Duplication
- Utility functions, UI components, or extensions copy-pasted across modules that should be abstracted into a shared module.

## Step 4: Clean Code Pass

1. From all findings, identify the 3 most problematic files.
2. Use `view` to read these files in full.
3. Analyze them against core principles: SRP, DRY, KISS, guard clauses, naming clarity.
4. Present proposed changes — do NOT auto-fix.

## Step 5: Architecture Recommendation

Based on the project context from Step 0 and findings above:

1. Describe the current architecture as-found.
2. Identify whether it fits the project's goals, platform norms, and scale.
3. Recommend a target architecture with rationale (e.g., "Given this is a scaling iOS app, moving from Massive View Controllers to a coordinator-driven MVVM pattern would resolve the lifecycle leakage found in X, Y, Z").
4. Propose a migration path from current to target — incremental, not a full rewrite.

## Output

Generate the audit report as `audit-report.html` in the project root.

To produce the report, run the bundled generation script:

```bash
python3 /path/to/codebase-audit/scripts/generate_audit_report.py \
  --output audit-report.html \
  --findings findings.json
```

Before running the script, write a `findings.json` file containing the structured audit data. The JSON schema is:

```json
{
  "project_name": "MyApp",
  "generated_date": "2026-04-06",
  "context": "One paragraph describing project scale and platform.",
  "tech_stack": ["Python 3.11", "FastAPI", "PostgreSQL", "Docker"],
  "current_architecture": "Layered monolith with service/repository pattern.",
  "coverage_note": "Audited: src/api, src/core, src/models. Skipped: tests/, scripts/, migrations/.",
  "categories": {
    "structure_patterns": [
      {"description": "Mixed error handling — some endpoints use try/except, others use Result types.", "severity": "confirmed"}
    ],
    "security_hygiene": [
      {"description": "DATABASE_URL hardcoded in config.py line 14.", "severity": "confirmed"}
    ],
    "tech_stack_consistency": [],
    "dependency_health": [],
    "test_coverage": [],
    "documentation": [],
    "logging_observability": [],
    "code_duplication": []
  },
  "clean_code_files": [
    {
      "file": "src/api/handlers.py",
      "issues": "Handles 6 unrelated endpoints, mixes auth logic with business logic, no error handling.",
      "proposed_changes": "Split into auth_handler.py and order_handler.py. Extract auth checks into middleware."
    }
  ],
  "target_architecture": {
    "recommendation": "Move to a domain-driven layered structure with dedicated service classes.",
    "rationale": "The current flat structure causes cross-cutting concerns to leak between modules.",
    "migration_path": "1. Extract auth middleware. 2. Create service classes per domain. 3. Introduce repository interfaces."
  }
}
```

Severity values: `"confirmed"` (definitely an issue), `"likely"` (probable issue, needs verification), `"uncertain"` (might be intentional).

Only include categories the user selected in Step 2. Omit unselected categories from the JSON entirely.

### Manual Verification Reminder

Always include a section in the report reminding the user to:
- Run platform-specific vulnerability scanners (e.g., OWASP, `npm audit`, `pip-audit`).
- Run platform linters (e.g., SwiftLint, Ktlint, ESLint, Ruff).
- Check actual test coverage percentages with their CI tools.
