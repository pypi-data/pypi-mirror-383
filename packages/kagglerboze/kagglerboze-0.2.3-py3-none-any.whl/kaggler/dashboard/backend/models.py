"""Pydantic models for the dashboard API."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CompetitionInfo(BaseModel):
    """Competition information model."""
    id: str = Field(..., description="Unique competition identifier")
    name: str = Field(..., description="Competition name")
    status: str = Field(..., description="Competition status (running, completed, failed)")
    start_time: datetime = Field(..., description="Competition start time")
    end_time: Optional[datetime] = Field(None, description="Competition end time")
    current_generation: int = Field(0, description="Current generation number")
    total_generations: int = Field(..., description="Total generations planned")
    best_score: Optional[float] = Field(None, description="Best score achieved")
    pareto_size: int = Field(0, description="Number of solutions in Pareto frontier")


class EvolutionMetrics(BaseModel):
    """Evolution metrics for a specific generation."""
    generation: int = Field(..., description="Generation number")
    timestamp: datetime = Field(..., description="Timestamp of the generation")
    best_score: float = Field(..., description="Best score in generation")
    mean_score: float = Field(..., description="Mean score in generation")
    std_score: float = Field(..., description="Standard deviation of scores")
    diversity: float = Field(..., description="Population diversity metric")
    pareto_size: int = Field(..., description="Pareto frontier size")
    computation_time: float = Field(..., description="Generation computation time (seconds)")


class ParetoSolution(BaseModel):
    """Individual solution on the Pareto frontier."""
    id: str = Field(..., description="Solution identifier")
    scores: Dict[str, float] = Field(..., description="Objective scores")
    hyperparameters: Dict[str, Any] = Field(..., description="Solution hyperparameters")
    generation: int = Field(..., description="Generation when solution was found")
    dominated_count: int = Field(0, description="Number of solutions this dominates")


class EvolutionProgress(BaseModel):
    """Complete evolution progress data."""
    competition_id: str = Field(..., description="Competition identifier")
    competition_name: str = Field(..., description="Competition name")
    metrics_history: List[EvolutionMetrics] = Field(..., description="Historical metrics")
    pareto_frontier: List[ParetoSolution] = Field(..., description="Current Pareto frontier")
    current_generation: int = Field(..., description="Current generation")
    total_generations: int = Field(..., description="Total generations")
    is_running: bool = Field(..., description="Whether evolution is running")


class CompetitionRequest(BaseModel):
    """Request to start a new competition."""
    competition_name: str = Field(..., description="Name of the competition")
    dataset_path: str = Field(..., description="Path to the dataset")
    population_size: int = Field(50, description="Population size")
    generations: int = Field(100, description="Number of generations")
    objectives: List[str] = Field(
        ["accuracy", "complexity"],
        description="Optimization objectives"
    )
    time_limit: Optional[int] = Field(None, description="Time limit in seconds")
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


class CompetitionResponse(BaseModel):
    """Response after starting a competition."""
    competition_id: str = Field(..., description="Unique competition identifier")
    status: str = Field(..., description="Competition status")
    message: str = Field(..., description="Response message")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str = Field(..., description="Message type (update, complete, error)")
    competition_id: str = Field(..., description="Competition identifier")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class PerformanceMetrics(BaseModel):
    """System performance metrics."""
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    active_competitions: int = Field(..., description="Number of active competitions")
    total_evaluations: int = Field(..., description="Total evaluations performed")
    uptime_seconds: float = Field(..., description="System uptime in seconds")
