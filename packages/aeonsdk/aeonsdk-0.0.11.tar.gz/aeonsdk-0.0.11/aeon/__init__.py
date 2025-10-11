import httpx
import asyncio


class Aeon:
    total_costs: float = 0
    model_name: str = "unknown"
    api_key: str
    agent: str
    endpoint: str

    @staticmethod
    def init(agent: str, api_key: str, endpoint: str = "https://withaeon.com"):
        Aeon.api_key = api_key
        Aeon.agent = agent
        Aeon.endpoint = endpoint
        print("Aeon initialized with endpoint ", Aeon.endpoint)

    @staticmethod
    async def _track_costs(costs=None):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{Aeon.endpoint}/api/v1/agents/costs",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"{Aeon.api_key}",
                    },
                    json={
                        "agent_name": Aeon.agent,
                        "model": Aeon.model_name,
                        "cost": costs if costs is not None else Aeon.total_costs,
                    },
                )

        except Exception as e:
            print("Error: ", e)

    @staticmethod
    async def trace(to: str, event: str, costs=None):
        print(f"Tracing event '{event}' to {to}")

        try:

            async with httpx.AsyncClient() as client:
                track_task = Aeon._track_costs(
                    costs=costs if costs is not None else None
                )

                post_task = client.post(
                    f"{Aeon.endpoint}/api/v1/agents/triggers",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"{Aeon.api_key}",
                    },
                    json={
                        "from": Aeon.agent,
                        "to": to,
                        "event": event,
                    },
                )

                await asyncio.gather(track_task, post_task)

        except Exception as e:
            print("Error: ", e)
