"""Integration helpers between OctoDNS Metaname provider and opsdevnz secrets."""

from typing import Optional

from .onepassword import get_secret as opsdevnz_get_secret


def resolve(name: str, reference: Optional[str] = None) -> Optional[str]:
    """Resolve secrets via 1Password using the opsdevnz helper.

    Parameters
    ----------
    name:
        Logical name of the secret (e.g., ``METANAME_API_TOKEN``).
    reference:
        Optional reference retrieved from ``<NAME>_REF``. When present this is
        passed directly to 1Password; otherwise we rely on ``opsdevnz_get_secret``
        to look up any matching reference env variable.
    """

    if reference:
        return opsdevnz_get_secret(
            secret_ref=reference,
            env_override=name,
            prefer_cli=True,
        )
    return opsdevnz_get_secret(
        secret_ref_env=f"{name}_REF",
        env_override=name,
        prefer_cli=True,
    )
