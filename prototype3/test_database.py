"""
Testing script for strategic political donation database.
Validates data and provides PRD-aligned analytics.
"""

import sqlite3
from datetime import datetime
from typing import Dict, List
import json


class DonationPlatformTester:
    """Test and validate strategic donation platform database."""
    
    def __init__(self, db_path: str = "political_donations.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print("\n" + "=" * 70)
        print(f" {title}")
        print("=" * 70)
    
    def test_database_structure(self) -> bool:
        """Test if all required tables exist."""
        self.print_section("DATABASE STRUCTURE TEST")
        
        required_tables = [
            'elections', 'races', 'candidates', 'issues', 'candidate_issues',
            'race_candidates', 'campaign_finance', 'polling_data',
            'district_demographics', 'impact_scores', 'data_sources'
        ]
        
        all_exist = True
        
        for table in required_tables:
            self.cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table,))
            
            exists = self.cursor.fetchone()
            
            if exists:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"✓ Table '{table}' exists with {count} records")
            else:
                print(f"✗ Table '{table}' is missing")
                all_exist = False
        
        return all_exist
    
    def get_statistics(self) -> Dict:
        """Get comprehensive database statistics."""
        self.print_section("DATABASE STATISTICS")
        
        stats = {}
        
        # Basic counts
        self.cursor.execute("SELECT COUNT(*) FROM elections")
        stats['elections'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM races")
        stats['races'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM candidates")
        stats['candidates'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM campaign_finance")
        stats['finance_records'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM issues")
        stats['issues'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM impact_scores")
        stats['impact_scores'] = self.cursor.fetchone()[0]
        
        # Candidates by party
        self.cursor.execute("""
            SELECT party, COUNT(*) as count 
            FROM candidates 
            WHERE party IS NOT NULL AND party != ''
            GROUP BY party 
            ORDER BY count DESC
        """)
        stats['candidates_by_party'] = dict(self.cursor.fetchall())
        
        # Races by type
        self.cursor.execute("""
            SELECT race_type, COUNT(*) as count 
            FROM races 
            GROUP BY race_type
        """)
        stats['races_by_type'] = dict(self.cursor.fetchall())
        
        print(f"\nOverall Statistics:")
        print(f"  Elections: {stats['elections']}")
        print(f"  Races: {stats['races']}")
        print(f"  Candidates: {stats['candidates']}")
        print(f"  Finance Records: {stats['finance_records']}")
        print(f"  Political Issues: {stats['issues']}")
        print(f"  Impact Scores: {stats['impact_scores']}")
        
        if stats['races_by_type']:
            print(f"\nRaces by Type:")
            for race_type, count in stats['races_by_type'].items():
                print(f"  {race_type}: {count}")
        
        if stats['candidates_by_party']:
            print(f"\nCandidates by Party:")
            for party, count in list(stats['candidates_by_party'].items())[:5]:
                print(f"  {party}: {count}")
        
        return stats
    
    def show_high_impact_candidates(self, limit: int = 10):
        """Show top strategic donation opportunities (PRD use case)."""
        self.print_section(f"TOP {limit} HIGH-IMPACT DONATION OPPORTUNITIES")
        print("(Aligned with PRD: Strategic donation recommendations)")
        
        self.cursor.execute("""
            SELECT 
                c.name,
                c.party,
                c.state,
                c.district,
                r.office,
                cf.total_receipts,
                cf.opponent_total_receipts,
                cf.funding_gap,
                cf.donation_leverage_score,
                ims.overall_impact_score,
                ims.recommendation_tier
            FROM impact_scores ims
            JOIN candidates c ON ims.candidate_id = c.id
            JOIN races r ON ims.race_id = r.id
            LEFT JOIN campaign_finance cf ON c.id = cf.candidate_id
            WHERE ims.overall_impact_score IS NOT NULL
            ORDER BY ims.overall_impact_score DESC
            LIMIT ?
        """, (limit,))
        
        candidates = self.cursor.fetchall()
        
        if not candidates:
            print("No impact scores calculated yet. Run scraper first.")
            return
        
        for i, cand in enumerate(candidates, 1):
            location = f"{cand['state']}"
            if cand['district']:
                location += f"-{cand['district']}"
            
            print(f"\n{i}. {cand['name']} ({cand['party']})")
            print(f"   Office: {cand['office']} ({location})")
            print(f"   Impact Score: {cand['overall_impact_score']:.1f}/100")
            print(f"   Tier: {cand['recommendation_tier']}")
            
            if cand['total_receipts']:
                print(f"   Fundraising: ${cand['total_receipts']:,.0f}")
                if cand['opponent_total_receipts']:
                    print(f"   Opponent: ${cand['opponent_total_receipts']:,.0f}")
                    print(f"   Funding Gap: ${cand['funding_gap']:,.0f}")
                if cand['donation_leverage_score']:
                    print(f"   Donation Leverage: {cand['donation_leverage_score']:.1f}/100")
    
    def show_candidates_by_issue(self, issue_name: str, limit: int = 10):
        """Show candidates supporting a specific issue (PRD use case)."""
        self.print_section(f"CANDIDATES SUPPORTING: {issue_name.upper()}")
        print("(Aligned with PRD: Issue-based filtering)")
        
        self.cursor.execute("""
            SELECT 
                c.name,
                c.party,
                c.state,
                c.district,
                c.office,
                ci.position,
                ci.strength,
                ims.overall_impact_score
            FROM candidate_issues ci
            JOIN candidates c ON ci.candidate_id = c.id
            JOIN issues i ON ci.issue_id = i.id
            LEFT JOIN impact_scores ims ON c.id = ims.candidate_id
            WHERE i.name = ?
            ORDER BY ims.overall_impact_score DESC
            LIMIT ?
        """, (issue_name, limit))
        
        candidates = self.cursor.fetchall()
        
        if not candidates:
            print(f"No candidates found supporting '{issue_name}'")
            return
        
        for i, cand in enumerate(candidates, 1):
            location = f"{cand['state']}"
            if cand['district']:
                location += f"-{cand['district']}"
            
            print(f"\n{i}. {cand['name']} ({cand['party']})")
            print(f"   Location: {location}")
            print(f"   Office: {cand['office']}")
            print(f"   Position: {cand['strength']} {cand['position']}")
            if cand['overall_impact_score']:
                print(f"   Impact Score: {cand['overall_impact_score']:.1f}/100")
    
    def show_underfunded_competitive_races(self, limit: int = 10):
        """Show underfunded but competitive races (PRD use case)."""
        self.print_section(f"TOP {limit} UNDERFUNDED COMPETITIVE RACES")
        print("(Aligned with PRD: High leverage donation opportunities)")
        
        self.cursor.execute("""
            SELECT 
                c.name,
                c.party,
                c.state,
                c.district,
                r.office,
                cf.total_receipts,
                cf.opponent_total_receipts,
                cf.funding_ratio,
                cf.donation_leverage_score
            FROM campaign_finance cf
            JOIN candidates c ON cf.candidate_id = c.id
            JOIN race_candidates rc ON c.id = rc.candidate_id
            JOIN races r ON rc.race_id = r.id
            WHERE cf.funding_ratio < 1.0
            AND cf.donation_leverage_score > 60
            ORDER BY cf.donation_leverage_score DESC
            LIMIT ?
        """, (limit,))
        
        races = self.cursor.fetchall()
        
        if not races:
            print("No underfunded competitive races found")
            return
        
        for i, race in enumerate(races, 1):
            location = f"{race['state']}"
            if race['district']:
                location += f"-{race['district']}"
            
            print(f"\n{i}. {race['name']} ({race['party']})")
            print(f"   Office: {race['office']} ({location})")
            print(f"   Raised: ${race['total_receipts']:,.0f}")
            print(f"   Opponent: ${race['opponent_total_receipts']:,.0f}")
            print(f"   Funding Ratio: {race['funding_ratio']:.2f}x")
            print(f"   Leverage Score: {race['donation_leverage_score']:.1f}/100")
            print(f"   → Your donation has {race['donation_leverage_score']:.0f}% impact potential")
    
    def show_grassroots_candidates(self, limit: int = 10):
        """Show candidates with strong grassroots support (PRD use case)."""
        self.print_section(f"TOP {limit} GRASSROOTS-FUNDED CANDIDATES")
        print("(Aligned with PRD: Small-dollar donation success stories)")
        
        self.cursor.execute("""
            SELECT 
                c.name,
                c.party,
                c.state,
                c.district,
                r.office,
                cf.total_receipts,
                cf.individual_contributions,
                cf.small_dollar_percentage
            FROM campaign_finance cf
            JOIN candidates c ON cf.candidate_id = c.id
            JOIN race_candidates rc ON c.id = rc.candidate_id
            JOIN races r ON rc.race_id = r.id
            WHERE cf.small_dollar_percentage > 40
            ORDER BY cf.small_dollar_percentage DESC
            LIMIT ?
        """, (limit,))
        
        candidates = self.cursor.fetchall()
        
        if not candidates:
            print("No grassroots candidates found")
            return
        
        for i, cand in enumerate(candidates, 1):
            location = f"{cand['state']}"
            if cand['district']:
                location += f"-{cand['district']}"
            
            print(f"\n{i}. {cand['name']} ({cand['party']})")
            print(f"   Office: {cand['office']} ({location})")
            print(f"   Total Raised: ${cand['total_receipts']:,.0f}")
            print(f"   Individual Contributions: ${cand['individual_contributions']:,.0f}")
            print(f"   Small-Dollar %: {cand['small_dollar_percentage']:.1f}%")
    
    def show_available_issues(self):
        """Show all political issues in database."""
        self.print_section("AVAILABLE POLITICAL ISSUES")
        
        self.cursor.execute("""
            SELECT i.name, i.category, COUNT(ci.candidate_id) as candidate_count
            FROM issues i
            LEFT JOIN candidate_issues ci ON i.id = ci.issue_id
            GROUP BY i.id
            ORDER BY i.category, i.name
        """)
        
        issues = self.cursor.fetchall()
        
        current_category = None
        for issue in issues:
            if issue['category'] != current_category:
                current_category = issue['category']
                print(f"\n{current_category}:")
            print(f"  • {issue['name']} ({issue['candidate_count']} candidates)")
    
    def export_recommendations_json(self, output_file: str = "donation_recommendations.json"):
        """Export top recommendations to JSON."""
        self.print_section("EXPORTING RECOMMENDATIONS")
        
        # Get top 20 recommendations
        self.cursor.execute("""
            SELECT 
                c.name,
                c.party,
                c.state,
                c.district,
                r.office,
                cf.total_receipts,
                cf.opponent_total_receipts,
                cf.funding_gap,
                cf.donation_leverage_score,
                ims.overall_impact_score,
                ims.recommendation_tier
            FROM impact_scores ims
            JOIN candidates c ON ims.candidate_id = c.id
            JOIN races r ON ims.race_id = r.id
            LEFT JOIN campaign_finance cf ON c.id = cf.candidate_id
            WHERE ims.overall_impact_score IS NOT NULL
            ORDER BY ims.overall_impact_score DESC
            LIMIT 20
        """)
        
        recommendations = [dict(row) for row in self.cursor.fetchall()]
        
        output = {
            'generated_at': datetime.now().isoformat(),
            'platform': 'Strategic Political Donation Platform',
            'description': 'GiveWell for Politics - High-impact donation opportunities',
            'recommendations': recommendations
        }
        
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"✓ Exported {len(recommendations)} recommendations to: {output_file}")
    
    def run_all_tests(self):
        """Run all tests and display PRD-aligned analytics."""
        print("\n" + "=" * 70)
        print(" STRATEGIC POLITICAL DONATION PLATFORM - TEST SUITE")
        print("=" * 70)
        print(" PRD: 'GiveWell for Politics'")
        print(f" Database: {self.db_path}")
        print(f" Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Run tests
        structure_ok = self.test_database_structure()
        stats = self.get_statistics()
        
        if stats['candidates'] == 0:
            print("\n⚠ Database is empty. Run scraper.py to populate it.")
            return
        
        # Show PRD-aligned analytics
        self.show_high_impact_candidates(10)
        self.show_underfunded_competitive_races(10)
        self.show_grassroots_candidates(10)
        
        # Show issue-based filtering
        self.show_available_issues()
        
        # Example: Show candidates for specific issues
        example_issues = ["Climate Change", "Healthcare Access", "Economic Justice"]
        for issue in example_issues:
            self.cursor.execute("SELECT COUNT(*) FROM issues WHERE name = ?", (issue,))
            if self.cursor.fetchone()[0] > 0:
                self.show_candidates_by_issue(issue, 5)
        
        # Export recommendations
        self.export_recommendations_json()
        
        # Final summary
        self.print_section("TEST SUMMARY")
        
        print(f"\nDatabase Structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
        print(f"Total Candidates: {stats['candidates']}")
        print(f"Total Races: {stats['races']}")
        print(f"Impact Scores Calculated: {stats['impact_scores']}")
        
        if stats['impact_scores'] > 0:
            print("\n✓ Platform ready for strategic donation recommendations!")
            print("\nNext steps:")
            print("  1. Review donation_recommendations.json for top opportunities")
            print("  2. Filter by issues using candidate_issues table")
            print("  3. Integrate with donation processing system")
        
        print("\n" + "=" * 70)
    
    def close(self):
        """Close database connection."""
        self.conn.close()


if __name__ == "__main__":
    tester = DonationPlatformTester()
    
    try:
        tester.run_all_tests()
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.close()
