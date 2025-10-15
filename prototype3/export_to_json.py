"""
Export SQLite database to JSON for web interface.
"""

import sqlite3
import json
from pathlib import Path


def export_database_to_json(db_path: str = "political_donations.db", output_dir: str = "web-interface/public"):
    """Export database tables to JSON files."""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print("Exporting database to JSON...")
    
    # Export candidates with all related data
    cursor.execute("""
        SELECT 
            c.id,
            c.name,
            c.party,
            c.office,
            c.state,
            c.district,
            c.incumbent,
            c.election_year,
            cf.total_receipts,
            cf.total_disbursements,
            cf.cash_on_hand,
            cf.individual_contributions,
            cf.opponent_total_receipts,
            cf.funding_gap,
            cf.donation_leverage_score,
            cf.small_dollar_percentage,
            ims.overall_impact_score,
            ims.competitiveness_score,
            ims.funding_leverage_score,
            ims.recommendation_tier
        FROM candidates c
        LEFT JOIN campaign_finance cf ON c.id = cf.candidate_id
        LEFT JOIN impact_scores ims ON c.id = ims.candidate_id
        ORDER BY ims.overall_impact_score DESC
    """)
    
    candidates = [dict(row) for row in cursor.fetchall()]
    
    with open(f"{output_dir}/candidates.json", 'w') as f:
        json.dump(candidates, f, indent=2, default=str)
    
    print(f"✓ Exported {len(candidates)} candidates")
    
    # Export races
    cursor.execute("""
        SELECT 
            r.id,
            r.office,
            r.race_type,
            r.state,
            r.district,
            r.general_date,
            r.competitiveness_score,
            r.cook_rating,
            r.is_swing_district,
            COUNT(rc.candidate_id) as candidate_count
        FROM races r
        LEFT JOIN race_candidates rc ON r.id = rc.race_id
        GROUP BY r.id
        ORDER BY r.state, r.district
    """)
    
    races = [dict(row) for row in cursor.fetchall()]
    
    with open(f"{output_dir}/races.json", 'w') as f:
        json.dump(races, f, indent=2, default=str)
    
    print(f"✓ Exported {len(races)} races")
    
    # Export issues
    cursor.execute("""
        SELECT 
            i.id,
            i.name,
            i.category,
            i.description,
            COUNT(ci.candidate_id) as candidate_count
        FROM issues i
        LEFT JOIN candidate_issues ci ON i.id = ci.issue_id
        GROUP BY i.id
        ORDER BY i.category, i.name
    """)
    
    issues = [dict(row) for row in cursor.fetchall()]
    
    with open(f"{output_dir}/issues.json", 'w') as f:
        json.dump(issues, f, indent=2, default=str)
    
    print(f"✓ Exported {len(issues)} issues")
    
    # Export candidate-issue relationships
    cursor.execute("""
        SELECT 
            ci.candidate_id,
            ci.issue_id,
            i.name as issue_name,
            ci.position,
            ci.strength,
            ci.priority
        FROM candidate_issues ci
        JOIN issues i ON ci.issue_id = i.id
        ORDER BY ci.candidate_id, ci.priority
    """)
    
    candidate_issues = [dict(row) for row in cursor.fetchall()]
    
    with open(f"{output_dir}/candidate-issues.json", 'w') as f:
        json.dump(candidate_issues, f, indent=2, default=str)
    
    print(f"✓ Exported {len(candidate_issues)} candidate-issue relationships")
    
    # Export district demographics
    cursor.execute("""
        SELECT 
            state,
            district,
            population,
            median_income,
            college_educated_percentage
        FROM district_demographics
        ORDER BY state, district
    """)
    
    demographics = [dict(row) for row in cursor.fetchall()]
    
    with open(f"{output_dir}/demographics.json", 'w') as f:
        json.dump(demographics, f, indent=2, default=str)
    
    print(f"✓ Exported {len(demographics)} district demographics")
    
    # Export summary statistics
    stats = {
        'total_candidates': len(candidates),
        'total_races': len(races),
        'total_issues': len(issues),
        'high_impact_candidates': len([c for c in candidates if c.get('overall_impact_score', 0) and c['overall_impact_score'] >= 75]),
        'competitive_races': len([r for r in races if r.get('competitiveness_score', 0) and r['competitiveness_score'] >= 45]),
        'last_updated': str(cursor.execute("SELECT datetime('now')").fetchone()[0])
    }
    
    with open(f"{output_dir}/stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"✓ Exported summary statistics")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("Export complete!")
    print("=" * 60)
    print(f"Files created in: {output_dir}/")
    print(f"  - candidates.json ({len(candidates)} records)")
    print(f"  - races.json ({len(races)} records)")
    print(f"  - issues.json ({len(issues)} records)")
    print(f"  - candidate-issues.json ({len(candidate_issues)} records)")
    print(f"  - demographics.json ({len(demographics)} records)")
    print(f"  - stats.json")


if __name__ == "__main__":
    export_database_to_json()
