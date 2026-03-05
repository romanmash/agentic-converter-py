# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2026-03-05

### Added

- Configurable LLM hyperparameters (`temperature`, `max_tokens`, `top_p`, `top_k`) through `config.json` and `.env` override
- Added nested parameters tailored specifically for `converter` and `reviewer` nodes out of the box.

## [1.1.0] - 2026-03-05

### Added

- Conversion report (`report.md`) generated alongside each `ci.yml`
- Unified report format: status, iterations, confidence level, timestamp
- Iteration history table tracking each convert/review action
- Manual Verification Checklist (11 items) for common Jenkins→GHA issues
- Confidence level: HIGH (≤2 iter) / MEDIUM (3-4 iter) / LOW (max iter)
- Embedded generated YAML in report for self-contained reference
- Reviewer feedback integrated as Comment column in iteration history table
- `IterationRecord` model for tracking pipeline history

## [1.0.0] - 2026-03-05

### Added

- Agentic converter↔reviewer loop for Jenkinsfile → GitHub Actions YAML
- Dual-mode CLI (positional + named options) with `--help`, `--version`, `--verbose`
- Batch directory processing with recursive Jenkinsfile discovery
- Output directory mirroring (preserves input folder structure)
- Three-layer configuration: `config.json` → `.env` → CLI args
- LLM integration via OpenAI SDK (LM Studio local server)
- Converter system prompt with Jenkins→GHA mapping rules
- Reviewer system prompt with evaluation checklist and structured verdict
- Exit codes: 0 (all approved), 1 (fatal error), 2 (partial success)
- Unit tests with mocked LLM client (pytest, runs offline)
- Project documentation: README, CHANGELOG, CONTRIBUTING, AGENTS, LICENSE (MIT)
- Spec Kit documents: constitution, spec, plan, tasks
