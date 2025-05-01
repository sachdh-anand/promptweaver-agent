import aiohttp
import asyncio
import json
import time
from pprint import pprint

# Constants
BASE_URL = "http://localhost:8000"  # PromptWeaver API base URL
AGENT_CARD_URL = f"{BASE_URL}/.well-known/agent.json"  # Agent card URL
A2A_ENDPOINT = f"{BASE_URL}/a2a"  # A2A endpoint

async def fetch_agent_card():
    """
    Discover the PromptWeaver agent by fetching its Agent Card
    """
    print("\n📄 Fetching Agent Card...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(AGENT_CARD_URL) as response:
            if response.status != 200:
                print(f"Error: {response.status} - {response.reason}")
                return None
            
            agent_card = await response.json()
            print("✅ Agent Card fetched successfully!")
            
            # Display key information
            print(f"\nAgent: {agent_card['agent']['name']} (v{agent_card['agent']['version']})")
            print(f"Description: {agent_card['agent']['description']}")
            print(f"API Endpoint: {agent_card['agent']['endpoint']}")
            
            # Display skills
            print("\nAvailable Skills:")
            for skill in agent_card['skills']:
                print(f"  - {skill['name']}: {skill['description']}")
            
            # Display operating modes
            print("\nOperating Modes:")
            for mode in agent_card['custom_data']['operating_modes']:
                print(f"  - {mode['name']}: {mode['description']}")
            
            return agent_card

async def send_task(description, mode="lean"):
    """
    Send a task to the PromptWeaver agent
    """
    print(f"\n📝 Sending prompt generation request (mode: {mode})...")
    
    # Prepare request payload
    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": description
                    },
                    {
                        "type": "data",
                        "data": {
                            "mode": mode
                        }
                    }
                ]
            }
        },
        "id": 1
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(A2A_ENDPOINT, json=payload) as response:
            if response.status != 200:
                print(f"Error: {response.status} - {response.reason}")
                return None
            
            result = await response.json()
            if "error" in result:
                print(f"Error: {result['error']['message']}")
                return None
            
            task = result["result"]
            print(f"✅ Task created with ID: {task['id']}")
            print(f"Current state: {task['state']}")
            
            return task

async def poll_task(task_id, poll_interval=1):
    """
    Poll a task until it reaches a terminal state
    """
    print("\n⏳ Polling task until completion...")
    terminal_states = ["completed", "failed", "canceled"]
    
    async with aiohttp.ClientSession() as session:
        while True:
            # Prepare request payload
            payload = {
                "jsonrpc": "2.0",
                "method": "tasks/get",
                "params": {
                    "id": task_id
                },
                "id": 1
            }
            
            async with session.post(A2A_ENDPOINT, json=payload) as response:
                if response.status != 200:
                    print(f"Error: {response.status} - {response.reason}")
                    return None
                
                result = await response.json()
                if "error" in result:
                    print(f"Error: {result['error']['message']}")
                    return None
                
                task = result["result"]
                state = task["state"]
                
                print(f"Task state: {state}")
                
                if state in terminal_states:
                    print("✅ Task completed!")
                    return task
                
                # Wait before polling again
                await asyncio.sleep(poll_interval)

async def display_result(task):
    """
    Display the result of a completed task
    """
    if not task:
        return
    
    print("\n==== RESULT ====")
    
    # Find the agent's response message
    agent_messages = [msg for msg in task["messages"] if msg["role"] == "agent"]
    if not agent_messages:
        print("No agent response found.")
        return
    
    # Get the latest agent message
    latest_message = agent_messages[-1]
    
    # Display the prompt
    for part in latest_message["parts"]:
        if part["type"] == "text":
            print(part["text"])

async def main():
    """
    Main function to test the PromptWeaver A2A integration
    """
    print("====== PromptWeaver A2A Test ======")
    
    # Fetch agent card
    agent_card = await fetch_agent_card()
    if not agent_card:
        print("Failed to fetch agent card. Make sure the server is running.")
        return
    
    # Test case 1: Generate prompt in lean mode
    print("\n\n----- Test Case 1: Lean Mode -----")
    description = "Explain quantum computing to high school students"
    task = await send_task(description, mode="lean")
    if task:
        task = await poll_task(task["id"])
        await display_result(task)
    
    # Test case 2: Generate prompt in full mode
    print("\n\n----- Test Case 2: Full Mode -----")
    description = "Create a story about a time-traveling detective"
    task = await send_task(description, mode="full")
    if task:
        task = await poll_task(task["id"])
        await display_result(task)

if __name__ == "__main__":
    asyncio.run(main())