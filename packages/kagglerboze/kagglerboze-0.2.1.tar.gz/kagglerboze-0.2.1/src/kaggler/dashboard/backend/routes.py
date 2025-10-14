"""API routes for the dashboard."""
import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
import logging

from .models import (
    CompetitionInfo,
    EvolutionProgress,
    CompetitionRequest,
    CompetitionResponse,
    PerformanceMetrics,
)
from .websocket import notifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["dashboard"])

# In-memory storage (replace with database in production)
competitions: Dict[str, Dict] = {}
evolution_data: Dict[str, List[Dict]] = {}
pareto_data: Dict[str, List[Dict]] = {}


@router.get("/competitions", response_model=List[CompetitionInfo])
async def list_competitions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """List all competitions with optional filtering."""
    try:
        comps = list(competitions.values())

        # Filter by status if provided
        if status:
            comps = [c for c in comps if c.get("status") == status]

        # Sort by start time (most recent first)
        comps.sort(key=lambda x: x.get("start_time", datetime.min), reverse=True)

        # Apply pagination
        comps = comps[offset:offset + limit]

        # Convert to response model
        results = []
        for comp in comps:
            results.append(
                CompetitionInfo(
                    id=comp["id"],
                    name=comp["name"],
                    status=comp["status"],
                    start_time=comp["start_time"],
                    end_time=comp.get("end_time"),
                    current_generation=comp.get("current_generation", 0),
                    total_generations=comp.get("total_generations", 0),
                    best_score=comp.get("best_score"),
                    pareto_size=len(pareto_data.get(comp["id"], [])),
                )
            )

        return results
    except Exception as e:
        logger.error(f"Error listing competitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitions/{competition_id}", response_model=CompetitionInfo)
async def get_competition(competition_id: str):
    """Get detailed information about a specific competition."""
    if competition_id not in competitions:
        raise HTTPException(status_code=404, detail="Competition not found")

    comp = competitions[competition_id]
    return CompetitionInfo(
        id=comp["id"],
        name=comp["name"],
        status=comp["status"],
        start_time=comp["start_time"],
        end_time=comp.get("end_time"),
        current_generation=comp.get("current_generation", 0),
        total_generations=comp.get("total_generations", 0),
        best_score=comp.get("best_score"),
        pareto_size=len(pareto_data.get(competition_id, [])),
    )


@router.get("/evolution/{competition_id}", response_model=EvolutionProgress)
async def get_evolution_progress(
    competition_id: str,
    start_generation: int = Query(0, ge=0, description="Start generation"),
    end_generation: Optional[int] = Query(None, ge=0, description="End generation"),
):
    """Get evolution progress for a competition."""
    if competition_id not in competitions:
        raise HTTPException(status_code=404, detail="Competition not found")

    comp = competitions[competition_id]
    metrics = evolution_data.get(competition_id, [])
    pareto = pareto_data.get(competition_id, [])

    # Filter metrics by generation range
    if end_generation is not None:
        metrics = [m for m in metrics if start_generation <= m["generation"] <= end_generation]
    else:
        metrics = [m for m in metrics if m["generation"] >= start_generation]

    return EvolutionProgress(
        competition_id=competition_id,
        competition_name=comp["name"],
        metrics_history=metrics,
        pareto_frontier=pareto,
        current_generation=comp.get("current_generation", 0),
        total_generations=comp.get("total_generations", 0),
        is_running=comp["status"] == "running",
    )


@router.post("/compete", response_model=CompetitionResponse)
async def start_competition(request: CompetitionRequest):
    """Start a new competition."""
    try:
        competition_id = str(uuid.uuid4())

        # Create competition entry
        competitions[competition_id] = {
            "id": competition_id,
            "name": request.competition_name,
            "status": "running",
            "start_time": datetime.now(),
            "end_time": None,
            "current_generation": 0,
            "total_generations": request.generations,
            "best_score": None,
            "config": {
                "dataset_path": request.dataset_path,
                "population_size": request.population_size,
                "objectives": request.objectives,
                "time_limit": request.time_limit,
                "config": request.config or {},
            },
        }

        # Initialize data structures
        evolution_data[competition_id] = []
        pareto_data[competition_id] = []

        # Start evolution process in background
        asyncio.create_task(run_evolution(competition_id, request))

        # Notify clients
        await notifier.notify_status_change(
            competition_id,
            "running",
            {"message": "Competition started"}
        )

        return CompetitionResponse(
            competition_id=competition_id,
            status="running",
            message=f"Competition '{request.competition_name}' started successfully",
        )
    except Exception as e:
        logger.error(f"Error starting competition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compete/{competition_id}/stop")
