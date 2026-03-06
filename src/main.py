"""AgenticConverter CLI entry point.

ALL file I/O lives here — agents receive and return in-memory data only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from src.config.manager import load_config, load_project_version, merge_with_cli
from src.graph.pipeline import PipelineStatus, run_pipeline
from src.llm.client import LLMClient
from src.report.generator import generate_report


def _load_prompt(prompt_name: str) -> str:
    """Load a system prompt from src/prompts."""
    prompt_path = Path(__file__).resolve().parent / "prompts" / f"{prompt_name}.md"
    return prompt_path.read_text(encoding="utf-8")


def build_parser(version: str) -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Args:
        version: Application version string from pyproject.toml.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="agentic-converter",
        description="Convert Jenkinsfiles to GitHub Actions workflow YAML using a local LLM.",
        epilog=(
            "Examples:\n"
            "  uv run python -m src.main .data/input/1/Jenkinsfile\n"
            "  uv run python -m src.main .data/input/ -n 3 -v\n"
            "  uv run python -m src.main --version"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        help="Jenkinsfile or directory containing Jenkinsfiles",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        metavar="DIR",
        default=None,
        help="Output directory (default: from config/config.json)",
    )
    parser.add_argument(
        "-n",
        "--max-iterations",
        type=int,
        metavar="N",
        default=None,
        help="Max converter↔reviewer iterations (default: from config/config.json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=None,
        help="Enable verbose output",
    )
    return parser


def main() -> None:
    """Main entry point for AgenticConverter."""
    # Load version from pyproject.toml for --version
    try:
        version = load_project_version()
    except Exception as e:
        print(f"❌ Error: failed to load project version: {e}", file=sys.stderr)
        sys.exit(1)
    parser = build_parser(version)
    args = parser.parse_args()

    # Load runtime configuration after parsing arguments
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error: failed to load configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Merge CLI overrides into config
    config = merge_with_cli(config, vars(args))

    # Validate input path
    input_path = Path(args.path)
    if not input_path.exists():
        print(f"❌ Error: path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Create LLM client
    try:
        client = LLMClient(config)
    except Exception as e:
        print(f"❌ Error: failed to initialize LLM client: {e}", file=sys.stderr)
        sys.exit(1)

    # Load prompts (I/O boundary)
    try:
        converter_prompt = _load_prompt("converter")
        reviewer_prompt = _load_prompt("reviewer")
    except Exception as e:
        print(f"❌ Error: failed to load prompts: {e}", file=sys.stderr)
        sys.exit(1)

    # Discover Jenkinsfiles
    if input_path.is_file():
        jenkinsfiles = [input_path]
    else:
        jenkinsfiles = sorted(input_path.rglob("Jenkinsfile"))
        if not jenkinsfiles:
            print(f"❌ Error: no Jenkinsfiles found in {input_path}", file=sys.stderr)
            sys.exit(1)

    if config.verbose:
        print(f"📂 Found {len(jenkinsfiles)} Jenkinsfile(s)")

    # Process each Jenkinsfile
    results: list[PipelineStatus] = []

    for jf_path in jenkinsfiles:
        if config.verbose:
            print(f"\n🔄 Processing: {jf_path}")

        # Read Jenkinsfile (I/O here only)
        jenkinsfile_content = jf_path.read_text(encoding="utf-8")

        # Run the full agentic loop
        try:
            state = run_pipeline(
                jenkinsfile=jenkinsfile_content,
                client=client,
                converter_params=config.llm.converter,
                reviewer_params=config.llm.reviewer,
                converter_prompt=converter_prompt,
                reviewer_prompt=reviewer_prompt,
                max_iterations=config.max_iterations,
                progress_callback=print if config.verbose else None,
            )
        except Exception as e:
            print(f"❌ Error converting {jf_path}: {e}", file=sys.stderr)
            results.append(PipelineStatus.ERROR)
            continue

        # Validate YAML
        try:
            yaml.safe_load(state.workflow_yaml)
        except yaml.YAMLError as e:
            print(f"⚠️  Warning: generated YAML is not valid: {e}")

        # Compute output path (mirror input structure)
        if input_path.is_file():
            relative = jf_path.parent.relative_to(jf_path.parent.parent)
        else:
            relative = jf_path.parent.relative_to(input_path)

        output_dir = Path(config.output_dir) / relative
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "ci.yml"

        # Write output (I/O here only)
        output_file.write_text(state.workflow_yaml, encoding="utf-8")

        # Generate and write conversion report
        report_md = generate_report(
            state=state,
            source_path=str(jf_path),
            output_path=str(output_file),
            max_iterations=config.max_iterations,
        )
        report_file = output_dir / "report.md"
        report_file.write_text(report_md, encoding="utf-8")

        status_emoji = "✅" if state.status == PipelineStatus.APPROVED else "⚠️"
        print(f"  {status_emoji} {output_file} ({state.status.value}, {state.iteration} iteration(s))")

        results.append(state.status)

    # Final summary
    print(f"\n{'='*50}")
    print(f"Processed {len(results)} file(s)")

    approved = sum(1 for r in results if r == PipelineStatus.APPROVED)
    max_iterations = sum(1 for r in results if r == PipelineStatus.MAX_ITERATIONS)
    errors = sum(1 for r in results if r == PipelineStatus.ERROR)

    if approved == len(results):
        print(f"✅ {len(results)} file(s) converted successfully")
        sys.exit(0)

    if errors == len(results):
        print("❌ All conversions failed")
        sys.exit(1)

    print(
        f"⚠️  {approved} approved, {max_iterations} max-iterations, {errors} failed"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
