# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2024-10-13

### Fixed
- **Package Distribution** - Fixed MANIFEST.in to include correct documentation folder
  - Changed from `docs/` (private notes) to `doc/` (public documentation)
  - Ensures only user-facing documentation is included in PyPI package
  - Private development notes now properly excluded from distribution

## [0.2.3] - 2024-10-13

### Changed
- **Documentation Clarity** - Improved documentation to clearly distinguish Kaggle competition features from GEPA technology demos
  - Updated `doc/QUICK_START.md` to use Titanic competition as primary example
  - Replaced `medical-text-extraction` examples with actual Kaggle competition workflow using XGBoostGA/LightGBMGA
  - Added clear disclaimers in `doc/MEDICAL_DOMAIN.md` identifying it as GEPA technology demonstration
  - Added clear disclaimers in `doc/FINANCE_DOMAIN.md` identifying it as GEPA technology demonstration
  - Reorganized examples to separate Kaggle competition use cases from custom domain applications

### Documentation
- Clarified that Medical/Finance domain modules showcase GEPA's prompt optimization capabilities for custom NLP tasks
- Directed users to tabular modules (XGBoostGA, LightGBMGA) for Kaggle competition workflows
- Added "Advanced: GEPA for Custom Domains" section to clearly mark technology demonstration examples
- Improved user onboarding by focusing on Kaggle competition examples first

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
