import os
import httpx
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]


async def send_slack_alert(severity: str, diff: dict, report_url: str):
    if severity == "pass":
        return  # nothing worth interrupting the team for

    emoji = "🟠" if severity == "warning" else "🔴"
    text = (
        f"{emoji} *Eval {severity.upper()}* — "
        f"pass rate {diff['previous_pass_rate']:.1%} → {diff['current_pass_rate']:.1%} "
        f"({len(diff['regressions'])} regressions, {len(diff['improvements'])} improvements)\n"
        f"<{report_url}|View full diff report>"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(SLACK_WEBHOOK_URL, json={"text": text})
        response.raise_for_status()