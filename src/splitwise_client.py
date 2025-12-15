"""Splitwise API client module."""

import pandas as pd
from splitwise import Splitwise

from src.config import splitwise as config


def _serialize_object(obj):
    """Recursively serialize Splitwise objects to JSON-friendly dicts.
    
    Handles nested objects, lists, and primitive types.
    """
    if obj is None:
        return None
    
    # Primitive types - return as-is
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # List - serialize each element
    if isinstance(obj, list):
        return [_serialize_object(item) for item in obj]
    
    # Dict - serialize values
    if isinstance(obj, dict):
        return {k: _serialize_object(v) for k, v in obj.items()}
    
    # Object with __dict__ - convert to dict and serialize
    if hasattr(obj, "__dict__"):
        return {k: _serialize_object(v) for k, v in obj.__dict__.items()}
    
    # Fallback - convert to string
    return str(obj)


def get_client() -> Splitwise:
    """Create authenticated Splitwise client using API key.
    
    Returns:
        Authenticated Splitwise client instance.
        
    Raises:
        ValueError: If api_key is not configured.
    """
    if not config.api_key:
        raise ValueError("Missing api_key environment variable")
    
    print(f"Connecting to Splitwise with API key: {config.api_key[:8]}...")
    return Splitwise("", "", api_key=config.api_key)


def get_raw_expenses(client: Splitwise) -> pd.DataFrame:
    """Fetch ALL raw expense data from Splitwise (for backup/cache).
    
    Returns a DataFrame with ALL fields and ALL records from Splitwise,
    including payments/settlements. This is intended for backup purposes.
    
    Args:
        client: Authenticated Splitwise client.
        
    Returns:
        DataFrame with complete raw expense data from Splitwise.
        
    Note:
        If group_id is not configured, fetches expenses from ALL groups.
        Uses pagination to retrieve ALL expenses.
    """
    # Build base API parameters
    params = {"visible": True}
    
    if config.group_id:
        params["group_id"] = config.group_id
        print(f"Fetching expenses for group: {config.group_id}")
    else:
        print("⚠️  No group_id configured - fetching expenses from ALL groups")
    
    # Pagination settings
    BATCH_SIZE = 100
    offset = 0
    all_expenses = []
    
    # Fetch all expenses in batches
    print("Fetching all expenses with pagination...")
    while True:
        batch = client.getExpenses(limit=BATCH_SIZE, offset=offset, **params)
        if not batch:
            break
        all_expenses.extend(batch)
        print(f"  Fetched {len(all_expenses)} records so far...")
        offset += BATCH_SIZE
    
    print(f"Retrieved {len(all_expenses)} total records from Splitwise API")

    # Convert to DataFrame with ALL fields, properly serializing nested objects
    print("Serializing expense data...")
    dicts = [_serialize_object(obj) for obj in all_expenses]
    df = pd.DataFrame(dicts)
    
    return df


def process_for_dashboard(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Process raw expenses for dashboard display.
    
    Filters out payments, parses dates/costs, and selects columns
    needed for the dashboard visualization.
    
    Args:
        raw_df: Raw DataFrame from get_raw_expenses().
        
    Returns:
        Processed DataFrame ready for dashboard.
    """
    if raw_df.empty:
        return raw_df.copy()
    
    df = raw_df.copy()
    
    # Filter out payments (settlements)
    if "payment" in df.columns:
        expenses_only = df[df["payment"] == False].copy()
        print(f"Filtered: {len(df)} records → {len(expenses_only)} expenses (excluded {len(df) - len(expenses_only)} payments)")
        df = expenses_only

    # Parse dates
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df[~df["date"].isna()]

    # Parse costs
    if "cost" in df.columns:
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
        df = df[~df["cost"].isna()]

    # Extract category name
    if "category" in df.columns:
        df["category_name"] = df["category"].apply(_extract_category_name)

    # Select relevant columns for dashboard
    wanted_cols = [c for c in [
        "id", "description", "cost", "currency_code", "date", "category_name"
    ] if c in df.columns]
    df = df[wanted_cols].copy()

    # Add month columns
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month_str"] = df["month"].dt.strftime("%Y-%m")

    return df


def _extract_category_name(category) -> str | None:
    """Extract category name from category object or dict."""
    try:
        return getattr(category, "name", None) or (
            category.get("name") if isinstance(category, dict) else None
        )
    except Exception:
        return None
