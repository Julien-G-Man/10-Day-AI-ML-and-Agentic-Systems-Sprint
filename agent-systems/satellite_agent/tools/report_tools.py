from langchain.tools import tool
from datetime import datetime

@tool
def compile_satellite_report(
    satellite_name: str,
    technical_summary: str,
    news_summary: str,
    key_insights: str,
) -> str:
    """
    Compile all gathered information into a formatted satellite intelligence report.
    Call this LAST, after you have gathered technical data AND news.
    Provide summaries of both the technical data and news findings.
    """
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    return f'''
╔══════════════════════════════════════════════════════════╗
║         SATELLITE INTELLIGENCE REPORT                    ║
╚══════════════════════════════════════════════════════════╝
Satellite:  {satellite_name}
Generated:  {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━
TECHNICAL OVERVIEW
{technical_summary}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━
RECENT NEWS & EVENTS
{news_summary}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━
KEY INSIGHTS & ANALYSIS
{key_insights}
══════════════════════════════════════════════════════════
'''
