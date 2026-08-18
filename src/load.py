import pandas as pd
from pathlib import Path

def load_data(data_dir: str = "data/raw"):
    """
    Load and process the RavenStack SaaS dataset.
    
    Returns:
        account_current: DataFrame with one row per account (500 rows)
        churn_events_filtered: DataFrame with churn events for churned accounts only
    """
    data_path = Path(data_dir)
    
    # Load CSV files
    accounts = pd.read_csv(data_path / "accounts.csv")
    subscriptions = pd.read_csv(data_path / "subscriptions.csv")
    churn_events = pd.read_csv(data_path / "churn_events.csv")
    
    # Build derived account_current table
    # For each account_id, take the subscription row with max start_date (most recent/current)
    latest_subs = subscriptions.loc[subscriptions.groupby('account_id')['start_date'].idxmax()]
    
    # Join accounts (industry, churn_flag) + latest subscription (plan_tier, mrr_amount, arr_amount, end_date)
    # CRITICAL: Use account-level churn_flag from accounts.csv only, exclude subscription-level churn_flag
    account_current = pd.merge(
        accounts[['account_id', 'account_name', 'industry', 'churn_flag']],
        latest_subs[['account_id', 'start_date', 'end_date', 'plan_tier', 'mrr_amount', 'arr_amount']],
        on='account_id',
        how='inner'
    )
    
    # Validate result is exactly 500 rows (one per account)
    assert len(account_current) == 500, f"Expected 500 rows in account_current, got {len(account_current)}"
    
    # Filter churn_events to only include accounts where churn_flag=True in accounts.csv
    churned_accounts = set(accounts[accounts['churn_flag'] == True]['account_id'])
    churn_events_filtered = churn_events[churn_events['account_id'].isin(churned_accounts)].copy()
    
    print(f"Loaded {len(account_current)} accounts to account_current table")
    print(f"Filtered churn_events to {len(churn_events_filtered)} events from {churn_events_filtered['account_id'].nunique()} churned accounts")
    
    return account_current, churn_events_filtered