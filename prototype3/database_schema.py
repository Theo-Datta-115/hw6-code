"""
Enhanced database schema for political donation platform.
Supports strategic donation recommendations based on competitiveness,
funding gaps, issues, and impact metrics.

Aligned with PRD: "GiveWell for Politics"
"""

import sqlite3
from datetime import datetime
from typing import Optional


class PoliticalDonationDB:
    """Database manager for strategic political donation platform."""
    
    def __init__(self, db_path: str = "political_donations.db"):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create all necessary tables for the donation platform."""
        
        # Elections table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS elections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                election_date DATE NOT NULL,
                election_type VARCHAR(100),
                state VARCHAR(2),
                district VARCHAR(50),
                jurisdiction VARCHAR(200),
                description TEXT,
                registration_deadline DATE,
                early_voting_start DATE,
                early_voting_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(election_date, election_type, state, district)
            )
        """)
        
        # Races table - enhanced with competitiveness metrics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS races (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                election_id INTEGER,
                office VARCHAR(200) NOT NULL,
                race_type VARCHAR(100),
                state VARCHAR(2),
                district VARCHAR(50),
                seat_name VARCHAR(200),
                incumbent_name VARCHAR(200),
                incumbent_party VARCHAR(50),
                number_of_seats INTEGER DEFAULT 1,
                is_special_election BOOLEAN DEFAULT 0,
                is_swing_district BOOLEAN DEFAULT 0,
                
                -- Competitiveness metrics
                competitiveness_score DECIMAL(5, 2),
                margin_of_victory_2022 DECIMAL(5, 2),
                margin_of_victory_2020 DECIMAL(5, 2),
                district_lean VARCHAR(50),
                cook_rating VARCHAR(50),
                
                -- Dates
                filing_deadline DATE,
                primary_date DATE,
                general_date DATE,
                
                -- Strategic importance
                strategic_importance VARCHAR(50),
                control_impact BOOLEAN DEFAULT 0,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (election_id) REFERENCES elections(id),
                UNIQUE(office, state, district, general_date)
            )
        """)
        
        # Candidates table - enhanced with issue positions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fec_candidate_id VARCHAR(50) UNIQUE,
                name VARCHAR(200) NOT NULL,
                party VARCHAR(100),
                office VARCHAR(200),
                state VARCHAR(2),
                district VARCHAR(50),
                incumbent BOOLEAN DEFAULT 0,
                candidate_status VARCHAR(50),
                election_year INTEGER,
                
                -- Contact & web presence
                website_url TEXT,
                email VARCHAR(200),
                phone VARCHAR(50),
                address TEXT,
                twitter_handle VARCHAR(100),
                facebook_url TEXT,
                
                -- Endorsements & credibility
                endorsements TEXT,
                experience TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Issues table - for filtering by policy positions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL UNIQUE,
                category VARCHAR(100),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Candidate_Issues junction table - links candidates to their issue positions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidate_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                issue_id INTEGER NOT NULL,
                position VARCHAR(50),
                strength VARCHAR(50),
                priority INTEGER,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id),
                FOREIGN KEY (issue_id) REFERENCES issues(id),
                UNIQUE(candidate_id, issue_id)
            )
        """)
        
        # Race_Candidates junction table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS race_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id INTEGER NOT NULL,
                candidate_id INTEGER NOT NULL,
                ballot_position INTEGER,
                withdrew BOOLEAN DEFAULT 0,
                withdrawal_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (race_id) REFERENCES races(id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id),
                UNIQUE(race_id, candidate_id)
            )
        """)
        
        # Campaign Finance table - enhanced with leverage metrics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_finance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                fec_committee_id VARCHAR(50),
                committee_name VARCHAR(300),
                
                -- Financial totals
                total_receipts DECIMAL(15, 2),
                total_disbursements DECIMAL(15, 2),
                cash_on_hand DECIMAL(15, 2),
                total_contributions DECIMAL(15, 2),
                
                -- Contribution breakdown
                individual_contributions DECIMAL(15, 2),
                small_dollar_contributions DECIMAL(15, 2),
                pac_contributions DECIMAL(15, 2),
                party_contributions DECIMAL(15, 2),
                candidate_contributions DECIMAL(15, 2),
                
                -- Opponent comparison (for leverage calculation)
                opponent_total_receipts DECIMAL(15, 2),
                funding_gap DECIMAL(15, 2),
                funding_ratio DECIMAL(5, 2),
                
                -- Leverage metrics
                donation_leverage_score DECIMAL(5, 2),
                small_dollar_percentage DECIMAL(5, 2),
                
                reporting_period_start DATE,
                reporting_period_end DATE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)
        
        # Polling Data table - for competitiveness tracking
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS polling_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id INTEGER NOT NULL,
                candidate_id INTEGER,
                poll_date DATE,
                pollster VARCHAR(200),
                sample_size INTEGER,
                margin_of_error DECIMAL(5, 2),
                percentage DECIMAL(5, 2),
                poll_url TEXT,
                quality_rating VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (race_id) REFERENCES races(id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        """)
        
        # District Demographics - for understanding voter base
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS district_demographics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state VARCHAR(2) NOT NULL,
                district VARCHAR(50),
                population INTEGER,
                median_income DECIMAL(10, 2),
                urban_percentage DECIMAL(5, 2),
                college_educated_percentage DECIMAL(5, 2),
                youth_voter_turnout DECIMAL(5, 2),
                swing_score DECIMAL(5, 2),
                partisan_lean VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state, district)
            )
        """)
        
        # Impact Scores - calculated strategic importance
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS impact_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                race_id INTEGER NOT NULL,
                
                -- Component scores (0-100)
                competitiveness_score DECIMAL(5, 2),
                funding_leverage_score DECIMAL(5, 2),
                control_impact_score DECIMAL(5, 2),
                grassroots_potential_score DECIMAL(5, 2),
                
                -- Overall impact score
                overall_impact_score DECIMAL(5, 2),
                
                -- Recommendation tier
                recommendation_tier VARCHAR(50),
                
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id),
                FOREIGN KEY (race_id) REFERENCES races(id),
                UNIQUE(candidate_id, race_id)
            )
        """)
        
        # Data Sources table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name VARCHAR(200) NOT NULL,
                source_url TEXT,
                api_endpoint TEXT,
                last_scraped TIMESTAMP,
                records_added INTEGER DEFAULT 0,
                status VARCHAR(50),
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_elections_date ON elections(election_date)",
            "CREATE INDEX IF NOT EXISTS idx_races_state ON races(state, district)",
            "CREATE INDEX IF NOT EXISTS idx_races_competitive ON races(competitiveness_score)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_fec ON candidates(fec_candidate_id)",
            "CREATE INDEX IF NOT EXISTS idx_candidates_state ON candidates(state, district)",
            "CREATE INDEX IF NOT EXISTS idx_candidate_issues_candidate ON candidate_issues(candidate_id)",
            "CREATE INDEX IF NOT EXISTS idx_candidate_issues_issue ON candidate_issues(issue_id)",
            "CREATE INDEX IF NOT EXISTS idx_finance_leverage ON campaign_finance(donation_leverage_score)",
            "CREATE INDEX IF NOT EXISTS idx_impact_scores_overall ON impact_scores(overall_impact_score)",
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
        
        self.conn.commit()
    
    def seed_issues(self):
        """Seed the database with common political issues."""
        issues = [
            ("Climate Change", "Environment", "Policies related to climate action and environmental protection"),
            ("Healthcare Access", "Healthcare", "Universal healthcare, insurance reform, and medical costs"),
            ("Immigration Reform", "Immigration", "Border policy, pathways to citizenship, and refugee policy"),
            ("Economic Justice", "Economy", "Wealth inequality, minimum wage, and economic opportunity"),
            ("Crime & Safety", "Justice", "Criminal justice reform, policing, and public safety"),
            ("Education", "Education", "Public education funding, student debt, and education access"),
            ("Reproductive Rights", "Healthcare", "Abortion access and reproductive healthcare"),
            ("Gun Control", "Justice", "Gun safety legislation and Second Amendment rights"),
            ("Voting Rights", "Democracy", "Voter access, election security, and gerrymandering"),
            ("Housing Affordability", "Economy", "Affordable housing, rent control, and homelessness"),
            ("Labor Rights", "Economy", "Union rights, worker protections, and fair wages"),
            ("LGBTQ+ Rights", "Civil Rights", "LGBTQ+ protections and equality"),
            ("Racial Justice", "Civil Rights", "Systemic racism, police reform, and equity"),
            ("Foreign Policy", "International", "Military intervention, diplomacy, and international relations"),
            ("Infrastructure", "Economy", "Roads, bridges, broadband, and public works"),
        ]
        
        for name, category, description in issues:
            self.cursor.execute("""
                INSERT OR IGNORE INTO issues (name, category, description)
                VALUES (?, ?, ?)
            """, (name, category, description))
        
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Create database and tables
    db = PoliticalDonationDB()
    print(f"Database created successfully at: {db.db_path}")
    print("Tables created:")
    
    # List all tables
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = db.cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    
    # Seed issues
    print("\nSeeding issues...")
    db.seed_issues()
    
    db.cursor.execute("SELECT COUNT(*) FROM issues")
    issue_count = db.cursor.fetchone()[0]
    print(f"✓ Seeded {issue_count} political issues")
    
    db.close()
