import pandas as pd

def calculate_kpis(account_current, churn_events_filtered):
    """
    Calculate KPIs from the account_current table and filtered churn_events.
    
    Returns:
        Dictionary containing all KPI calculations
    """
    kpis = {}
    
    # Active MRR and ARR (where end_date is null)
    active_accounts = account_current[account_current['end_date'].isna()]
    
    kpis['active_mrr_total'] = active_accounts['mrr_amount'].sum()
    kpis['active_arr_total'] = active_accounts['arr_amount'].sum()
    
    # MRR and ARR by plan tier
    kpis['mrr_by_tier'] = active_accounts.groupby('plan_tier')['mrr_amount'].sum().to_dict()
    kpis['arr_by_tier'] = active_accounts.groupby('plan_tier')['arr_amount'].sum().to_dict()
    
    # Churn rate by plan tier (% of accounts with churn_flag = True)
    churn_by_tier = account_current.groupby('plan_tier')['churn_flag'].agg(['sum', 'count'])
    kpis['churn_rate_by_tier'] = (churn_by_tier['sum'] / churn_by_tier['count'] * 100).to_dict()
    
    # Churn rate by industry
    churn_by_industry = account_current.groupby('industry')['churn_flag'].agg(['sum', 'count'])
    kpis['churn_rate_by_industry'] = (churn_by_industry['sum'] / churn_by_industry['count'] * 100).to_dict()
    
    # Churn rate by plan tier × industry (matrix)
    tier_industry_pivot = account_current.pivot_table(
        values='churn_flag',
        index='plan_tier',
        columns='industry',
        aggfunc='mean'
    ) * 100
    kpis['churn_rate_matrix'] = tier_industry_pivot
    
    # Overall churn rate
    total_churned = account_current['churn_flag'].sum()
    total_accounts = len(account_current)
    kpis['overall_churn_rate'] = (total_churned / total_accounts) * 100
    
    # Top churn reasons
    kpis['top_churn_reasons'] = churn_events_filtered['reason_code'].value_counts().to_dict()
    
    # Top churn reason per plan tier
    churn_with_tier = pd.merge(
        churn_events_filtered,
        account_current[['account_id', 'plan_tier']],
        on='account_id',
        how='left'
    )
    kpis['top_reason_by_tier'] = {}
    for tier in churn_with_tier['plan_tier'].unique():
        tier_churn = churn_with_tier[churn_with_tier['plan_tier'] == tier]
        if len(tier_churn) > 0:
            kpis['top_reason_by_tier'][tier] = tier_churn['reason_code'].value_counts().idxmax()
    
    # Alert calculation: check if any tier's churn rate > 1.5x overall average
    kpis['alert_tiers'] = []
    for tier, rate in kpis['churn_rate_by_tier'].items():
        if rate > (kpis['overall_churn_rate'] * 1.5):
            kpis['alert_tiers'].append({
                'tier': tier,
                'rate': rate,
                'overall': kpis['overall_churn_rate']
            })
    
    return kpis