# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2024-10-13

### Fixed
- **Version Reporting** - Fixed `kagglerboze version` showing incorrect version
  - Updated `__version__` in `__init__.py` to match package version
- **Package Distribution** - Fixed missing files in PyPI package
  - Added `README.en.md` to distribution
  - Added `CHANGELOG.md` to distribution
  - Added `.claude` directory to distribution for `install-claude` command

## [0.2.1] - 2024-10-13

### Fixed
- **Import Error Fix** - Fixed circular import issue in CLI
  - Exported `EvolutionConfig` from `kaggler.core` module
  - Added lazy imports in CLI to prevent circular dependencies
  - Fixed `kagglerboze` command startup errors

### Changed
- **Onboarding Improvements** - Updated default competition to Titanic
  - Changed quick start examples from `medical-text-extraction` to `titanic`
  - Updated all `.claude` command templates (compete, analyze, optimize, submit)
  - Added Kaggle API setup instructions to README
  - Updated `kagglerboze install-claude` success message

### Documentation
- Added comprehensive Kaggle API setup guide
- Updated installation flow with 3 clear steps
- Improved onboarding documentation for new users
- Updated both English and Japanese READMEs

## [0.2.0] - 2024-10-13

### Added
- **Medical Domain Support** - Medical entity extraction with 96% accuracy
  - Symptom extraction (fever, pain, etc.)
  - Medication parsing (dosage, frequency)
  - Lab value interpretation
  - Diagnosis extraction
- **Finance Domain Support** - Financial analysis with 92% accuracy
  - Stock analysis (PER, PBR, ROE metrics)
  - Sentiment analysis (market sentiment detection)
  - Technical analysis (moving averages, RSI)
  - Risk analysis (volatility, beta calculations)
- **GEPA Core Engine** - Genetic-Pareto Reflective Evolution
  - Evolutionary prompt optimization
  - Pareto-optimal multi-objective optimization
  - Reflection-based continuous improvement
  - Mutation and crossover operators
- **Kaggle API Wrapper** - Seamless competition integration
  - Competition data download
  - Submission management
  - Leaderboard tracking
- **Claude Code Integration** - AI-powered development workflow
  - Custom slash commands
  - Autonomous agent pipeline
  - GitHub OS integration

### Documentation
- Comprehensive README with quick start guide
- Contributing guidelines
- Multi-language documentation (EN, JA, ZH)
- Domain-specific examples
- API reference documentation

### Infrastructure
- GitHub Actions CI/CD pipeline
- Automated testing with pytest
- Code coverage tracking
- Type checking with mypy
- Code formatting with black and isort

## [0.1.0] - 2024-10-01

### Added
- Initial project structure
- Basic GEPA framework
- Core evolution engine
- Project documentation

---

[0.2.0]: https://github.com/StarBoze/kagglerboze/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/StarBoze/kagglerboze/releases/tag/v0.1.0
