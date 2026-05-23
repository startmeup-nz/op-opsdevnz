# Agents — op_opsdevnz

**Audience:** Contributors and AI assistants working on the op_opsdevnz module.

## IMPORTANT: No Autonomous Commits

AI assistants must NOT commit changes to this repository. Always stage changes
and describe what was done, then wait for human review and confirmation before
committing.

## Secret Resolution

Users resolve 1Password secrets via `op_opsdevnz`:

```
OCTODNS_METANAME_SECRET_RESOLVER="op_opsdevnz.octodns_hooks:resolve"
```

CI environments rely on `_REF` variables pointing to 1Password references.

## Git Signing

This repository is frequently edited by AI agents.

- Never disable or bypass the default git signing configuration.
- Run commits/pushes normally so the signing prompt can appear for the operator.
