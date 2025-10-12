import httpx
import json
from typing import Awaitable, Optional, Callable, Any
from pydantic import SecretStr


class Aeon:
    api_key: SecretStr
    project_id: int
    agent: str
    endpoint: Optional[str] = "https://withaeon.com"
    initialized: bool = False

    @staticmethod
    def init(
        agent: str,
        api_key: str,
        project_id: int,
        endpoint: Optional[str] = "https://withaeon.com",
    ):
        if Aeon.initialized:
            raise RuntimeError("Aeon has already been initialized")

        Aeon.initialized = True
        Aeon.api_key = SecretStr(api_key)
        Aeon.agent = agent
        Aeon.endpoint = endpoint
        Aeon.project_id = project_id

        print("Aeon initialized with endpoint: ", Aeon.endpoint)

    @staticmethod
    async def track_session(costs: float, model: str):
        """
        Send session data to API
        """

        print("Sending session")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/sessions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"{Aeon.api_key.get_secret_value()}",
                    },
                    json={
                        "agent_name": Aeon.agent,
                        "model": model,
                        "costs": costs,
                    },
                )

                print(response)

        except Exception as e:
            print("Error: ", e)

    # Orchestration
    @staticmethod
    async def send_task(task: dict):
        """
        Send a task to an agent

        Parameters:
            task (dict): Information of the task recipient and the event to be send
                Expected keys:
                - 'from' (str, optional): Agent that send the event (handled internally).
                - 'to' (str): Which agent to send the message.
                - 'event' (str): What should the agent do.
        """

        if "from" not in task:
            task["from"] = Aeon.agent

        try:
            # Create the trigger on the database and retrieve the id
            id = await Aeon.track_trigger(
                from_=task["from"], to=task["to"], event=task["event"]
            )

            # Assign the id retrieved from backend
            task["id"] = id

            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/send",
                    headers={
                        "Authorization": Aeon.api_key.get_secret_value(),
                        "Content-Type": "application/json",
                    },
                    json=task,
                    timeout=30.0,
                )

                print(f"Task sent: {task}")
        except Exception as e:
            print("Error: ", e)

    @staticmethod
    async def listen(callback: Callable[[str], Awaitable[None]]):
        """
        Listen to the server for tasks to execute

        Parameters:
            callback (Callable[[str], Awaitable[None]]): Asynchronous function to call when the agent receives a task.
                Receives the event as a string argument.
        """

        # Store the trigger_id to send failed status in case something goes wrong
        trigger_id = None

        url = f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/listen?agent={Aeon.agent}"

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "GET",
                    url,
                    headers={"Authorization": Aeon.api_key.get_secret_value()},
                ) as response:

                    if response.status_code != 200:
                        raise Exception(f"Failed to connect: {response.status_code}")

                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue

                        # Process SSE format
                        if line.startswith("data: "):
                            data_str = line[6:]

                            try:
                                task = json.loads(data_str)
                                event = task.get("event")
                                trigger_id = task.get("id")

                                if not event:
                                    continue

                                print(f"Executing task: {task}")

                                try:
                                    await callback(event)

                                    print("Sending received status...")

                                    async with httpx.AsyncClient() as client:
                                        response = await client.patch(
                                            f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/triggers/{trigger_id}",
                                            headers={
                                                "Content-Type": "application/json",
                                                "Authorization": Aeon.api_key.get_secret_value(),
                                            },
                                            json={"status": "received"},
                                        )
                                        print(response)

                                except Exception as e:
                                    print(f"Error: {e}")
                                    print("Sending failed status...")

                                    # If something failes, update the status to 'failed'
                                    async with httpx.AsyncClient() as client:
                                        response = await client.patch(
                                            f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/triggers/{trigger_id}",
                                            headers={
                                                "Content-Type": "application/json",
                                                "Authorization": Aeon.api_key.get_secret_value(),
                                            },
                                            json={"status": "failed"},
                                        )
                                        print(response)

                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            print(f"Connection error: {e}")
            raise

    @staticmethod
    async def track_trigger(
        from_: str,
        to: str,
        event: str,
    ):
        """
        Track agent trigger

        Parameters:
            from_ (str): Which agent sent the event.
            to (str): The recipient agent name.
            event (str): The event sent to the agent.
        """

        try:
            async with httpx.AsyncClient() as client:
                print(f"Tracing trigger '{event}' to {to}")
                response = await client.post(
                    f"{Aeon.endpoint}/api/v1/projects/{Aeon.project_id}/agents/triggers",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"{Aeon.api_key.get_secret_value()}",
                    },
                    json={
                        "from": from_,
                        "to": to,
                        "event": event,
                    },
                )

                data = response.json()

                print(data)

                return data["id"]

        except Exception as e:
            print("Error: ", e)
