"""Integration helpers between the OctoDNS Metaname provider and op_opsdevnz secrets.

Deprecated: this provider-specific adapter is retained temporarily for
compatibility. It is intended to move into the ``octodns-metaname`` module,
leaving ``op-opsdevnz`` focused on generic secret resolution.
"""

import os
from typing import Optional

from .onepassword import get_secret as op_get_secret


def _prefer_cli() -> bool:
    """Resolution order for the hook (see docs/design/fallback-policy.md).

    Workstations (no service-account token) resolve CLI-first, where the
    signed-in ``op`` session is the intended principal. When
    ``OP_SERVICE_ACCOUNT_TOKEN`` is set, the SDK path runs first and any
    failure is a hard error — no fallback.

    The one remaining CLI path with a token set (SDK not installed) stays
    same-principal: the ``op`` CLI itself authenticates via
    ``OP_SERVICE_ACCOUNT_TOKEN`` when it is present. This assumes CI runners
    never carry a signed-in CLI session for a *different* principal alongside
    the token; such a runner would be a misconfiguration to fix, not to
    accommodate.
    """
    return not os.getenv("OP_SERVICE_ACCOUNT_TOKEN")


def resolve(name: str, reference: Optional[str] = None) -> Optional[str]:
    """Resolve secrets via 1Password using the op_opsdevnz helper.

    Parameters
    ----------
    name:
        Logical name of the secret (e.g., ``METANAME_API_TOKEN``).
    reference:
        Optional reference retrieved from ``<NAME>_REF``. When present this is
        passed directly to 1Password; otherwise we rely on ``op_get_secret``
        to look up any matching reference env variable.
    """

    if reference:
        return op_get_secret(
            secret_ref=reference,
            env_override=name,
            prefer_cli=_prefer_cli(),
        )
    return op_get_secret(
        secret_ref_env=f"{name}_REF",
        env_override=name,
        prefer_cli=_prefer_cli(),
    )
