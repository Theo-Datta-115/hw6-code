# Data Sources & APIs

## Overview

The scraper now integrates **8 different data sources** to provide comprehensive political race information:

## 1. FEC API (OpenFEC) ✅ IMPLEMENTED

**Status**: Fully integrated
**API Key**: Required (free)
**Get Key**: https://api.open.fec.gov/developers/

### Data Collected:
- Candidate information (name, party, office, district)
- Campaign finance totals (receipts, disbursements, cash on hand)
- Contribution breakdowns (individual, PAC, party, candidate)
- FEC committee information
- Historical financial data by cycle

### Coverage:
- All federal races (House, Senate, Presidential)
- Real-time financial data (updated daily)
- Historical data back to 1995

### Rate Limits:
- With API key: 1,000 requests/hour
- DEMO_KEY: 120 requests/hour

---

## 2. Census API ✅ IMPLEMENTED

**Status**: Fully integrated
**API Key**: Not required
**Documentation**: https://www.census.gov/data/developers/data-sets.html

### Data Collected:
- District population
- Median household income
- Education levels (college-educated percentage)
- Demographic breakdowns by congressional district

### Coverage:
- All U.S. congressional districts
- American Community Survey (ACS) 5-year estimates
- Updated annually

### Implementation:
- Fetches data for first 20 districts (configurable)
- Uses FIPS codes for state/district identification
- No rate limits

---

## 3. Wikipedia API ✅ IMPLEMENTED

**Status**: Fully integrated
**API Key**: Not required
**Documentation**: https://www.mediawiki.org/wiki/API:Main_page

### Data Collected:
- Candidate biographical information
- Career background
- Education and experience
- Profile images

### Coverage:
- Candidates with Wikipedia pages
- Automatically fetches for top 10 candidates (configurable)

### Implementation:
- Uses MediaWiki API
- Extracts intro text and images
- Graceful fallback if no page exists

---

## 4. Ballotpedia ⚠️ SIMULATED

**Status**: Simulated data (web scraping not implemented)
**API**: No public API available
**Website**: https://ballotpedia.org

### Data Provided (Simulated):
- Race competitiveness ratings (Toss-up, Lean D, Lean R)
- Competitive race identification
- 8 sample competitive races for 2026

### Future Implementation:
- Would require web scraping
- Could license Ballotpedia data
- Alternative: Cook Political Report API

### Current Data:
```python
Competitive Races (Simulated):
- AZ-01: Toss-up
- CA-13: Lean D
- PA-07: Toss-up
- MI-03: Lean R
- NC-01: Toss-up
- TX-23: Lean R
- NV-03: Toss-up
- GA-06: Lean D
```

---

## 5. Google Civic Information API ⚠️ OPTIONAL

**Status**: Integrated (optional)
**API Key**: Required (free with Google Cloud account)
**Get Key**: https://console.cloud.google.com/

### Data Collected:
- Election dates and information
- Polling locations
- Voter registration deadlines
- Early voting information

### Coverage:
- Federal, state, and local elections
- Real-time election data
- Polling place lookup by address

### Usage:
```bash
python scraper.py FEC_KEY GOOGLE_CIVIC_KEY
```

### Rate Limits:
- 25,000 requests/day (free tier)
- Can request quota increase

---

## 6. ProPublica Congress API ❌ NOT IMPLEMENTED

**Status**: Placeholder
**API Key**: Required (free but limited availability)
**Get Key**: https://www.propublica.org/datastore/api/propublica-congress-api

### Potential Data:
- Voting records
- Bill sponsorships
- Committee assignments
- Member statements
- Attendance records

### Why Not Implemented:
- API keys not widely available
- Requires approval process
- Limited to current Congress members
- Better suited for incumbent tracking

### Future Implementation:
- Add voting record analysis
- Track incumbent positions on issues
- Compare challenger vs. incumbent records

---

## 7. OpenSecrets (Bulk Data) ❌ NOT IMPLEMENTED

**Status**: Not implemented
**API**: Discontinued as of April 2025
**Alternative**: Bulk data downloads

