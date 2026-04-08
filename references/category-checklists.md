# Audit Category Checklists

Detailed checklists for each audit category. Read only the sections relevant to the user's selected categories. Each category includes checks from both the Clean Code and Vibe-Coding lenses.

## Contents
- Tech Stack Consistency
- Structure & Design Pattern Consistency
- Security Hygiene
- Dependency Health
- Test Coverage Consistency
- Documentation Consistency
- Logging & Observability
- Code Duplication

---

## Tech Stack Consistency

- Mixed dependency managers (e.g., CocoaPods + Swift Package Manager, npm + yarn).
- Conflicting or duplicate libraries serving the same purpose (e.g., both `axios` and `node-fetch` for HTTP requests).
- Dead dependencies — declared in the manifest but never imported or used in source code.
- **Vibe-Coding:** AI-generated imports that pull in entire libraries for a single utility function.

## Structure & Design Pattern Consistency

- Mixed design patterns in the same layer (e.g., Repository pattern in some services, direct DB queries in others).
- Functions or classes violating SRP or exceeding standard length limits. Compare against the module's average line count, not a fixed threshold.
- Inconsistent naming conventions (camelCase vs snake_case vs PascalCase within the same layer).
- Business logic leaking into UI components or network interceptors.
- Chained method calls (Law of Demeter violations).
- **Clean Code:** Functions with more than 2-3 arguments (dyadic/triadic). Functions with boolean flag parameters. Missing or inconsistent error handling patterns.
- **Vibe-Coding:** Deep Architectural Incoherence — mixing async paradigms (callbacks + async/await) in the same module. Hyper-fragmented files that could be a single cohesive module.

## Security Hygiene

- Hardcoded secrets, API keys, certificates, or tokens in source files. Use: `grep -rn 'api_key\|secret\|password\|token\|private_key' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.go' --include='*.rb' --include='*.swift' --include='*.kt'`
- Unsafe environment variable or build-config handling (e.g., falling back to hardcoded defaults when env vars are missing).
- OWASP Top 10 vulnerabilities: SQL injection via string concatenation, broken access controls, unsafe raw HTML rendering, unsanitized user input in shell commands.
- Insecure defaults (e.g., wildcard CORS `Access-Control-Allow-Origin: '*'`, `DEBUG=True` in production configs, logging sensitive user data).

## Dependency Health

- Flag visibly outdated or deprecated packages from config files (check for deprecation notices in comments or changelogs).
- Note packages with known major version gaps (e.g., using v2 when v5 is current).

## Test Coverage Consistency

- Core business logic files with no corresponding test files.
- Tests lacking meaningful assertions (F.I.R.S.T. principles: Fast, Independent, Repeatable, Self-validating, Timely).
- Inconsistent testing approaches across the codebase (e.g., some modules use unit tests, others only integration tests, some have no tests at all).
- Test files that exist but contain only stubs or placeholder tests.

## Documentation Consistency

- Public APIs, classes, or exported functions with no docstrings or JSDoc comments.
- Missing or outdated architecture documentation (README references files or features that no longer exist).
- Obsolete or commented-out code — flag as debt, not documentation.
- **Vibe-Coding:** AI-generated boilerplate comments that describe what code does rather than why.

## Logging & Observability

- Modules that log extensively vs. modules with zero logging.
- Inconsistent log levels or formats across the codebase (e.g., some use structured JSON logging, others use plain text).
- Sensitive data appearing in log statements (PII, tokens, passwords).
- Missing error mapping/logging in hot paths (Brittle Production State).
- Missing correlation IDs or request tracing in service-to-service calls.

## Code Duplication

- Utility functions copy-pasted across modules that should be abstracted into a shared module.
- UI components duplicated with minor variations (candidates for a shared component with props/parameters).
- **Vibe-Coding:** Context Window Amnesia — duplicate logic with slightly different names generated across separate AI sessions. Orphaned code that was superseded but never deleted.
- Configuration or setup code repeated across entry points.
