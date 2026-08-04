"""Integration helpers between the OctoDNS Metaname provider and op_opsdevnz secrets."""

import os
from typing import Optional

from .onepassword import get_secret as op_get_secret


def _prefer_cli() -> bool:
    """Resolution order for the hook (see docs/design/fallback-policy.md).

    Workstations (no service-account token) resolve CLI-first, where the
    signed-in ``op`` session is the intended principal. When
    ``OP_SERVICE_ACCOUNT_TOKEN`` is set, the SDK path runs first; in CI the
    CLI and SDK authenticate as the same service-account principal, so the
    order carries no credential downgrade risk there.
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
