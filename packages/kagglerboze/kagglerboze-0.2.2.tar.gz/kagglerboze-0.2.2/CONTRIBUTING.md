# Contributing to KagglerBoze

Thank you for your interest in contributing to KagglerBoze! We welcome contributions from the community.

## 🌟 Ways to Contribute

### 1. New Domain Implementations
Expand KagglerBoze to new domains (legal, manufacturing, customer service, etc.)

**Steps:**
1. Create `src/kaggler/domains/{domain_name}/`
2. Implement templates, analyzers, validators
3. Write tests in `tests/domains/{domain_name}/`
4. Add documentation in `docs/{DOMAIN}_DOMAIN.md`
5. Add examples in `examples/{domain_name}/`

**Template structure:**
```python
# src/kaggler/domains/your_domain/__init__.py
from .analyzers import YourAnalyzer
from .templates import YourTemplates

__all__ = ["YourAnalyzer", "YourTemplates"]
```

### 2. GEPA Core Improvements
Enhance the evolutionary algorithm

**Areas:**
- Faster convergence strategies
- Distributed evolution (multi-process)
- Better mutation strategies
- Enhanced reflection prompts

### 3. Kaggle Integration
Improve competition automation

**Ideas:**
- Auto-detect competition type
- Ensemble predictions
- Hyperparameter optimization
- Leaderboard shake-up prediction

### 4. Documentation
Help others understand and use KagglerBoze

**Needs:**
- Tutorials and guides
- Video walkthroughs
- Blog posts
- Translations (日本語, 中文, etc.)

### 5. Testing
Increase test coverage and robustness

**Target:**
- Core modules: 90%+ coverage
- Domain modules: 85%+ coverage
- Integration tests
- Performance benchmarks

## 🚀 Getting Started

### Development Setup

```bash
# Clone repository
git clone https://github.com/StarBoze/kagglerboze.git
cd kagglerboze

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ --cov=src/kaggler

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
kagglerboze/
├── src/kaggler/          # Source code
│   ├── core/            # GEPA engine
│   ├── domains/         # Domain implementations
│   └── kaggle/          # Kaggle API wrapper
├── tests/               # Test suite
├── docs/                # Documentation
├── examples/            # Example scripts
└── .github/             # GitHub workflows
```

## 📝 Coding Standards

### Python Style
- **Formatter**: Black (line length 100)
- **Import sorting**: isort
- **Type hints**: Use where helpful
- **Docstrings**: Google style

### Example:
```python
def calculate_score(values: List[float], weights: Optional[List[float]] = None) -> float:
    """
    Calculate weighted score from values.

    Args:
        values: List of numeric values
        weights: Optional weights (defaults to equal weighting)

    Returns:
        Weighted average score

    Example:
        >>> calculate_score([0.8, 0.9, 0.85])
        0.85
    """
    ...
```

### Testing
- **Framework**: pytest
- **Coverage target**: 80%+
- **Test naming**: `test_<function>_<scenario>`
- **Fixtures**: Use for common test data

```python
def test_analyzer_handles_japanese_text():
    """Test analyzer correctly processes Japanese input."""
    analyzer = YourAnalyzer()
    result = analyzer.analyze("日本語テキスト")
    assert result['confidence'] > 0.9
```

### Documentation
- **Format**: Markdown
- **Code blocks**: Include language tags
- **Examples**: Provide runnable code
- **Links**: Use relative paths

## 🔄 Pull Request Process

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write code
- Add tests
- Update documentation
- Format code

### 3. Run Quality Checks
```bash
# Tests
pytest tests/ --cov=src/kaggler

# Formatting
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### 4. Commit
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Feature
git commit -m "feat: add legal domain analyzer"

# Bug fix
git commit -m "fix: correct temperature boundary classification"

# Documentation
git commit -m "docs: add finance domain tutorial"

# Refactoring
git commit -m "refactor: simplify evolution loop logic"

# Tests
git commit -m "test: add tests for stock analyzer"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- **Title**: Clear and descriptive
- **Description**: What, why, and how
- **Tests**: Demonstrate changes work
- **Screenshots**: If UI changes

### PR Template
```markdown
## What
Brief description of changes

