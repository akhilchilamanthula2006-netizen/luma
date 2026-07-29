"""
Debug: Render the analytics template with real user data and extract
the embedded JSON + Chart.js dataset values.
"""
import sys
sys.path.insert(0, '.')

from app import app
from services.wellness.statistics_service import StatisticsService
from services.wellness.insights_service import InsightsService
from services.wellness_service import WellnessService
import json

uid = '6a65cceed01519146b678962'  # akhil - known to have data

with app.test_request_context('/analytics'):
    summary_data = WellnessService.get_dashboard_summary(uid)
    analytics = StatisticsService.get_7day_analytics(uid)
    ai_summary = InsightsService.generate_weekly_ai_summary(uid)
    timeline = StatisticsService.get_unified_timeline(uid, limit=15)

    print("=== BACKEND analytics dict keys ===")
    for k, v in analytics.items():
        print(f"  {k}: {v}")

    print("\n=== BACKEND ai_summary dict keys ===")
    for k, v in ai_summary.items():
        if isinstance(v, list):
            print(f"  {k}: {v[:2]} ...")
        else:
            print(f"  {k}: {v}")

    print("\n=== BACKEND timeline ===")
    print(f"  timeline count: {len(timeline)}")
    if timeline:
        print(f"  First item keys: {list(timeline[0].keys())}")
        print(f"  First item: {timeline[0]}")

    from flask import render_template
    html = render_template(
        'analytics/index.html',
        username='akhil',
        summary=summary_data,
        analytics=analytics,
        ai_summary=ai_summary,
        timeline=timeline
    )

    print("\n=== RENDERED HTML CHECKS ===")
    print("HTML length:", len(html))
    print("Empty state banner present:", 'Your Wellness Journey Starts Here' in html)

    # Find and print the analytics-data JSON block
    start = html.find('<script id="analytics-data"')
    end = html.find('</script>', start) + len('</script>')
    block = html[start:end]
    print("\n=== analytics-data script block ===")
    print(block[:800])

    # Parse the JSON and check values
    json_start = block.find('>') + 1
    json_end = block.rfind('</')
    raw_json = block[json_start:json_end].strip()
    try:
        parsed = json.loads(raw_json)
        print("\n=== PARSED JSON from embedded block ===")
        for k, v in parsed.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"\nJSON PARSE ERROR: {e}")
        print("Raw JSON snippet:", raw_json[:200])

    # Check Chart.js inline data checks
    print("\n=== KEY CHECKS IN HTML (Chart.js truthy checks) ===")
    checks = [
        'analyticsData.wellness_scores',
        'analyticsData.sleep_hours',
        'analyticsData.breathing_mins',
        'analyticsData.meditation_mins',
        'analyticsData.mood_counts',
        'analyticsData.activity_distribution',
        'analyticsData.day_labels',
    ]
    for c in checks:
        present = c in html
        print(f"  {c} referenced in JS: {present}")

    # Check overlay divs (white overlays blocking charts)
    print("\n=== OVERLAY CHECKS (white chart blocking overlays) ===")
    import re
    overlays = re.findall(r'absolute inset-0.*?No data available yet', html, re.DOTALL)
    print(f"  Number of white overlay divs rendered: {len(overlays)}")

    # Check timeline rendered items
    timeline_count_in_html = html.count('item.event_type')
    print(f"\n  Timeline item.event_type references: {timeline_count_in_html}")
    print("  'No activity recorded in timeline yet' shown:", 'No activity recorded in timeline yet' in html)
