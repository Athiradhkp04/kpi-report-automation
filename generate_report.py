#!/usr/bin/env python3
"""
Main script to generate the KPI automation report.
This script loads data, calculates KPIs, and builds the Excel report.
"""

from src.load import load_data
from src.kpis import calculate_kpis
from src.build_report import build_excel_report

def main():
    print("Starting KPI report generation...")
    
    # Load data
    print("Loading data...")
    account_current, churn_events_filtered = load_data()
    
    # Calculate KPIs
    print("Calculating KPIs...")
    kpis = calculate_kpis(account_current, churn_events_filtered)
    
    # Print summary
    print(f"\nKPI Summary:")
    print(f"Active MRR: ${kpis['active_mrr_total']:,.0f}")
    print(f"Active ARR: ${kpis['active_arr_total']:,.0f}")
    print(f"Overall churn rate: {kpis['overall_churn_rate']:.1f}%")
    print(f"Churn rate by tier: {kpis['churn_rate_by_tier']}")
    print(f"Top churn reasons: {kpis['top_churn_reasons']}")
    
    if kpis['alert_tiers']:
        print(f"\nALERTS:")
        for alert in kpis['alert_tiers']:
            print(f"  {alert['tier']} churn rate ({alert['rate']:.1f}%) above average ({alert['overall']:.1f}%)")
    else:
        print("\nNo churn rate alerts")
    
    # Build Excel report
    print("\nBuilding Excel report...")
    build_excel_report(account_current, kpis)
    
    print("Report generation complete!")

if __name__ == "__main__":
    main()