## Why
Problem being solved or feature being added

## How
Technical approach and key changes

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manually tested

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Examples provided (if new feature)
```

## 🐛 Bug Reports

Use [GitHub Issues](https://github.com/StarBoze/kagglerboze/issues) with:

**Title**: Short, descriptive summary

**Description**:
```markdown
## Bug Description
What happened vs what should happen

## Steps to Reproduce
1. Install kagglerboze
2. Run `analyzer.analyze(...)`
3. See error

## Environment
- OS: macOS 14.0
- Python: 3.10.5
- kagglerboze: 0.2.0

## Expected Behavior
Should return valid result

## Actual Behavior
Raises ValueError

## Error Log
```
Traceback (most recent call last):
  ...
```
\`\`\`

## Possible Solution (optional)
Suggested fix
```

## 💡 Feature Requests

**Title**: Concise feature name

**Description**:
```markdown
## Feature Description
What feature do you want?

## Use Case
Why is this useful? Who benefits?

## Proposed Solution
How might this work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Screenshots, examples, references
```

## 📋 Domain Contribution Checklist

When adding a new domain:

- [ ] **Templates** (`templates.py`)
  - [ ] 3+ pre-optimized templates
  - [ ] Clear classification rules
  - [ ] Edge case handling
  - [ ] JSON output format specified

- [ ] **Analyzers** (`analyzers.py`)
  - [ ] High-level API classes
  - [ ] Extraction/classification logic
  - [ ] Confidence scoring
  - [ ] Error handling

- [ ] **Metrics** (`metrics.py`)
  - [ ] Domain-specific metrics
  - [ ] Evaluation functions
  - [ ] Benchmark calculations

- [ ] **Validators** (`validators.py`)
  - [ ] Data validation
  - [ ] Sanitization utilities
  - [ ] Outlier detection

- [ ] **Tests** (`tests/domains/{domain}/`)
  - [ ] Unit tests (80%+ coverage)
  - [ ] Integration tests
  - [ ] Edge case tests
  - [ ] Benchmark validation

- [ ] **Documentation** (`docs/{DOMAIN}_DOMAIN.md`)
  - [ ] Quick start (5-minute guide)
  - [ ] API reference
  - [ ] Use cases (3+ examples)
  - [ ] Benchmark results

- [ ] **Examples** (`examples/{domain}/`)
  - [ ] Basic usage script
  - [ ] Advanced examples
  - [ ] Real-world use case

## 🎯 Good First Issues

Look for issues labeled [`good first issue`](https://github.com/StarBoze/kagglerboze/labels/good%20first%20issue):

- Documentation improvements
- Adding examples
- Writing tests
- Fixing typos
- Adding type hints

## 🤝 Code of Conduct

Be respectful, inclusive, and collaborative:
- Welcome newcomers
- Give constructive feedback
- Focus on the code, not the person
- Respect different opinions
- Help create a positive environment

## 📞 Getting Help

- **Discussions**: [GitHub Discussions](https://github.com/StarBoze/kagglerboze/discussions)
- **Issues**: [GitHub Issues](https://github.com/StarBoze/kagglerboze/issues)
- **Twitter**: [@kagglerboze](https://twitter.com/kagglerboze)

## 📚 Resources

- [GEPA Paper](https://arxiv.org/abs/2507.19457)
- [Architecture Docs](docs/ARCHITECTURE.md)
- [Medical Domain Guide](docs/MEDICAL_DOMAIN.md)
- [Finance Domain Guide](docs/FINANCE_DOMAIN.md)

## ⭐ Recognition

Contributors will be:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Given credit in documentation

Thank you for making KagglerBoze better! 🚀
