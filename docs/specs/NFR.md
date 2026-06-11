# Non-Functional Requirements

**Module:** op-opsdevnz<br />
**Status:** Draft

---

## Overview

Non-functional requirements cover security, reliability, compatibility, and code quality standards for op-opsdevnz.

## Requirements

### NFR-1: Security — No secret leakage

The module SHALL NOT log, print, or expose secret values in error messages, stack traces, or debug output.

### NFR-2: Security — Token redaction

Error messages SHALL redact any tokens or secret values before display.

### NFR-3: Reliability — Graceful fallback

When the primary resolver (SDK) fails, the module SHALL attempt the secondary resolver (CLI) before raising an error.

### NFR-4: Reliability — Timeout handling

CLI invocations SHALL have a configurable timeout (default: 10 seconds) to prevent hanging.

### NFR-5: Compatibility — Python versions

The module SHALL support Python 3.10 and later.

### NFR-6: Compatibility — 1Password SDK versions

The module SHALL work with the official `onepassword-sdk` Python package.

### NFR-7: Code quality — Linting

The codebase SHALL pass `ruff` linting with no errors.

### NFR-8: Code quality — Testing

The codebase SHALL maintain test coverage for all public APIs.

---

## Related

- [Functional Requirements](functional-requirements.md)
- [Design Decisions](../design/README.md)
- [User Stories](../stories/README.md)
