# Strategic Political Donation Platform - Database Prototype

**"GiveWell for Politics"** - A data-driven platform to help donors make strategic, high-impact political contributions.

## Overview

This prototype implements the database and data collection infrastructure for a platform that helps individual donors identify where their political donations can have the most impact. Aligned with the project PRD, it focuses on:

1. **Strategic Impact**: Identifying competitive races where donations matter most
2. **Funding Gaps**: Highlighting underfunded but viable candidates
3. **Issue Alignment**: Filtering candidates by policy positions
4. **Transparency**: Clear metrics on competitiveness and leverage
5. **Grassroots Support**: Prioritizing small-dollar funded campaigns

## PRD Alignment

This prototype directly supports the PRD goals:

- **Problem**: Voters want to donate effectively but lack trustworthy guidance
- **Solution**: Data-driven recommendations showing where marginal dollars have maximum impact
- **Personas**: Individual donors (Theo), Campaigns (Josh), Lobbying Groups (Varun)
- **Use Cases**: Issue-based filtering, competitiveness analysis, funding gap identification

## Database Schema

### Core Tables

1. **elections** - Election events and dates
2. **races** - Individual races with competitiveness metrics
3. **candidates** - Candidate profiles and FEC data
4. **campaign_finance** - Fundraising data with leverage calculations
5. **issues** - Political issues (climate, healthcare, etc.)
6. **candidate_issues** - Candidate positions on issues
7. **impact_scores** - Strategic importance calculations
8. **polling_data** - Polling and competitiveness tracking
9. **district_demographics** - Voter base characteristics

### Key Metrics

- **Donation Leverage Score** (0-100): Impact potential per dollar donated
- **Overall Impact Score** (0-100): Strategic importance combining multiple factors
- **Funding Gap**: Difference between candidate and opponent fundraising
- **Small-Dollar Percentage**: Grassroots support indicator
- **Recommendation Tier**: High/Medium/Lower priority classification

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Get free FEC API key
# Visit: https://api.open.fec.gov/developers/
```

## Usage

### 1. Create Database

```bash
python3 database_schema.py
```

Creates the SQLite database with all tables and seeds 15 political issues.

### 2. Populate with Data

```bash
# With API key (recommended)
python3 scraper.py YOUR_FEC_API_KEY

# Without API key (limited rate)
python3 scraper.py
```

The scraper collects:
- 300+ House candidates (2026 cycle)
- 100+ Senate candidates (2026 cycle)
- Campaign finance data for each candidate
- Issue position assignments (party-based)
- Strategic impact score calculations

**Time**: 10-15 minutes with API key, 20-30 minutes without

### 3. Test and Analyze

```bash
python3 test_database.py
```

Generates:
- Database validation report
- Top 10 high-impact donation opportunities
- Underfunded competitive races
- Grassroots-funded candidates
- Issue-based candidate lists
- JSON export of recommendations

## Key Features

### Strategic Donation Recommendations

The platform calculates impact scores based on:

1. **Competitiveness** (30%): How close is the race?
2. **Funding Leverage** (35%): How underfunded is the candidate?
3. **Control Impact** (20%): Does this race affect chamber control?
4. **Grassroots Potential** (15%): Is the campaign grassroots-funded?

### Issue-Based Filtering

Supports filtering by 15 political issues:
- Climate Change
- Healthcare Access
- Immigration Reform
- Economic Justice
- Crime & Safety
- Education
- Reproductive Rights
- Gun Control
- Voting Rights
- Housing Affordability
- Labor Rights
- LGBTQ+ Rights
- Racial Justice
- Foreign Policy
- Infrastructure

### Funding Gap Analysis

Identifies candidates who are:
- Competitive but underfunded (high leverage)
- Running against well-funded opponents
- Viable with additional support

## Example Queries

### Find High-Impact Opportunities

```sql
SELECT 
    c.name,
    c.state,
    r.office,
    ims.overall_impact_score,
    cf.donation_leverage_score,
    cf.funding_gap
FROM impact_scores ims
JOIN candidates c ON ims.candidate_id = c.id
JOIN races r ON ims.race_id = r.id
JOIN campaign_finance cf ON c.id = cf.candidate_id
WHERE ims.overall_impact_score > 70
ORDER BY ims.overall_impact_score DESC;
```

### Find Candidates by Issue

```sql
SELECT 
    c.name,
    c.party,
    c.state,
    i.name as issue,
    ci.position,
    ims.overall_impact_score
FROM candidate_issues ci
JOIN candidates c ON ci.candidate_id = c.id
JOIN issues i ON ci.issue_id = i.id
LEFT JOIN impact_scores ims ON c.id = ims.candidate_id
WHERE i.name = 'Climate Change'
ORDER BY ims.overall_impact_score DESC;
```

### Find Underfunded Competitive Races

```sql
SELECT 
    c.name,
    r.office,
    c.state,
    cf.total_receipts,
    cf.opponent_total_receipts,
    cf.funding_ratio,
    cf.donation_leverage_score
