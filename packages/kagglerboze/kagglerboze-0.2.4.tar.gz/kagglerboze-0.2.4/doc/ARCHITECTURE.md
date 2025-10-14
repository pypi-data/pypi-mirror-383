# Architecture Overview

KagglerBoze combines GEPA (Genetic-Pareto Reflective Evolution) with Kaggle best practices.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Code CLI                        │
│  (/compete, /optimize, /submit, /analyze commands)      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 KagglerBoze Core                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ GEPA Engine │  │ Domain Models│  │ Kaggle API    │  │
│  ├─────────────┤  ├──────────────┤  ├───────────────┤  │
│  │ Evolution   │  │ Medical      │  │ Download      │  │
│  │ Pareto      │  │ Finance      │  │ Submit        │  │
│  │ Reflection  │  │ NLP          │  │ Leaderboard   │  │
│  │ Mutation    │  │ Vision       │  │ Tracking      │  │
│  │ Crossover   │  │ ...          │  │               │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
└──────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              External Services                           │
├──────────────────────────────────────────────────────────┤
│  • Kaggle API (competition data, submissions)           │
│  • Anthropic API (Claude for LLM tasks)                 │
│  • MLflow (experiment tracking)                          │
└──────────────────────────────────────────────────────────┘
```

## Core Modules

### 1. GEPA Engine (`src/kaggler/core/`)

Implements the Genetic-Pareto Reflective Evolution algorithm:

- **evolution.py**: Main evolutionary loop
  - Population management
  - Fitness evaluation
  - Generation cycles
  - History tracking

- **pareto.py**: Multi-objective optimization
  - Pareto frontier computation
  - Dominance checking
  - Crowding distance
  - Trade-off selection

- **reflection.py**: Intelligent mutation
  - Error pattern analysis
  - LLM-based improvement suggestions
  - Root cause diagnosis
  - Directed evolution

- **mutation.py**: Mutation strategies
  - Rule refinement
  - Example injection
  - Structure reorganization
  - Adaptive mutation rates

- **crossover.py**: Semantic crossover
  - Section-based crossover
  - Template-based crossover
  - Uniform crossover

### 2. Domain Models (`src/kaggler/domains/`)

Specialized implementations for different competition types:

#### Medical Domain (`domains/medical/`)
- **templates.py**: Optimized prompts (96%+ accuracy)
- **extractors.py**: Medical data extraction logic
- **metrics.py**: F1, accuracy, specialized medical metrics
- **validators.py**: Data validation and sanitization

#### Future Domains
- Finance (technical indicators, risk metrics)
- NLP (sentiment, NER, classification)
- Computer Vision (object detection, segmentation)
- Time Series (forecasting, anomaly detection)

### 3. Kaggle Integration (`src/kaggler/kaggle/`)

Complete Kaggle API wrapper:

- **client.py**: High-level API operations
- **downloader.py**: Competition data download
- **submitter.py**: Submission validation and submission
- **leaderboard.py**: Score tracking, shake-up prediction

### 4. Claude Code Integration (`.claude/`)

Custom agents and commands:

- **agents/competition-analyzer.md**: Competition analysis
- **agents/feature-engineer.md**: Feature generation
- **agents/model-optimizer.md**: GEPA optimization
- **agents/submission-generator.md**: Prediction generation

- **commands/compete.md**: `/compete` - End-to-end automation
- **commands/optimize.md**: `/optimize` - GEPA/hyperparameter tuning
- **commands/submit.md**: `/submit` - Submission handling
- **commands/analyze.md**: `/analyze` - Data analysis

## Data Flow

### Typical Competition Workflow

```
1. /compete medical-text-extraction
   │
   ├─> Download data (KaggleClient)
   │
   ├─> Analyze competition (CompetitionAnalyzer)
   │   └─> Identify: NLP extraction, F1 metric
   │
   ├─> Load domain templates (MedicalTemplates)
   │
   ├─> GEPA optimization (EvolutionEngine)
   │   ├─> Initialize population (20 prompts)
   │   ├─> Evaluate fitness (parallel)
   │   ├─> Select parents (Pareto front)
   │   ├─> Generate offspring (crossover + mutation)
   │   ├─> Reflect and improve (ReflectionEngine)
   │   └─> Iterate 10 generations
   │
   ├─> Generate predictions (MedicalExtractor)
   │
   ├─> Validate submission (SubmissionManager)
   │
   └─> Submit to Kaggle (KaggleClient)
