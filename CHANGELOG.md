# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
