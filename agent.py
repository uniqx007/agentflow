import os
from google.adk.agents import Agent
from google.adk.tools import Tool
from google.adk.memory import InMemoryMemory
import httpx

# ── Tool Definitions (MCP-style) ──────────────────────────

async def search_knowledge_base(query: str) -> str:
    """Search the enterprise knowledge base (simulates AlloyDB AI vector search)."""
    # In production: connect to AlloyDB AI with pgvector
    # import asyncpg
    # conn = await asyncpg.connect(os.environ["ALLOYDB_URL"])
    # results = await conn.fetch("SELECT content FROM docs ORDER BY embedding <-> $1 LIMIT 3", query_embedding)
    return f"Knowledge base results for '{query}': Found 3 relevant documents about enterprise AI workflows."

async def google_search(query: str) -> str:
    """Search the web using Google Search API."""
    # In production: use Google Custom Search API
    api_key = os.environ.get("GOOGLE_SEARCH_API_KEY", "")
    cx = os.environ.get("GOOGLE_SEARCH_CX", "")
    if api_key and cx:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": api_key, "cx": cx, "q": query}
            )
            data = resp.json()
            items = data.get("items", [])[:3]
            return "\n".join([f"- {i['title']}: {i['snippet']}" for i in items])
    return f"Search results for '{query}': [Connect GOOGLE_SEARCH_API_KEY to enable live search]"

async def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail API (MCP Gmail tool)."""
    # In production: use Gmail API with OAuth2
    return f"Email sent to {to} with subject '{subject}' ✓"

async def create_calendar_event(title: str, date: str, time: str) -> str:
    """Create a Google Calendar event (MCP Calendar tool)."""
    # In production: use Google Calendar API
    return f"Calendar event '{title}' created on {date} at {time} ✓"

# ── ADK Agent Setup ───────────────────────────────────────

tools = [
    Tool(name="search_knowledge_base", func=search_knowledge_base,
         description="Search the enterprise knowledge base for relevant information"),
    Tool(name="google_search", func=google_search,
         description="Search the web for current information"),
    Tool(name="send_email", func=send_email,
         description="Send an email to a recipient"),
    Tool(name="create_calendar_event", func=create_calendar_event,
         description="Create a calendar event with title, date and time"),
]

memory = InMemoryMemory()

supervisor_agent = Agent(
    name="AgentFlow Supervisor",
    model=os.environ.get("GEMINI_MODEL", "gemini-1.5-pro"),
    tools=tools,
    memory=memory,
    system_prompt="""You are AgentFlow, an intelligent enterprise AI assistant.
You help users by:
1. Searching the knowledge base for relevant enterprise information
2. Searching the web for current information
3. Sending emails on behalf of the user
4. Scheduling calendar events

Always think step-by-step, use the available tools, and provide clear, concise responses.
For complex tasks, break them down into subtasks and execute them in order."""
)

# ── Agent Runner ──────────────────────────────────────────

async def run_agent(query: str, session_id: str) -> dict:
    """Run the agent with a user query and return the response."""
    steps = []

    def on_tool_call(tool_name: str, args: dict):
        steps.append({"tool": tool_name, "args": args})

    response = await supervisor_agent.run(
        query,
        session_id=session_id,
        on_tool_call=on_tool_call
    )

    return {
        "response": response.text,
        "steps": steps
    }
