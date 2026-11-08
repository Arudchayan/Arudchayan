# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-08

### Added

- Deterministic level-100 singles battle engine with STAB, type effectiveness, critical hits, accuracy, damage rolls, stat stages, status conditions, hazards, and a fixed item/ability set.
- Agent zoo: random, greedy, heuristic, expectimax search, linear and MLP behaviour cloning, DAgger, REINFORCE, hybrid, and tabular Q baselines.
- Cloneable SplitMix64 random number generator for exact replay and reproducible search.
- Seeded evaluation with side-swapped matches, bootstrap confidence intervals, and Bradley-Terry ratings.
- Training and experiment utilities for search distillation, DAgger, REINFORCE, and tabular baselines.
- Reproducible experiment workflow with pinned seeds, saved configurations, and report generation.
- CLI workflow: `python -m pokerl bench`, `python -m pokerl demo --seed 1`, `python -m pokerl train`, `python -m pokerl generalize`, and `python -m pokerl report`.
- Zero runtime dependencies, with optional `dev` and `nn` extras.
- PEP 621 packaging, Make targets, pre-commit hooks, Docker and devcontainer environments.
- Continuous integration for tests, linting, smoke benchmarks, coverage, and package builds.
- Research-facing documentation: changelog, roadmap, security policy, code of conduct, citation metadata, issue forms, and a pull request checklist.

[Unreleased]: https://github.com/Arudchayan/Arudchayan/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Arudchayan/Arudchayan/releases/tag/v1.0.0
