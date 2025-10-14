# Analyze Command

Analyze competition data and generate insights.

## Usage

```
/analyze [focus-area]
```

## Focus Areas

- `all` - Complete analysis (default)
- `data` - Data structure and quality
- `features` - Feature analysis
- `target` - Target variable analysis
- `competition` - Competition metadata

## Example

```
/analyze

> Analyzing competition data...
>
> === Competition Info ===
> Name: Titanic - Machine Learning from Disaster
> Type: Binary Classification
> Metric: Accuracy
> Deadline: 2030-01-01 (永続コンペ)
>
> === Data Overview ===
> Train: 891 samples
> Test: 418 samples
> Features: 11 (Age, Sex, Pclass, Fare, Embarked, etc.)
> Target: Survived (0 or 1)
>
> === Data Quality ===
> Missing values:
>   - Age: 19.9%
>   - Cabin: 77.1%
>   - Embarked: 0.2%
> Class distribution:
>   - Survived: 38.4%
>   - Died: 61.6%
>
> === Recommended Approach ===
> 1. Use XGBoost + GA optimization
> 2. Feature engineering (family size, titles from names)
> 3. Handle missing values (Age imputation)
> 4. Consider Pclass, Sex, Age interactions
> 5. Estimated time: 30-60 minutes
>
> === Similar Competitions ===
> - House Prices (regression variant)
> - Spaceship Titanic (modern version)
```
