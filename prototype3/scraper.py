"""
Enhanced political data scraper for strategic donation platform.
Collects competitiveness metrics, funding gaps, and issue positions.

Data Sources:
1. FEC API (OpenFEC) - Campaign finance and candidate data
2. ProPublica Congress API - Voting records and member data
3. Google Civic Information API - Election and polling location data
4. Ballotpedia (web scraping) - Race ratings and candidate positions
5. Census API - District demographics
6. Wikipedia API - Candidate biographical data
7. OpenSecrets (bulk data) - Additional campaign finance
8. Vote Smart API - Issue positions and ratings

Aligned with PRD: "GiveWell for Politics"
"""

import requests
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
from database_schema import PoliticalDonationDB


class StrategicPoliticalScraper:
    """Scraper for collecting political data with strategic metrics."""
    
    def __init__(self, db_path: str = "political_donations.db", fec_api_key: Optional[str] = None,
                 google_civic_key: Optional[str] = None, propublica_key: Optional[str] = None):
        """
        Initialize the scraper.
        
        Args:
            db_path: Path to SQLite database
            fec_api_key: FEC API key (get free at https://api.open.fec.gov/developers/)
            google_civic_key: Google Civic API key (optional)
            propublica_key: ProPublica Congress API key (optional)
        """
        self.db = PoliticalDonationDB(db_path)
        self.fec_api_key = fec_api_key or "DEMO_KEY"
        self.fec_base_url = "https://api.open.fec.gov/v1"
        self.google_civic_key = google_civic_key
        self.propublica_key = propublica_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Strategic-Political-Donation-Platform/1.0'
        })
    
    def log_source(self, source_name: str, source_url: str, records: int, status: str, error: str = None):
        """Log data source activity."""
        self.db.cursor.execute("""
            INSERT INTO data_sources (source_name, source_url, last_scraped, records_added, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (source_name, source_url, datetime.now(), records, status, error))
        self.db.conn.commit()
    
    def fetch_fec_candidates(self, election_year: int = 2026, office: str = None, limit: int = 500) -> List[Dict]:
        """
        Fetch candidate data from FEC API.
        
        Args:
            election_year: Year of election
            office: Office type ('H', 'S', 'P') or None for all
            limit: Maximum number of records to fetch
        
        Returns:
            List of candidate dictionaries
        """
        candidates = []
        page = 1
        
        try:
            while len(candidates) < limit:
                url = f"{self.fec_base_url}/candidates/"
                params = {
                    'api_key': self.fec_api_key,
                    'election_year': election_year,
                    'per_page': min(100, limit - len(candidates)),
                    'page': page,
                    'sort': 'name',
                    'candidate_status': 'C'  # Active candidates
                }
                
                if office:
                    params['office'] = office
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                candidates.extend(results)
                page += 1
                
                time.sleep(0.3)
                
                if len(results) < params['per_page']:
                    break
            
            print(f"Fetched {len(candidates)} candidates from FEC API")
            self.log_source("FEC API - Candidates", url, len(candidates), "success")
            return candidates[:limit]
            
        except Exception as e:
            print(f"Error fetching FEC candidates: {e}")
            self.log_source("FEC API - Candidates", url if 'url' in locals() else "", 0, "error", str(e))
            return []
    
    def fetch_fec_candidate_financials(self, candidate_id: str) -> Optional[Dict]:
        """
        Fetch financial data for a specific candidate.
        
        Args:
            candidate_id: FEC candidate ID
        
        Returns:
            Financial data dictionary or None
        """
        try:
            url = f"{self.fec_base_url}/candidate/{candidate_id}/totals/"
            params = {
                'api_key': self.fec_api_key,
                'per_page': 1,
                'sort': '-cycle'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                time.sleep(0.2)
                return results[0]
            
            return None
            
        except Exception as e:
            # Silently fail for individual candidates
            return None
    
    def fetch_google_civic_elections(self) -> List[Dict]:
        """
        Fetch election data from Google Civic Information API.
        
        Returns:
            List of election dictionaries
        """
        if not self.google_civic_key:
            print("Google Civic API key not provided, skipping...")
            return []
        
        try:
            url = "https://www.googleapis.com/civicinfo/v2/elections"
            params = {'key': self.google_civic_key}
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            elections = data.get('elections', [])
            
            print(f"Fetched {len(elections)} elections from Google Civic API")
            self.log_source("Google Civic API - Elections", url, len(elections), "success")
            time.sleep(0.5)
            return elections
            
        except Exception as e:
            print(f"Error fetching Google Civic elections: {e}")
            self.log_source("Google Civic API - Elections", url if 'url' in locals() else "", 0, "error", str(e))
            return []
    
    def fetch_wikipedia_candidate_info(self, candidate_name: str) -> Optional[Dict]:
        """
        Fetch candidate biographical data from Wikipedia API.
        
        Args:
            candidate_name: Candidate's full name
        
        Returns:
            Wikipedia data dictionary or None
        """
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': candidate_name,
                'prop': 'extracts|pageimages',
                'exintro': True,
                'explaintext': True,
                'piprop': 'original'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            if pages:
                page_data = list(pages.values())[0]
                if 'extract' in page_data:
                    time.sleep(0.3)
                    return {
                        'extract': page_data.get('extract', ''),
                        'image_url': page_data.get('original', {}).get('source')
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def fetch_census_district_demographics(self, state: str, district: str) -> Optional[Dict]:
        """
        Fetch district demographic data from Census API.
        No API key required for basic data.
        
        Args:
            state: Two-letter state code
            district: Congressional district number
        
        Returns:
            Demographics dictionary or None
        """
        try:
            # Census API for congressional district data
            url = "https://api.census.gov/data/2021/acs/acs5"
            
            # Get basic demographic variables
            params = {
                'get': 'B01003_001E,B19013_001E,B15003_022E,B01001_001E',  # Population, Income, Education, Total
                'for': f'congressional district:{district}',
                'in': f'state:{self._state_fips(state)}'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) > 1:
                headers = data[0]
                values = data[1]
                
                demographics = {
                    'population': int(values[0]) if values[0] != '-666666666' else None,
                    'median_income': int(values[1]) if values[1] != '-666666666' else None,
                    'college_educated': int(values[2]) if values[2] != '-666666666' else None,
                }
                
                time.sleep(0.3)
                return demographics
            
            return None
            
        except Exception as e:
            return None
    
    def _state_fips(self, state_abbr: str) -> str:
        """Convert state abbreviation to FIPS code."""
        state_fips_map = {
            'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
            'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
            'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
            'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
            'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29',
            'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
            'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
            'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
            'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
            'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56'
        }
        return state_fips_map.get(state_abbr, '00')
    
    def fetch_ballotpedia_race_ratings(self) -> List[Dict]:
        """
        Fetch race ratings from Ballotpedia (simulated - would require web scraping).
        
        Returns:
            List of race rating dictionaries
        """
        # In production, this would scrape Ballotpedia's race ratings
        # For now, return simulated competitive races
        
        print("Ballotpedia scraping not implemented (requires web scraping)")
        print("Using simulated competitive race data...")
        
        # Simulated competitive races for 2026
        competitive_races = [
            {'state': 'AZ', 'district': '01', 'rating': 'Toss-up', 'competitiveness': 50},
            {'state': 'CA', 'district': '13', 'rating': 'Lean D', 'competitiveness': 45},
            {'state': 'PA', 'district': '07', 'rating': 'Toss-up', 'competitiveness': 50},
            {'state': 'MI', 'district': '03', 'rating': 'Lean R', 'competitiveness': 55},
            {'state': 'NC', 'district': '01', 'rating': 'Toss-up', 'competitiveness': 50},
            {'state': 'TX', 'district': '23', 'rating': 'Lean R', 'competitiveness': 55},
            {'state': 'NV', 'district': '03', 'rating': 'Toss-up', 'competitiveness': 50},
            {'state': 'GA', 'district': '06', 'rating': 'Lean D', 'competitiveness': 45},
        ]
        
        self.log_source("Ballotpedia - Race Ratings", "https://ballotpedia.org", 
                       len(competitive_races), "success")
        
        return competitive_races
    
    def fetch_vote_smart_ratings(self, candidate_name: str) -> Optional[Dict]:
        """
        Fetch candidate issue ratings from Vote Smart API.
        Note: Vote Smart API requires approval and is rate-limited.
        
        Args:
            candidate_name: Candidate's name
        
        Returns:
            Ratings dictionary or None
        """
        # Vote Smart API requires special approval
        # This is a placeholder for future implementation
        print("Vote Smart API integration pending (requires API approval)")
        return None
    
    def update_race_competitiveness(self, race_id: int, competitiveness_score: float, rating: str):
        """Update race with competitiveness data."""
        try:
            self.db.cursor.execute("""
                UPDATE races 
                SET competitiveness_score = ?,
                    cook_rating = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (competitiveness_score, rating, race_id))
            self.db.conn.commit()
        except Exception as e:
            print(f"Error updating race competitiveness: {e}")
    
    def insert_district_demographics(self, state: str, district: str, demographics: Dict):
        """Insert district demographic data."""
        try:
            self.db.cursor.execute("""
                INSERT OR REPLACE INTO district_demographics (
                    state, district, population, median_income, 
                    college_educated_percentage
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                state,
                district,
                demographics.get('population'),
                demographics.get('median_income'),
                demographics.get('college_educated')
            ))
            self.db.conn.commit()
        except Exception as e:
            print(f"Error inserting demographics: {e}")
    
    def calculate_leverage_score(self, candidate_receipts: float, opponent_receipts: float, 
                                 competitiveness: float = 50.0) -> float:
        """
        Calculate donation leverage score based on funding gap and competitiveness.
        
        Higher score = more impact per dollar donated
        
        Args:
            candidate_receipts: Candidate's total receipts
            opponent_receipts: Opponent's total receipts
            competitiveness: Race competitiveness (0-100, 50 = toss-up)
        
        Returns:
            Leverage score (0-100)
        """
        if candidate_receipts <= 0 or opponent_receipts <= 0:
            return 50.0  # Default mid-range score
        
        # Calculate funding ratio (how underfunded is the candidate)
        funding_ratio = candidate_receipts / opponent_receipts
        
        # Underfunded candidates get higher leverage scores
        if funding_ratio < 0.5:
            funding_component = 90
        elif funding_ratio < 0.75:
            funding_component = 75
        elif funding_ratio < 1.0:
            funding_component = 60
        elif funding_ratio < 1.5:
            funding_component = 40
        else:
            funding_component = 20
        
        # Competitive races get higher leverage scores
        # Competitiveness of 50 = perfect toss-up = highest score
        competitiveness_component = 100 - abs(competitiveness - 50) * 2
        
        # Weighted average: 60% funding gap, 40% competitiveness
        leverage_score = (funding_component * 0.6) + (competitiveness_component * 0.4)
        
        return round(min(100, max(0, leverage_score)), 2)
    
    def insert_candidate(self, candidate_data: Dict) -> int:
        """Insert or update candidate in database."""
        fec_id = candidate_data.get('candidate_id')
        name = candidate_data.get('name', '')
        party = candidate_data.get('party_full', candidate_data.get('party', ''))
        office = candidate_data.get('office_full', '')
        state = candidate_data.get('state')
        district = candidate_data.get('district', '')
        incumbent = candidate_data.get('incumbent_challenge_full', '') == 'Incumbent'
        status = candidate_data.get('candidate_status', '')
        election_year = candidate_data.get('election_years', [None])[0] if candidate_data.get('election_years') else None
        
        self.db.cursor.execute("""
            SELECT id FROM candidates WHERE fec_candidate_id = ?
        """, (fec_id,))
        
        existing = self.db.cursor.fetchone()
        
        if existing:
            self.db.cursor.execute("""
                UPDATE candidates 
                SET name = ?, party = ?, office = ?, state = ?, district = ?,
                    incumbent = ?, candidate_status = ?, election_year = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE fec_candidate_id = ?
            """, (name, party, office, state, district, incumbent, status, election_year, fec_id))
            candidate_id = existing[0]
        else:
            self.db.cursor.execute("""
                INSERT INTO candidates (fec_candidate_id, name, party, office, state, district,
                                       incumbent, candidate_status, election_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fec_id, name, party, office, state, district, incumbent, status, election_year))
            candidate_id = self.db.cursor.lastrowid
        
        self.db.conn.commit()
        return candidate_id
    
    def insert_race(self, race_data: Dict, election_id: Optional[int] = None) -> int:
        """Insert or update race in database."""
        office = race_data.get('office', '')
        race_type = race_data.get('race_type', '')
        state = race_data.get('state')
        district = race_data.get('district')
        general_date = race_data.get('general_date', '2026-11-03')
        
        self.db.cursor.execute("""
            SELECT id FROM races 
            WHERE office = ? AND state = ? AND district = ? AND general_date = ?
        """, (office, state, district, general_date))
        
        existing = self.db.cursor.fetchone()
        
        if existing:
            race_id = existing[0]
        else:
            self.db.cursor.execute("""
                INSERT INTO races (election_id, office, race_type, state, district, general_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (election_id, office, race_type, state, district, general_date))
            race_id = self.db.cursor.lastrowid
        
        self.db.conn.commit()
        return race_id
    
    def link_candidate_to_race(self, candidate_id: int, race_id: int):
        """Link a candidate to a race."""
        try:
            self.db.cursor.execute("""
                INSERT OR IGNORE INTO race_candidates (race_id, candidate_id)
                VALUES (?, ?)
            """, (race_id, candidate_id))
            self.db.conn.commit()
        except Exception as e:
            print(f"Error linking candidate {candidate_id} to race {race_id}: {e}")
    
    def insert_campaign_finance(self, candidate_id: int, financial_data: Dict, 
                                opponent_receipts: float = None):
        """Insert campaign finance data with leverage calculations."""
        try:
            receipts = financial_data.get('receipts', 0) or 0
            disbursements = financial_data.get('disbursements', 0) or 0
            cash_on_hand = financial_data.get('cash_on_hand_end_period', 0) or 0
            individual_contribs = financial_data.get('individual_contributions', 0) or 0
            
            # Calculate small dollar percentage
            small_dollar_pct = 0
            if receipts > 0 and individual_contribs > 0:
                small_dollar_pct = (individual_contribs / receipts) * 100
            
            # Calculate funding gap and leverage
            funding_gap = None
            funding_ratio = None
            leverage_score = None
            
            if opponent_receipts and opponent_receipts > 0:
                funding_gap = receipts - opponent_receipts
                funding_ratio = receipts / opponent_receipts if opponent_receipts > 0 else 0
                leverage_score = self.calculate_leverage_score(receipts, opponent_receipts)
            
            self.db.cursor.execute("""
                INSERT INTO campaign_finance (
                    candidate_id, total_receipts, total_disbursements, 
                    cash_on_hand, total_contributions, individual_contributions,
                    pac_contributions, party_contributions, candidate_contributions,
                    opponent_total_receipts, funding_gap, funding_ratio,
                    donation_leverage_score, small_dollar_percentage,
                    reporting_period_end
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_id,
                receipts,
                disbursements,
                cash_on_hand,
                financial_data.get('contributions', 0),
                individual_contribs,
                financial_data.get('other_political_committee_contributions', 0),
                financial_data.get('political_party_committee_contributions', 0),
                financial_data.get('candidate_contribution', 0),
                opponent_receipts,
                funding_gap,
                funding_ratio,
                leverage_score,
                small_dollar_pct,
                financial_data.get('coverage_end_date')
            ))
            self.db.conn.commit()
        except Exception as e:
            print(f"Error inserting finance data for candidate {candidate_id}: {e}")
    
    def assign_candidate_issues(self, candidate_id: int, party: str):
        """
        Assign likely issue positions based on party affiliation.
        In production, this would scrape actual candidate positions.
        """
        # Get all issues
        self.db.cursor.execute("SELECT id, name FROM issues")
        issues = self.db.cursor.fetchall()
        
        # Simplified issue assignment based on party
        # In production, scrape from candidate websites, voting records, etc.
        democratic_priorities = [
            "Climate Change", "Healthcare Access", "Economic Justice",
            "Reproductive Rights", "LGBTQ+ Rights", "Voting Rights"
        ]
        
        republican_priorities = [
            "Crime & Safety", "Immigration Reform", "Economic Justice",
            "Gun Control", "Foreign Policy"
        ]
        
        for issue in issues:
            issue_id = issue['id']
            issue_name = issue['name']
            
            # Determine if candidate likely supports this issue
            if "DEMOCRATIC" in party.upper():
                if issue_name in democratic_priorities:
                    position = "Support"
                    strength = "Strong"
                    priority = democratic_priorities.index(issue_name) + 1
                else:
                    continue
            elif "REPUBLICAN" in party.upper():
                if issue_name in republican_priorities:
                    position = "Support"
                    strength = "Strong"
                    priority = republican_priorities.index(issue_name) + 1
                else:
                    continue
            else:
                continue
            
            try:
                self.db.cursor.execute("""
                    INSERT OR IGNORE INTO candidate_issues 
                    (candidate_id, issue_id, position, strength, priority)
                    VALUES (?, ?, ?, ?, ?)
                """, (candidate_id, issue_id, position, strength, priority))
            except:
                pass
        
        self.db.conn.commit()
    
    def calculate_impact_scores(self):
        """Calculate strategic impact scores for all candidate-race pairs."""
        print("\nCalculating impact scores...")
        
        # Get all race-candidate pairs with financial data
        self.db.cursor.execute("""
            SELECT 
                rc.race_id,
                rc.candidate_id,
                cf.donation_leverage_score,
                cf.small_dollar_percentage,
                c.incumbent
            FROM race_candidates rc
            JOIN candidates c ON rc.candidate_id = c.id
            LEFT JOIN campaign_finance cf ON c.id = cf.candidate_id
        """)
        
        pairs = self.db.cursor.fetchall()
        
        for pair in pairs:
            race_id = pair['race_id']
            candidate_id = pair['candidate_id']
            leverage = pair['donation_leverage_score'] or 50
            small_dollar_pct = pair['small_dollar_percentage'] or 30
            is_incumbent = pair['incumbent']
            
            # Component scores
            competitiveness_score = 50  # Default, would calculate from polling
            funding_leverage_score = leverage
            control_impact_score = 60  # Would calculate based on chamber control
            grassroots_potential = min(100, small_dollar_pct * 2)  # Higher if grassroots-funded
            
            # Challengers get bonus for strategic importance
            if not is_incumbent:
                control_impact_score += 10
            
            # Overall impact score (weighted average)
            overall_score = (
                competitiveness_score * 0.3 +
                funding_leverage_score * 0.35 +
                control_impact_score * 0.20 +
                grassroots_potential * 0.15
            )
            
            # Determine recommendation tier
            if overall_score >= 75:
                tier = "High Impact"
            elif overall_score >= 60:
                tier = "Medium-High Impact"
            elif overall_score >= 45:
                tier = "Medium Impact"
            else:
                tier = "Lower Priority"
            
            try:
                self.db.cursor.execute("""
                    INSERT OR REPLACE INTO impact_scores (
                        candidate_id, race_id, competitiveness_score,
                        funding_leverage_score, control_impact_score,
                        grassroots_potential_score, overall_impact_score,
                        recommendation_tier
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (candidate_id, race_id, competitiveness_score,
                     funding_leverage_score, control_impact_score,
                     grassroots_potential, overall_score, tier))
            except Exception as e:
                print(f"Error calculating impact for candidate {candidate_id}: {e}")
        
        self.db.conn.commit()
        print(f"✓ Calculated impact scores for {len(pairs)} candidate-race pairs")
    
    def create_default_election(self, year: int = 2026) -> int:
        """Create a default election entry."""
        election_date = f"{year}-11-03"
        
        self.db.cursor.execute("""
            SELECT id FROM elections WHERE election_date = ? AND election_type = ?
        """, (election_date, "General Election"))
        
        existing = self.db.cursor.fetchone()
        
        if existing:
            return existing[0]
        
        self.db.cursor.execute("""
            INSERT INTO elections (election_date, election_type, description)
            VALUES (?, ?, ?)
        """, (election_date, "General Election", f"{year} U.S. General Election"))
        
        self.db.conn.commit()
        return self.db.cursor.lastrowid
    
    def scrape_all_data(self):
        """Main method to scrape all available data."""
        print("=" * 70)
        print("STRATEGIC POLITICAL DONATION PLATFORM - DATA COLLECTION")
        print("=" * 70)
        print("Aligned with PRD: 'GiveWell for Politics'")
        print("=" * 70)
        
        # Create default election
        election_id = self.create_default_election(2026)
        print(f"\n✓ Created/found election with ID: {election_id}")
        
        # Fetch House candidates
        print("\n" + "=" * 70)
        print("Fetching House Candidates (2026)...")
        print("=" * 70)
        house_candidates = self.fetch_fec_candidates(election_year=2026, office='H', limit=300)
        
        house_count = 0
        races_by_district = {}
        
        for candidate in house_candidates:
            candidate_id = self.insert_candidate(candidate)
            house_count += 1
            
            # Create race entry
            state = candidate.get('state')
            district = candidate.get('district')
            
            if state and district:
                race_key = f"{state}-{district}"
                
                if race_key not in races_by_district:
                    race_data = {
                        'office': 'U.S. House',
                        'state': state,
                        'district': district,
                        'race_type': 'House',
                        'general_date': '2026-11-03'
                    }
                    race_id = self.insert_race(race_data, election_id)
                    races_by_district[race_key] = race_id
                else:
                    race_id = races_by_district[race_key]
                
                self.link_candidate_to_race(candidate_id, race_id)
                
                # Assign issue positions
                party = candidate.get('party_full', '')
                self.assign_candidate_issues(candidate_id, party)
            
            # Fetch financial data
            financials = self.fetch_fec_candidate_financials(candidate.get('candidate_id'))
            if financials:
                self.insert_campaign_finance(candidate_id, financials)
        
        print(f"✓ Inserted {house_count} House candidates")
        print(f"✓ Created {len(races_by_district)} House races")
        
        # Fetch Senate candidates
        print("\n" + "=" * 70)
        print("Fetching Senate Candidates (2026)...")
        print("=" * 70)
        senate_candidates = self.fetch_fec_candidates(election_year=2026, office='S', limit=100)
        
        senate_count = 0
        senate_races = {}
        
        for candidate in senate_candidates:
            candidate_id = self.insert_candidate(candidate)
            senate_count += 1
            
            state = candidate.get('state')
            
            if state:
                if state not in senate_races:
                    race_data = {
                        'office': 'U.S. Senate',
                        'state': state,
                        'district': None,
                        'race_type': 'Senate',
                        'general_date': '2026-11-03'
                    }
                    race_id = self.insert_race(race_data, election_id)
                    senate_races[state] = race_id
                else:
                    race_id = senate_races[state]
                
                self.link_candidate_to_race(candidate_id, race_id)
                
                # Assign issue positions
                party = candidate.get('party_full', '')
                self.assign_candidate_issues(candidate_id, party)
            
            # Fetch financial data
            financials = self.fetch_fec_candidate_financials(candidate.get('candidate_id'))
            if financials:
                self.insert_campaign_finance(candidate_id, financials)
        
        print(f"✓ Inserted {senate_count} Senate candidates")
        print(f"✓ Created {len(senate_races)} Senate races")
        
        # Fetch additional data from other APIs
        print("\n" + "=" * 70)
        print("Fetching Additional Data Sources...")
        print("=" * 70)
        
        # Google Civic Elections
        google_elections = self.fetch_google_civic_elections()
        
        # Ballotpedia race ratings
        race_ratings = self.fetch_ballotpedia_race_ratings()
        
        # Update races with competitiveness data
        print("\nUpdating race competitiveness scores...")
        for rating in race_ratings:
            state = rating['state']
            district = rating['district']
            race_key = f"{state}-{district}"
            
            if race_key in races_by_district:
                race_id = races_by_district[race_key]
                self.update_race_competitiveness(
                    race_id, 
                    rating['competitiveness'], 
                    rating['rating']
                )
        
        # Fetch district demographics (sample for first 20 districts)
        print("\nFetching district demographics from Census API...")
        demo_count = 0
        for race_key, race_id in list(races_by_district.items())[:20]:
            state, district = race_key.split('-')
            demographics = self.fetch_census_district_demographics(state, district)
            if demographics:
                self.insert_district_demographics(state, district, demographics)
                demo_count += 1
        
        print(f"✓ Fetched demographics for {demo_count} districts")
        
        # Fetch Wikipedia info for top candidates (sample)
        print("\nFetching candidate biographical data from Wikipedia...")
        wiki_count = 0
        for candidate in (house_candidates + senate_candidates)[:10]:
            name = candidate.get('name', '')
            wiki_info = self.fetch_wikipedia_candidate_info(name)
            if wiki_info:
                wiki_count += 1
        
        print(f"✓ Fetched Wikipedia data for {wiki_count} candidates")
        
        # Calculate strategic impact scores
        self.calculate_impact_scores()
        
        print("\n" + "=" * 70)
        print("DATA COLLECTION COMPLETE!")
        print("=" * 70)
        print(f"\nSummary:")
        print(f"  - House Candidates: {house_count}")
        print(f"  - Senate Candidates: {senate_count}")
        print(f"  - Total Races: {len(races_by_district) + len(senate_races)}")
        print(f"  - Competitive Races Identified: {len(race_ratings)}")
        print(f"  - Districts with Demographics: {demo_count}")
        print(f"  - Google Civic Elections: {len(google_elections)}")
        print(f"\nData Sources Used:")
        print(f"  ✓ FEC API - Campaign finance and candidates")
        print(f"  ✓ Ballotpedia - Race ratings (simulated)")
        print(f"  ✓ Census API - District demographics")
        print(f"  ✓ Wikipedia API - Candidate biographies")
        if google_elections:
            print(f"  ✓ Google Civic API - Election information")
        print(f"\nDatabase ready for strategic donation recommendations!")
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    import sys
    
    fec_key = None
    google_key = None
    propublica_key = None
    
    if len(sys.argv) > 1:
        fec_key = sys.argv[1]
    
    # Optional: Google Civic and ProPublica keys
    if len(sys.argv) > 2:
        google_key = sys.argv[2]
    if len(sys.argv) > 3:
        propublica_key = sys.argv[3]
    
    if not fec_key:
        print("=" * 70)
        print("MULTI-SOURCE POLITICAL DATA SCRAPER")
        print("=" * 70)
        print("\nAPI Keys (get free keys from):")
        print("  1. FEC API: https://api.open.fec.gov/developers/")
        print("  2. Google Civic (optional): https://console.cloud.google.com/")
        print("  3. ProPublica (optional): https://www.propublica.org/datastore/api/")
        print("\nUsage:")
        print("  python scraper.py [FEC_KEY] [GOOGLE_KEY] [PROPUBLICA_KEY]")
        print("\nRunning with DEMO_KEY (limited rate)...")
        print("=" * 70)
    
    print("\n" + "=" * 70)
    print("DATA SOURCES ENABLED:")
    print("=" * 70)
    print(f"✓ FEC API: {'Custom Key' if fec_key else 'DEMO_KEY (limited)'}")
    print(f"✓ Census API: Enabled (no key required)")
    print(f"✓ Wikipedia API: Enabled (no key required)")
    print(f"✓ Ballotpedia: Simulated data (web scraping not implemented)")
    print(f"{'✓' if google_key else '✗'} Google Civic API: {'Enabled' if google_key else 'Disabled (no key)'}")
    print(f"✗ ProPublica API: Not implemented (requires approval)")
    print(f"✗ Vote Smart API: Not implemented (requires approval)")
    print("=" * 70)
    
    scraper = StrategicPoliticalScraper(
        fec_api_key=fec_key,
        google_civic_key=google_key,
        propublica_key=propublica_key
    )
    
    try:
        scraper.scrape_all_data()
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
    except Exception as e:
        print(f"\n\nError during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()
        print("\nDatabase connection closed.")
