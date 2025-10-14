# Compete Command

Automatically compete in a Kaggle competition end-to-end.

## Usage

```
/compete <competition-name>
```

## What it does

1. **Download competition data**
   ```bash
   kaggle competitions download -c <competition-name>
   ```

2. **Analyze competition**
   - Competition type
   - Evaluation metric
   - Data structure
   - Recommended approach

3. **EDA (Exploratory Data Analysis)**
   - Data distributions
   - Missing values
   - Correlations
   - Target analysis

4. **Feature engineering**
   - Generate domain-specific features
   - Handle missing values
   - Encode categorical variables

5. **Model training & optimization**
   - For NLP tasks: Use GEPA to evolve prompts
   - For tabular: Use gradient boosting + genetic hyperparameter tuning
   - Cross-validation
   - Hyperparameter optimization

6. **Generate submission**
   - Create submission.csv
   - Validate format
   - Submit to Kaggle

7. **Report results**
   - CV score
   - Public leaderboard score
   - Suggested improvements

## Example

```
/compete titanic

> Downloading competition data...
> Analyzing competition... Type: Binary Classification, Metric: Accuracy
> Running EDA...
> Engineering features...
> Training with XGBoost + GA optimization (30 min estimated)...
> Generation 1: Accuracy=0.76
> Generation 5: Accuracy=0.81
> Generation 10: Accuracy=0.84
> Creating submission...
> Submitting to Kaggle...
> Public score: 0.82 (Top 15%)
>
> Next steps:
> - Try stacking with LightGBM
> - Feature engineering (family size, titles)
> - Tune ensemble weights
```

## Configuration

Can be configured via `/Users/b416/star-boze/kagglerboze/kagglerboze/.claude/settings.json`:

```json
{
  "compete": {
    "auto_submit": true,
    "gepa_generations": 10,
    "cv_folds": 5,
    "time_limit_minutes": 60
  }
}
```