```

### GEPA Evolution Flow

```
Initial Prompt: "Extract medical data"
      │
      ▼
┌─────────────────────────────────┐
│  Population Initialization      │
│  - 20 variants generated        │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Parallel Evaluation            │
│  - Test on validation set       │
│  - Compute F1, speed, cost      │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Pareto Selection               │
│  - Find non-dominated solutions │
│  - Balance accuracy/speed/cost  │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Crossover & Mutation           │
│  - Semantic prompt combination  │
│  - Reflection-based improvement │
└──────────┬──────────────────────┘
           │
           ▼
      Repeat 10x
           │
           ▼
Optimized Prompt: "MEDICAL DATA EXTRACTION PROTOCOL v2.3..."
(96% accuracy)
```

## Key Design Decisions

### 1. Why GEPA over Fine-tuning?

- **Cost**: $5 vs $500+ for fine-tuning
- **Speed**: 30 minutes vs 6+ hours
- **Resources**: 8GB RAM vs 48GB+ VRAM
- **Flexibility**: Easy to adapt to new domains
- **Interpretability**: Human-readable prompts

### 2. Domain-First Approach

Start with a sharp, specialized implementation (medical) rather than generic AutoML:
- Faster to market
- Clearer value proposition
- Easier to validate (96% accuracy benchmark)
- Natural expansion path to other domains

### 3. Claude Code Integration

Leverage Claude Code's agent system for:
- Natural language interface
- Automatic workflow orchestration
- Built-in error handling
- Session persistence

### 4. Multi-Objective Optimization

Balance multiple objectives (accuracy, speed, cost) using Pareto optimization:
- No single "best" solution
- User can choose trade-offs
- More robust than single-objective

## Performance Characteristics

### GEPA Optimization
- **Time**: 30-60 minutes (10-50 generations)
- **Memory**: 4-8GB RAM
- **Parallel**: 4-8 workers (configurable)
- **Improvement**: Typically 15-30% over baseline

### Medical Extraction
- **Accuracy**: 96%+ on temperature classification
- **F1 Score**: 94%+ on symptom extraction
- **Speed**: <100ms per document
- **Scalability**: 1000s of documents

## Extensibility

### Adding New Domains

1. Create domain directory: `src/kaggler/domains/mydomain/`
2. Implement modules:
   - `templates.py` - Seed prompts
   - `extractors.py` - Extraction logic
   - `metrics.py` - Domain metrics
   - `validators.py` - Validation rules

3. Register in `src/kaggler/domains/__init__.py`

### Custom Mutation Strategies

```python
from kaggler.core.mutation import MutationStrategy

class CustomMutation(MutationStrategy):
    def mutate(self, prompt, context):
        # Your mutation logic
        return modified_prompt
```

### Custom Objectives

```python
config = EvolutionConfig(
    objectives=["accuracy", "latency", "token_count", "custom_metric"]
)
```

## Monitoring and Debugging

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Detailed evolution logs
# Generation progress
# Error diagnostics
```

### Experiment Tracking

```python
# MLflow integration (planned)
from kaggler.tracking import MLflowTracker

tracker = MLflowTracker()
tracker.log_evolution_run(engine)
```

## Security Considerations

- **API Keys**: Never commit `kaggle.json` or API keys
- **Data Privacy**: Competition data may be confidential
- **Rate Limiting**: Respect Kaggle API limits
- **Validation**: Always validate before submission

## Future Architecture Plans

- Distributed evolution across multiple machines
- Real-time collaboration features
- Web dashboard for monitoring
- Pre-trained prompt libraries
- AutoML integration