async def stop_competition(competition_id: str):
    """Stop a running competition."""
    if competition_id not in competitions:
        raise HTTPException(status_code=404, detail="Competition not found")

    comp = competitions[competition_id]
    if comp["status"] != "running":
        raise HTTPException(status_code=400, detail="Competition is not running")

    # Update status
    comp["status"] = "stopped"
    comp["end_time"] = datetime.now()

    # Notify clients
    await notifier.notify_status_change(
        competition_id,
        "stopped",
        {"message": "Competition stopped by user"}
    )

    return {"message": "Competition stopped successfully"}


@router.delete("/compete/{competition_id}")
async def delete_competition(competition_id: str):
    """Delete a competition and its data."""
    if competition_id not in competitions:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Delete all data
    del competitions[competition_id]
    evolution_data.pop(competition_id, None)
    pareto_data.pop(competition_id, None)

    return {"message": "Competition deleted successfully"}


@router.get("/metrics", response_model=PerformanceMetrics)
async def get_system_metrics():
    """Get system performance metrics."""
    import psutil
    import time

    # Get system metrics
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    # Count active competitions
    active_count = sum(1 for c in competitions.values() if c["status"] == "running")

    # Count total evaluations
    total_evals = sum(
        len(metrics) * competitions[cid].get("config", {}).get("population_size", 50)
        for cid, metrics in evolution_data.items()
    )

    return PerformanceMetrics(
        cpu_usage=cpu_usage,
        memory_usage=memory.percent,
        active_competitions=active_count,
        total_evaluations=total_evals,
        uptime_seconds=time.time() - start_time,
    )


# Store start time
start_time = datetime.now().timestamp()


async def run_evolution(competition_id: str, request: CompetitionRequest):
    """Background task to simulate evolution process."""
    try:
        import random

        comp = competitions[competition_id]

        for generation in range(request.generations):
            # Simulate generation computation
            await asyncio.sleep(random.uniform(0.5, 2.0))

            # Check if competition was stopped
            if comp["status"] != "running":
                break

            # Generate simulated metrics
            best_score = random.uniform(0.7, 0.99) + generation * 0.001
            mean_score = best_score - random.uniform(0.1, 0.2)
            std_score = random.uniform(0.05, 0.15)
            diversity = random.uniform(0.3, 0.8)
            pareto_size = random.randint(5, 20)

            metrics = {
                "generation": generation,
                "timestamp": datetime.now(),
                "best_score": best_score,
                "mean_score": mean_score,
                "std_score": std_score,
                "diversity": diversity,
                "pareto_size": pareto_size,
                "computation_time": random.uniform(1.0, 5.0),
            }

            # Store metrics
            evolution_data[competition_id].append(metrics)

            # Update competition
            comp["current_generation"] = generation + 1
            comp["best_score"] = best_score

            # Generate simulated Pareto solutions
            if generation % 5 == 0:  # Update every 5 generations
                pareto = []
                for i in range(pareto_size):
                    pareto.append({
                        "id": str(uuid.uuid4()),
                        "scores": {
                            "accuracy": random.uniform(0.7, 0.95),
                            "complexity": random.uniform(0.6, 0.9),
                        },
                        "hyperparameters": {
                            "learning_rate": random.uniform(0.001, 0.1),
                            "max_depth": random.randint(3, 10),
                        },
                        "generation": generation,
                        "dominated_count": random.randint(0, 10),
                    })
                pareto_data[competition_id] = pareto

                # Notify Pareto update
                await notifier.notify_pareto_update(competition_id, pareto)

            # Notify generation complete
            await notifier.notify_generation_complete(
                competition_id,
                generation,
                metrics
            )

        # Competition complete
        comp["status"] = "completed"
        comp["end_time"] = datetime.now()

        await notifier.notify_competition_complete(
            competition_id,
            {
                "total_generations": comp["current_generation"],
                "best_score": comp["best_score"],
                "pareto_size": len(pareto_data.get(competition_id, [])),
            }
        )

    except Exception as e:
        logger.error(f"Error in evolution process: {e}")
        comp = competitions.get(competition_id)
        if comp:
            comp["status"] = "failed"
            comp["end_time"] = datetime.now()
        await notifier.notify_error(competition_id, str(e))
