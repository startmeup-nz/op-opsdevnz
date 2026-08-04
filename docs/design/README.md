# Design Decisions

**Module:** op-opsdevnz<br />
**Status:** Populated as decisions are recorded

---

Design decisions follow the ADR (Architecture Decision Record) format.
Each decision captures the context, options considered, outcome, and
rationale.

## Current Decisions

| ID | Title | Status |
|----|-------|--------|
| 001 | [Service-Account Resolution](service-account-resolution.md) | Accepted (0.2.0) |
| 002 | [Public Namespace](public-namespace.md) | Accepted (0.2.0) |
| 003 | [SDK-to-CLI Fallback Policy](fallback-policy.md) | Accepted (0.2.0) |

- **001 Service-Account Resolution**: Use the real `onepassword-sdk` `Client`
  API in the primary resolver, sourced from `onepassword_sdk.py`, with sync
  entry points unchanged.
- **002 Public Namespace**: Consolidate to a single `op_opsdevnz` package,
  matching the distro name, sibling modules, and existing consumers.
- **003 Fallback Policy**: Fall back to the CLI only when the SDK path is
  unconfigured; hard-fail on SDK auth errors so principals never switch.

## ADR Template

```markdown
- ID: [NNN]-{title}
- Title: short title, representative of solved problem and found solution
- Context: Describe the context and problem statement
- Options: Enumerate considered alternatives
- Outcome: Chosen option with justification
- More Information: Additional context, links to related artifacts
```

## Related

- [Functional Requirements](../specs/functional-requirements.md)
- [NFRs](../specs/NFR.md)
- [Module README](../index.md)
