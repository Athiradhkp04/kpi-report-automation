# Business KPI Automation Report

An end-to-end reporting pipeline that ingests SaaS subscription data and programmatically generates an executive-ready Excel workbook with live formulas, conditional formatting, charts, and threshold-based alerts. The report is automatically regenerated weekly via GitHub Actions and committed back to the repository.

## Dataset Attribution

This project uses the RavenStack synthetic SaaS dataset by River @ Rivalytics.

## Project Structure

```
kpi-report-automation/
├── data/raw/                      # Raw CSV files
│   ├── accounts.csv              # Account information (500 rows)
│   ├── subscriptions.csv         # Subscription data (5,000 rows)
│   └── churn_events.csv          # Churn event details (600 rows)
├── src/
│   ├── load.py                   # Data ingestion and account_current table creation
│   ├── kpis.py                   # KPI calculation logic
│   └── build_report.py           # Excel workbook generation with openpyxl
├── output/
│   └── kpi_report.xlsx           # Generated Excel report (committed by workflow)
├── .github/workflows/
│   └── weekly_report.yml         # GitHub Actions automation (weekly cron)
├── generate_report.py            # Main script to run the pipeline
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd kpi-report-automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the report generation**
   ```bash
   python generate_report.py
   ```

The generated Excel report will be saved to `output/kpi_report.xlsx`.

## KPIs Calculated

The report answers the business question: *"Which plan tier has the highest churn, is that concentrated in specific industries, and what are people actually citing as the reason?"*

### Key Metrics

- **Active MRR**: Monthly Recurring Revenue from active subscriptions (where end_date is null)
- **Active ARR**: Annual Recurring Revenue from active subscriptions
- **Churn Rate by Plan Tier**: Percentage of churned accounts per plan tier (Basic, Pro, Enterprise)
- **Churn Rate by Industry**: Percentage of churned accounts per industry (EdTech, FinTech, DevTools, HealthTech, Cybersecurity)
- **Churn Rate Matrix**: Plan tier × industry cross-tabulation with conditional formatting
- **Top Churn Reasons**: Count of churn reasons from churn events (budget, features, support, pricing, competitor, unknown)

### Data Modeling Approach

The project uses a derived `account_current` table to ensure accurate KPI calculations:
- For each account, the most recent subscription (by start_date) is selected
- This avoids double-counting revenue from historical subscription changes
- Account-level churn_flag from accounts.csv is used as the single source of truth
- Current plan tier (from subscriptions) is used rather than signup plan (from accounts) to correctly attribute churn

## Excel Workbook Structure

The generated workbook contains 3 sheets:

### 1. Summary Sheet
- **Alert Block**: Threshold-based alerts when a plan tier's churn rate exceeds 1.5x the overall average
- **KPI Scorecard**: Active MRR, Active ARR, and churn rates by tier with live Excel formulas
- **Charts**: 
  - Churn rate by plan tier (bar chart)
  - Top churn reasons (bar chart)

### 2. Tier_Industry_Matrix Sheet
- Plan tier × industry churn rate matrix
- Conditional formatting (green→red color scale) to highlight high-churn combinations
- Helps identify which specific tier/industry combinations are underperforming

### 3. Data Sheet
- Cleaned account_current table (500 rows, one per account)
- Contains all raw data used for KPI calculations
- Frozen header row for easy navigation

## Styling Features

- Muted executive palette (navy/slate headers)
- Currency format ($#,##0) for MRR/ARR
- Percentage format (0.0%) for churn rates
- Frozen header rows on all sheets
- Auto-fitted column widths
- Bold, distinct header styling

## Automation

The report is automatically regenerated every Monday at 8:00 AM via GitHub Actions:

```yaml
schedule:
  - cron: '0 8 * * 1'  # Weekly on Mondays at 8:00 AM
```

The automation loop:
1. Checks out the repository
2. Sets up Python environment
3. Installs dependencies
4. Runs the report generation script
5. Commits the regenerated `output/kpi_report.xlsx` back to the repository
6. Uploads the report as a workflow artifact

This provides a verifiable commit history proving the automation runs on schedule.

## Manual Trigger

The workflow can also be triggered manually via the GitHub Actions UI for ad-hoc report generation.

## Dependencies

- pandas: Data manipulation and analysis
- openpyxl: Excel workbook generation and formatting

## Data Integrity Notes

The churn_events table contains events for 352 unique accounts, but only 110 accounts are flagged as churned in accounts.csv. Only 75 accounts have both churn_flag=True AND churn_events. To ensure consistency across all KPIs, this project uses accounts.csv churn_flag as the single source of truth. Churn reason analysis is limited to the 75 accounts that have both flags set.

## License

This project uses synthetic data for demonstration purposes. The RavenStack dataset is provided by River @ Rivalytics.