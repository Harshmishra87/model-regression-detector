import asyncio
from src.alert import send_slack_alert

async def main():
    fake_diff = {
        "previous_pass_rate": 0.94,
        "current_pass_rate": 0.89,
        "regressions": ["case_020", "case_096", "case_014"],
        "improvements": [],
    }
    await send_slack_alert(severity="warning", diff=fake_diff, report_url="https://example.com/report.html")
    print("Alert sent.")

asyncio.run(main())