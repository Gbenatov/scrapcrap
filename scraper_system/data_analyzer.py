"""
Data Analyzer - ניתוח תיקים מתקדם
"""

import json
from typing import List, Dict, Any
import statistics


class DataAnalyzer:
    """מחלקה לניתוח נתוני תיקים"""
    
    def __init__(self, cases: List[Dict[str, Any]]):
        """
        אתחול
        
        Args:
            cases: רשימת התיקים
        """
        self.cases = cases
    
    def get_statistics(self) -> Dict[str, Any]:
        """קבלת סטטיסטיקות בסיסיות"""
        claim_amounts = [c.get('סכום_תביעה', 0) for c in self.cases]
        claim_amounts = [a for a in claim_amounts if a > 0]
        
        stats = {
            'סה"כ_תיקים': len(self.cases),
            'סכום_ממוצע': statistics.mean(claim_amounts) if claim_amounts else 0,
            'סכום_חציון': statistics.median(claim_amounts) if claim_amounts else 0,
            'סכום_מינימום': min(claim_amounts) if claim_amounts else 0,
            'סכום_מקסימום': max(claim_amounts) if claim_amounts else 0,
            'סה"כ_סכומים': sum(claim_amounts)
        }
        return stats
    
    def get_courts_distribution(self) -> Dict[str, int]:
        """התפלגות לפי בתי משפט"""
        distribution = {}
        for case in self.cases:
            court = case.get('בית_משפט', 'לא מוגדר')
            distribution[court] = distribution.get(court, 0) + 1
        
        return dict(sorted(
            distribution.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def get_plaintiff_groups_distribution(self) -> Dict[str, int]:
        """התפלגות לפי קבוצת תובעים"""
        distribution = {}
        for case in self.cases:
            group = case.get('קבוצה_תובעים', 'לא מוגדר')
            if group and group.strip():
                distribution[group] = distribution.get(group, 0) + 1
        
        return dict(sorted(
            distribution.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    def get_appeal_cases_percentage(self) -> float:
        """אחוז תיקי ערעור"""
        if not self.cases:
            return 0
        
        appeal_cases = sum(1 for c in self.cases if c.get('תיק_ערעור') == '1')
        return (appeal_cases / len(self.cases)) * 100
    
    def get_high_value_cases(self, threshold: float = 10000000) -> List[Dict[str, Any]]:
        """קבלת תיקים בסכום גבוה"""
        return sorted(
            [c for c in self.cases if c.get('סכום_תביעה', 0) >= threshold],
            key=lambda x: x.get('סכום_תביעה', 0),
            reverse=True
        )
    
    def generate_full_report(self) -> Dict[str, Any]:
        """יצירת דוח מלא"""
        report = {
            'סטטיסטיקה_בסיסית': self.get_statistics(),
            'התפלגות_בתי_משפט': self.get_courts_distribution(),
            'התפלגות_קבוצות_תובעים': self.get_plaintiff_groups_distribution(),
            'אחוז_תיקי_ערעור': f"{self.get_appeal_cases_percentage():.2f}%",
            'תיקי_ערך_גבוה': self.get_high_value_cases()[:10]
        }
        return report


# דוגמה לשימוש
if __name__ == "__main__":
    sample_cases = [
        {
            'מספר_תיק': '1',
            'שם_תיק': 'תיק 1',
            'בית_משפט': 'אזורי',
            'סכום_תביעה': 5000000,
            'תיק_ערעור': '0',
            'קבוצה_תובעים': 'עובדים'
        },
        {
            'מספר_תיק': '2',
            'שם_תיק': 'תיק 2',
            'בית_משפט': 'מחוזי',
            'סכום_תביעה': 15000000,
            'תיק_ערעור': '1',
            'קבוצה_תובעים': 'עובדים'
        }
    ]
    
    analyzer = DataAnalyzer(sample_cases)
    report = analyzer.generate_full_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
