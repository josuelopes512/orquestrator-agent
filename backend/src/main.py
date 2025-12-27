import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .agent import execute_plan, get_execution, get_all_executions
from .execution import (
    ExecutePlanRequest,
    ExecutePlanResponse,
    ExecutionsResponse,
    HealthResponse,
    LogsResponse,
)

app = FastAPI(
    title="Kanban Agent Server",
    description="Backend server for Kanban + Claude Agent SDK integration",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/api/logs/{card_id}", response_model=LogsResponse)
async def get_logs(card_id: str):
    """Get logs for a specific card."""
    execution = get_execution(card_id)

    if not execution:
        return LogsResponse(
            success=False,
            error="No execution found for this card",
        )

    return LogsResponse(
        success=True,
        execution=execution,
    )


@app.get("/api/executions", response_model=ExecutionsResponse)
async def get_executions():
    """Get all executions."""
    executions = get_all_executions()
    return ExecutionsResponse(
        success=True,
        executions=executions,
    )


@app.post("/api/execute-plan", response_model=ExecutePlanResponse)
async def execute_plan_endpoint(request: ExecutePlanRequest):
    """Execute a plan."""
    # Validate request
    if not request.card_id or not request.title:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: cardId and title are required",
        )

    print(f"[Server] Received plan request for card: {request.card_id}")
    print(f"[Server] Title: {request.title}")
    print(f"[Server] Description: {request.description or '(none)'}")

    try:
        # Use parent directory as working directory (the main project)
        cwd = str(Path.cwd().parent)

        result = await execute_plan(
            card_id=request.card_id,
            title=request.title,
            description=request.description or "",
            cwd=cwd,
        )

        if result.success:
            return ExecutePlanResponse(
                success=True,
                cardId=request.card_id,
                result=result.result,
                logs=result.logs,
            )
        else:
            error_response = ExecutePlanResponse(
                success=False,
                cardId=request.card_id,
                error=result.error,
                logs=result.logs,
            )
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump(by_alias=True),
            )

    except Exception as e:
        error_message = str(e)
        print(f"[Server] Error: {error_message}")
        error_response = ExecutePlanResponse(
            success=False,
            cardId=request.card_id,
            error=error_message,
            logs=[],
        )
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump(by_alias=True),
        )


def main():
    """Run the server."""
    import uvicorn

    port = int(os.environ.get("PORT", 3001))
    print(f"[Server] Agent server running on http://localhost:{port}")
    print("[Server] Endpoints:")
    print("  - GET  /health")
    print("  - GET  /api/logs/:cardId")
    print("  - GET  /api/executions")
    print("  - POST /api/execute-plan")

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
