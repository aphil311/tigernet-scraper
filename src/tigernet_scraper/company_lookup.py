"""Company lookup utilities for mapping company names to TigerNet company IDs."""

from pathlib import Path
import json

LOOKUP_FILE = Path(__file__).parent / "data" / "company_ids.json"


def load_company_ids() -> dict[str, str]:
    """Load mapping of company name -> company_id from JSON file.

    Returns:
        dict mapping company names (as they appear in the lookup) to company IDs.
        If the file doesn't exist or is invalid, returns an empty dict.
    """
    if not LOOKUP_FILE.exists():
        return {}
    try:
        with open(LOOKUP_FILE) as f:
            data = json.load(f)
            # Ensure keys and values are strings
            return {str(k): str(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        return {}


def get_company_id(company: str) -> str | None:
    """Get company ID from lookup table.

    First tries exact match with the provided company name.
    If not found, tries case-insensitive match.

    Args:
        company: The company name to look up.

    Returns:
        The company ID as a string if found, otherwise None.
    """
    mapping = load_company_ids()
    # Exact match (preserve case as stored)
    if company in mapping:
        return mapping[company]
    # Case-insensitive fallback
    lowered = company.lower()
    for name, cid in mapping.items():
        if name.lower() == lowered:
            return cid
    return None
