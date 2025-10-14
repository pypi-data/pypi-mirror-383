# Quick Start Guide

Get started with KagglerBoze in 5 minutes!

## Installation

```bash
pip install kagglerboze
```

Or from source:

```bash
git clone https://github.com/StarBoze/kagglerboze.git
cd kagglerboze
pip install -e .
```

## Prerequisites

1. **Kaggle API credentials**
   - Download `kaggle.json` from https://www.kaggle.com/settings
   - Place in `~/.kaggle/kaggle.json`

2. **Optional: Anthropic API key** (for LLM features)
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-xxxxx
   ```

## Your First Competition

### Using Claude Code (Recommended)

```bash
# In Claude Code terminal
/compete titanic
```

That's it! Claude Code will:
- Download competition data
- Analyze the task
- Generate features
- Optimize with XGBoost/LightGBM + Genetic Algorithm
- Submit predictions

### Using Python API

```python
from kaggler.tabular import XGBoostGA, LightGBMGA
from kaggler.kaggle import KaggleClient
import pandas as pd

# Download competition data
client = KaggleClient()
client.download_competition("titanic")

# Load data
train = pd.read_csv("data/titanic/train.csv")
test = pd.read_csv("data/titanic/test.csv")

X_train = train.drop(["Survived", "PassengerId"], axis=1)
y_train = train["Survived"]
X_test = test.drop(["PassengerId"], axis=1)

# Optimize with Genetic Algorithm
model = XGBoostGA(
    population_size=20,
    generations=10,
    task_type="classification"
)

# Train with GA optimization
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Create submission
submission = pd.DataFrame({
    "PassengerId": test["PassengerId"],
    "Survived": predictions
})
submission.to_csv("submission.csv", index=False)

# Submit
client.submit(
    "titanic",
    "submission.csv",
    message="XGBoost + GA optimization"
)
```

## Advanced: GEPA for Custom Domains

KagglerBoze includes GEPA (Genetic-Pareto Reflective Evolution) for optimizing prompts in custom domains. These are **advanced features** for non-Kaggle tasks:

### Medical Domain Example (GEPA Technology Demo)

```python
from kaggler.domains.medical import MedicalExtractor, MedicalTemplates

# Get optimized prompt (96%+ accuracy)
prompt = MedicalTemplates.get_template("temperature")

# Extract medical data
extractor = MedicalExtractor()
result = extractor.extract_all("患者は37.8°Cの発熱があり、咳と頭痛を訴えている")

# Output:
# {
#     "temperature": {"value": 37.8, "classification": "fever"},
#     "symptoms": [
#         {"symptom": "fever", "severity": null},
#         {"symptom": "cough", "severity": null},
#         {"symptom": "headache", "severity": null}
#     ]
# }
```

### Finance Domain Example (GEPA Technology Demo)

```python
from kaggler.domains.finance import StockAnalyzer, SentimentAnalyzer

# Stock screening
analyzer = StockAnalyzer()
result = analyzer.analyze("トヨタ自動車: PER 12.3, PBR 0.9, ROE 13.2%, 配当3.2%")

# Output:
# {
#     "ticker": "トヨタ自動車",
#     "recommendation": "buy",
#     "confidence": 0.92,
#     "reasons": ["PER < 15 (割安)", "PBR < 1.0 (純資産割れ)", "配当 > 3% (高配当)"]
# }

# Sentiment analysis
sentiment = SentimentAnalyzer()
result = sentiment.analyze("業績好調、上方修正を発表")
# Output: {"sentiment": "positive", "score": 0.85, "confidence": 0.93}
```

**Note**: These domain modules showcase GEPA's prompt optimization capabilities but are not specific to Kaggle competitions. For Kaggle competitions, use the tabular modules (XGBoostGA, LightGBMGA).

## GEPA Prompt Optimization

Evolve prompts for maximum accuracy:

```python
from kaggler.core import EvolutionEngine, EvolutionConfig

# Configure evolution
config = EvolutionConfig(
    population_size=20,
    generations=10,
    objectives=["accuracy", "speed", "cost"]
)

# Define evaluation function
def evaluate_prompt(prompt):
    # Your evaluation logic
    accuracy = test_on_validation_set(prompt)
    return {"accuracy": accuracy, "speed": 1.0, "cost": 0.5}

# Evolve!
engine = EvolutionEngine(config)
best_prompt = engine.evolve(
    seed_prompts=["Extract medical data from text"],
    eval_func=evaluate_prompt
)

print(f"Optimized prompt:\n{best_prompt.prompt}")
print(f"Accuracy: {best_prompt.fitness_scores['accuracy']:.3f}")
```

## What's Next?

- [Architecture Overview](ARCHITECTURE.md)
- [Medical Domain Guide](MEDICAL_DOMAIN.md) - Not yet created, see medical extractors
- [Finance Domain Guide](FINANCE_DOMAIN.md) - Stock screening, sentiment analysis
- [Examples](../examples/) - Medical and finance examples

## Common Issues

**Q: "Kaggle API authentication failed"**

A: Make sure `~/.kaggle/kaggle.json` exists and contains valid credentials.

**Q: "GEPA optimization is slow"**

A: Reduce population size or generations:
```python
config = EvolutionConfig(population_size=10, generations=5)
```

**Q: "Where are my submissions?"**

A: Check with:
```python
client = KaggleClient()
subs = client.get_my_submissions("competition-name")
```

## Support

- GitHub Issues: https://github.com/StarBoze/kagglerboze/issues
- Documentation: https://kagglerboze.readthedocs.io
- Examples: `/examples` directory
