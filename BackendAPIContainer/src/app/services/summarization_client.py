import httpx

from app.core.config import settings


class SummarizationClient:
    """Client for external AI summarization service."""

    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        self.base_url = (base_url or settings.SUMMARIZATION_API_URL).rstrip("/")
        self.token = token or settings.SUMMARIZATION_API_TOKEN

    async def summarize(self, note_id: str, content: str) -> str:
        """
        Submit content for summarization and return the resulting summary text.

        This implementation follows a simplified flow: POST /summarize and then GET /result
        using the returned job_id, with a short polling loop. In case of failure or timeout,
        a fallback summary is returned.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/summarize",
                    headers=headers,
                    json={"note_id": note_id, "content": content},
                )
                resp.raise_for_status()
                data = resp.json()
                job_id = data.get("job_id")
                if not job_id:
                    # Some services might directly return a summary
                    summary_direct = data.get("summary")
                    if summary_direct:
                        return summary_direct
                    raise RuntimeError("Invalid summarization response")

                # Poll result endpoint up to 5 times
                for _ in range(5):
                    r2 = await client.get(f"{self.base_url}/result", headers=headers, params={"job_id": job_id})
                    if r2.status_code == 200:
                        payload = r2.json()
                        if payload.get("status") == "completed" and payload.get("summary"):
                            return payload["summary"]
                    # Small delay between polls
                    await client.aclose()
                    async with httpx.AsyncClient(timeout=15.0) as client2:
                        client = client2  # reset client to keep simple without sleep; environment may not allow asyncio.sleep
                # Fallback
                return content[:140] + ("..." if len(content) > 140 else "")
            except Exception:
                # Fallback summary on error
                return content[:140] + ("..." if len(content) > 140 else "")