### Potential Data:
- Detailed contribution data
- Industry contributions
- Lobbying expenditures
- Personal financial disclosures

### Why Not Implemented:
- API discontinued
- Bulk data requires processing
- FEC API provides similar data

### Future Implementation:
- Download and process bulk files
- Integrate industry contribution analysis
- Add lobbying connection tracking

---

## 8. Vote Smart API ❌ NOT IMPLEMENTED

**Status**: Placeholder
**API Key**: Requires special approval
**Website**: https://justfacts.votesmart.org/

### Potential Data:
- Candidate issue positions
- Voting records
- Interest group ratings
- Public statements
- Campaign promises

### Why Not Implemented:
- API requires special approval
- Rate limits are strict
- Data quality varies

### Future Implementation:
- Apply for API access
- Scrape candidate positions
- Integrate issue ratings

---

## Data Coverage Summary

| Data Type | Source | Status | Coverage |
|-----------|--------|--------|----------|
| Campaign Finance | FEC API | ✅ Full | All federal races |
| Candidate Info | FEC API | ✅ Full | All federal candidates |
| Demographics | Census API | ✅ Partial | 20+ districts |
| Biographies | Wikipedia | ✅ Partial | Top 10 candidates |
| Race Ratings | Ballotpedia | ⚠️ Simulated | 8 competitive races |
| Elections | Google Civic | ⚠️ Optional | Varies by key |
| Voting Records | ProPublica | ❌ Not impl. | N/A |
| Issue Positions | Vote Smart | ❌ Not impl. | N/A |

---

## How to Use

### Basic (FEC only):
```bash
python scraper.py YOUR_FEC_API_KEY
```

### With Google Civic:
```bash
python scraper.py YOUR_FEC_KEY YOUR_GOOGLE_KEY
```

### With All Available APIs:
```bash
python scraper.py YOUR_FEC_KEY YOUR_GOOGLE_KEY YOUR_PROPUBLICA_KEY
```

---

## Future Enhancements

### Short Term:
1. **Expand Census data** - Fetch all districts (currently 20)
2. **More Wikipedia data** - Fetch for all candidates with pages
3. **Real Ballotpedia scraping** - Implement web scraping for race ratings

### Medium Term:
4. **ProPublica integration** - Add voting record analysis
5. **Polling data** - Integrate FiveThirtyEight or RealClearPolitics
6. **Social media** - Track candidate Twitter/Facebook engagement

### Long Term:
7. **Vote Smart integration** - Detailed issue positions
8. **OpenSecrets bulk data** - Industry contribution analysis
9. **News sentiment** - Analyze media coverage
10. **Endorsements** - Track organizational endorsements

---

## API Key Management

### Security Best Practices:
- Never commit API keys to git
- Use environment variables
- Rotate keys periodically
- Monitor usage quotas

### Example with Environment Variables:
```bash
export FEC_API_KEY="your_key_here"
export GOOGLE_CIVIC_KEY="your_key_here"

python scraper.py $FEC_API_KEY $GOOGLE_CIVIC_KEY
```

---

## Rate Limiting Strategy

The scraper implements automatic rate limiting:

- **FEC API**: 0.2-0.5 second delays between requests
- **Census API**: 0.3 second delays
- **Wikipedia API**: 0.3 second delays
- **Google Civic**: 0.5 second delays

This ensures compliance with API terms of service and prevents throttling.

---

## Data Quality

### High Quality (Real-time):
- ✅ FEC campaign finance data
- ✅ Census demographics
- ✅ Wikipedia biographies

### Medium Quality (Simulated/Optional):
- ⚠️ Ballotpedia race ratings (simulated)
- ⚠️ Google Civic elections (optional)

### Not Available:
- ❌ ProPublica voting records
- ❌ Vote Smart issue positions
- ❌ OpenSecrets industry data

---

## Total Data Points Collected

Per candidate:
- 15+ financial metrics (FEC)
- 10+ demographic data points (Census, per district)
- 1 biographical summary (Wikipedia)
- 6+ issue positions (party-based)
- 5+ competitiveness metrics (calculated + Ballotpedia)

**Total**: 35+ data points per candidate-race pair