FROM campaign_finance cf
JOIN candidates c ON cf.candidate_id = c.id
JOIN race_candidates rc ON c.id = rc.candidate_id
JOIN races r ON rc.race_id = r.id
WHERE cf.funding_ratio < 0.75
AND cf.donation_leverage_score > 65
ORDER BY cf.donation_leverage_score DESC;
```

## Data Sources

### 8 Integrated Data Sources

The scraper now pulls from **multiple APIs** for comprehensive coverage:

#### ✅ Fully Implemented:

1. **FEC API (OpenFEC)** - Campaign finance and candidate data
   - All federal races (House, Senate, Presidential)
   - Real-time financial data (updated daily)
   - 1,000 requests/hour with API key

2. **Census API** - District demographics
   - Population, income, education levels
   - All congressional districts
   - No API key required

3. **Wikipedia API** - Candidate biographies
   - Background and experience
   - Profile images
   - No API key required

4. **Ballotpedia** - Race ratings (simulated)
   - Competitiveness scores
   - 8 competitive races identified
   - (Web scraping not yet implemented)

#### ⚠️ Optional:

5. **Google Civic Information API** - Election data
   - Election dates and polling locations
   - Requires free Google Cloud API key
   - 25,000 requests/day

#### ❌ Planned:

6. **ProPublica Congress API** - Voting records
7. **Vote Smart API** - Issue positions
8. **OpenSecrets** - Industry contributions

**See [API_SOURCES.md](API_SOURCES.md) for detailed documentation**

## Calculation Methodology

### Donation Leverage Score

```
Funding Component (60%):
- Funding ratio < 0.5: 90 points
- Funding ratio 0.5-0.75: 75 points
- Funding ratio 0.75-1.0: 60 points
- Funding ratio 1.0-1.5: 40 points
- Funding ratio > 1.5: 20 points

Competitiveness Component (40%):
- Based on polling margin
- 50% (toss-up) = 100 points
- Further from 50% = lower score

Leverage = (Funding × 0.6) + (Competitiveness × 0.4)
```

### Overall Impact Score

```
Impact = (Competitiveness × 0.30) +
         (Funding Leverage × 0.35) +
         (Control Impact × 0.20) +
         (Grassroots Potential × 0.15)

Tiers:
- High Impact: 75-100
- Medium-High Impact: 60-74
- Medium Impact: 45-59
- Lower Priority: 0-44
```

## File Structure

```
prototype3/
├── database_schema.py          # Database schema and table creation
├── scraper.py                  # Data collection from FEC API
├── test_database.py            # Testing and analytics
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── political_donations.db      # SQLite database (created after running)
└── donation_recommendations.json  # Exported recommendations (created after testing)
```

## PRD Use Cases Supported

### Jordan: Make a Strategic Donation

1. **Issue Selection**: Filter candidates by "Climate Change" and "Economic Justice"
2. **Impact Preferences**: Show candidates in close races (high competitiveness score)
3. **Donation Strategy**: Sort by overall impact score
4. **Candidate Profiles**: Display funding gap, leverage score, polling data
5. **Transparency**: Show calculation methodology and data sources

### Campaign: Increase Visibility

1. **Profile Creation**: Structured candidate data from FEC
2. **Credibility**: Transparent competitiveness and funding metrics
3. **Discovery**: Issue-based filtering connects campaigns to aligned donors
4. **Efficiency**: Highlights underfunded but viable campaigns

### Lobbying Group: Strategic Allocation

1. **Issue Alignment**: Filter for candidates supporting specific policies
2. **Resource Optimization**: Identify high-leverage opportunities
3. **Portfolio Management**: Track multiple races by impact score
4. **Reporting**: Export data for stakeholder justification

## Success Metrics (PRD Aligned)

### Donation Targeting
- % of donations to competitive races (margin < 5%)
- % of donations to underfunded candidates (funding ratio < 0.75)
- Repeat donation rate

### Issue Diversity
- Distribution of donations across issue categories
- % of donations driven by issue filters vs. general recommendations

### Geographic Distribution
- Donations across states and districts
- Urban vs. rural candidate support

## Limitations & Future Work

### Current Limitations

1. **Issue Positions**: Currently assigned by party affiliation
   - **Future**: Scrape from candidate websites, voting records, endorsements

2. **Polling Data**: Not yet integrated
   - **Future**: Integrate FiveThirtyEight, RealClearPolitics APIs

3. **District Demographics**: Table structure exists but not populated
   - **Future**: Integrate Census API data

4. **Race Ratings**: Cook Political Report ratings not included
   - **Future**: Scrape or license Cook ratings

5. **Historical Data**: Limited to current cycle
   - **Future**: Add historical election results for trend analysis

### Roadmap

**Phase 1** (Current): Basic infrastructure and FEC data
**Phase 2**: Polling integration and real competitiveness scores
**Phase 3**: Candidate position scraping from websites
**Phase 4**: District demographics and voter analysis
**Phase 5**: Historical trends and predictive modeling

## Legal & Compliance

- All data from public FEC records
- No donation processing (links to campaign websites)
- Transparent calculation methodology
- Non-partisan recommendations based on strategic metrics
- Complies with FEC API terms of use

## Testing

Run the test suite to validate:

```bash
python3 test_database.py
```

Expected output:
- ✓ All tables exist and populated
- ✓ Impact scores calculated
- ✓ Top recommendations identified
- ✓ Issue-based filtering works
- ✓ JSON export successful

## Support

For questions or issues:
1. Check FEC API documentation: https://api.open.fec.gov/developers/
2. Review test output for data quality
3. Check `data_sources` table for scraping errors

## License

This project uses public FEC data (public domain).

## Acknowledgments

- Federal Election Commission (FEC) for OpenFEC API
- PRD authors for strategic vision
- Political transparency advocates

---

**Built for CS106 - TTS Project**
**Aligned with PRD: "GiveWell for Politics"**
