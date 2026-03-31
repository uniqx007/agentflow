from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import run_agent

app = FastAPI(title="AgentFlow API", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"

class QueryResponse(BaseModel):
    response: str
    session_id: str
    steps: list

@app.get("/")
def root():
    return {"status": "AgentFlow is running!", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/agent/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    try:
        result = await run_agent(request.query, request.session_id)
        return QueryResponse(
            response=result["response"],
            session_id=request.session_id,
            steps=result.get("steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
