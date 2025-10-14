# Submit Command

Submit predictions to Kaggle competition.

## Usage

```
/submit [message]
```

## What it does

1. Validates submission.csv format
2. Checks for missing/invalid values
3. Submits to Kaggle
4. Reports leaderboard score

## Example

```
/submit "XGBoost + GA optimization"

> Validating submission.csv...
> ✓ Format correct (PassengerId, Survived)
> ✓ All 418 test IDs present
> ✓ No missing values
> ✓ Binary values (0 or 1)
>
> Submitting to Kaggle...
> ✓ Submission successful!
>
> Results:
> Public score: 0.82
> Your rank: #1,247 / 13,946 (Top 9%)
>
> Comparison:
> CV score: 0.84
> Public score: 0.82
> Difference: -0.02 (slight overfitting, normal)
```

## Validation Checks

- File exists
- Correct columns (id + target)
- All test IDs present
- No missing values
- Value ranges valid
- Format matches sample_submission.csv
