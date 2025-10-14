# Optimize Command

Run GEPA optimization on prompts or model hyperparameters.

## Usage

```
/optimize [model-type]
```

## Model Types

- `prompt` - Optimize prompts using GEPA (default for NLP tasks)
- `xgboost` - Optimize XGBoost hyperparameters
- `lightgbm` - Optimize LightGBM hyperparameters
- `ensemble` - Optimize ensemble weights

## Examples

### Optimize prompt for NLP tasks

```
/optimize prompt

> Using GEPA to optimize prompt...
> Initial prompt: "Extract relevant information from text"
> Population size: 20, Generations: 10
>
> Generation 1: Best F1=0.72, Avg=0.68
> Generation 5: Best F1=0.87, Avg=0.82
> Generation 10: Best F1=0.91, Avg=0.88
>
> Optimization complete!
> Best prompt saved to: optimized_prompt.txt
> Performance: 0.72 → 0.91 (+26% improvement)
```

### Optimize XGBoost hyperparameters

```
/optimize xgboost

> Optimizing XGBoost with genetic algorithm...
> Parameter space:
>   - n_estimators: [100, 1000]
>   - learning_rate: [0.01, 0.3]
>   - max_depth: [3, 10]
>
> Generation 1: Best AUC=0.85
> Generation 10: Best AUC=0.92
>
> Best parameters:
>   n_estimators: 650
>   learning_rate: 0.08
>   max_depth: 7
```

## Configuration

```json
{
  "optimize": {
    "gepa": {
      "population_size": 20,
      "generations": 10,
      "objectives": ["accuracy", "speed", "cost"]
    },
    "hyperparameter": {
      "population_size": 50,
      "generations": 30
    }
  }
}
```
