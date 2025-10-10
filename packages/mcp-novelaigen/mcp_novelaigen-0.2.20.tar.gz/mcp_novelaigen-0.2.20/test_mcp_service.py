import pytest
import httpx
import asyncio
import uuid

# The address of the running MCP server
MCP_SERVER_URL = "http://142.171.230.23:45678/mcp"

@pytest.mark.asyncio
async def test_mcp_service_connection():
    """
    Tests basic connection to the MCP service and verifies it's streaming.
    """
    # It's better to use a longer timeout for network tests
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Sending a POST request with a more realistic payload.
            payload = {
                "model": "test-model",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": True
            }
            headers = {
                "Authorization": f"Bearer {uuid.uuid4()}"
            }
            async with client.stream("POST", MCP_SERVER_URL, json=payload, headers=headers) as response:
                # Handle potential errors first
                if response.status_code != 200:
                    # Read the response body to include in the error message
                    await response.aread()
                    pytest.fail(
                        f"MCP server returned an error status: {response.status_code} - {response.text}"
                    )

                # If status is OK, proceed to check the stream
                data_received = False
                try:
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            print(f"Received chunk: {chunk}")
                            data_received = True
                            break  # Exit after the first chunk
                except httpx.StreamError as e:
                    pytest.fail(f"An error occurred while streaming: {e}")

                assert data_received, "Stream was opened, but no data was received."

        except httpx.ConnectError as e:
            pytest.fail(f"Connection to MCP server at {MCP_SERVER_URL} failed: {e}")
        except httpx.ReadTimeout as e:
            pytest.fail(f"Reading from MCP server at {MCP_SERVER_URL} timed out: {e}")
