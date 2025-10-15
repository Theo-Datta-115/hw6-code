# Quick Start Guide

## Setup (2 minutes)

```bash
cd prototype3

# Install dependencies
pip install -r requirements.txt

# Create database
python3 database_schema.py
```

## Populate Database (10-15 minutes)

```bash
# With your FEC API key
python3 scraper.py 068uBagfChzqkgeAIfwXbLR6Qo20W2KgacxFHhZy
```

## View Results

```bash
# Run comprehensive tests and analytics
python3 test_database.py
```

## What You Get

### Strategic Metrics
- **Donation Leverage Scores**: Impact per dollar
- **Overall Impact Scores**: Strategic importance
- **Funding Gap Analysis**: Underfunded opportunities
- **Issue-Based Filtering**: Find candidates by policy

### PRD-Aligned Features
✓ Competitive race identification
✓ Funding gap calculations
✓ Issue position tracking (15 issues)
✓ Grassroots candidate identification
✓ Strategic impact scoring

### Output Files
- `political_donations.db` - SQLite database
- `donation_recommendations.json` - Top 20 opportunities

## Key Differences from Prototype2

| Feature | Prototype2 | Prototype3 |
|---------|-----------|-----------|
| Focus | General data collection | Strategic donation recommendations |
| Metrics | Basic finance data | Leverage scores, impact scores |
| Issues | None | 15 political issues with candidate positions |
| Analytics | Basic statistics | PRD-aligned use cases |
| Recommendations | None | Tiered impact recommendations |
| Use Case | Data warehouse | "GiveWell for Politics" |

## Next Steps

1. Review `donation_recommendations.json` for top opportunities
2. Query database for issue-specific candidates
3. Integrate with frontend for user-facing platform
4. Add polling data for real-time competitiveness
5. Scrape candidate websites for actual positions
