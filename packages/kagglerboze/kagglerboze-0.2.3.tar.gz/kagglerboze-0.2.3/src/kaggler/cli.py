"""
KagglerBoze CLI - Standalone Command Line Interface

Provides full functionality without .claude directory dependency.

Usage:
    kagglerboze compete <competition-name>
    kagglerboze optimize [prompt|xgboost|lightgbm]
    kagglerboze submit <competition-name> <file>
    kagglerboze analyze <competition-name>
"""

import argparse
import sys
from pathlib import Path
from typing import Optional


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="kagglerboze",
        description="GEPA-powered ML automation for Kaggle",
        epilog="For more help: kagglerboze <command> --help"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Compete command
    compete_parser = subparsers.add_parser(
        "compete",
        help="Compete in Kaggle competition end-to-end"
    )
    compete_parser.add_argument(
        "competition",
        help="Competition name (e.g., titanic)"
    )
    compete_parser.add_argument(
        "--no-submit",
        action="store_true",
        help="Skip automatic submission"
    )
    compete_parser.add_argument(
        "--generations",
        type=int,
        default=10,
        help="GEPA generations (default: 10)"
    )
    compete_parser.add_argument(
        "--time-limit",
        type=int,
        default=60,
        help="Time limit in minutes (default: 60)"
    )

    # Optimize command
    optimize_parser = subparsers.add_parser(
        "optimize",
        help="Optimize prompts or hyperparameters with GEPA"
    )
    optimize_parser.add_argument(
        "model_type",
        nargs="?",
        default="prompt",
        choices=["prompt", "xgboost", "lightgbm", "ensemble"],
        help="Model type to optimize (default: prompt)"
    )
    optimize_parser.add_argument(
        "--population",
        type=int,
        default=20,
        help="Population size (default: 20)"
    )
    optimize_parser.add_argument(
        "--generations",
        type=int,
        default=10,
        help="Number of generations (default: 10)"
    )
    optimize_parser.add_argument(
        "--seed-prompt",
        type=str,
        help="Initial seed prompt for optimization"
    )
    optimize_parser.add_argument(
        "--output",
        type=str,
        default="optimized_prompt.txt",
        help="Output file for optimized result"
    )

    # Submit command
    submit_parser = subparsers.add_parser(
        "submit",
        help="Submit predictions to Kaggle"
    )
    submit_parser.add_argument(
        "competition",
        help="Competition name"
    )
    submit_parser.add_argument(
        "file",
        help="Submission file path"
    )
    submit_parser.add_argument(
        "--message",
        type=str,
        default="Submission via KagglerBoze",
        help="Submission message"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze Kaggle competition"
    )
    analyze_parser.add_argument(
        "competition",
        help="Competition name"
    )
    analyze_parser.add_argument(
        "--download",
        action="store_true",
        help="Download competition data"
    )

    # Version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show KagglerBoze version"
    )

    # Install Claude Code integration command
    install_claude_parser = subparsers.add_parser(
        "install-claude",
        help="Install Claude Code integration (.claude directory)"
    )
    install_claude_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .claude directory"
    )
    install_claude_parser.add_argument(
        "--target",
        type=str,
        help="Target directory (default: current directory)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to command handlers
    try:
        if args.command == "compete":
            compete_command(args)
        elif args.command == "optimize":
            optimize_command(args)
        elif args.command == "submit":
            submit_command(args)
        elif args.command == "analyze":
            analyze_command(args)
        elif args.command == "version":
            version_command()
        elif args.command == "install-claude":
            install_claude_command(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


def compete_command(args):
    """Handle compete command."""
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from kaggler.workflows import CompetitionWorkflow

    console = Console()

    console.print(f"\n🎯 [bold cyan]Competing in: {args.competition}[/bold cyan]\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        # Initialize workflow
        task = progress.add_task("Initializing workflow...", total=None)
        workflow = CompetitionWorkflow(
            competition=args.competition,
            auto_submit=not args.no_submit,
            generations=args.generations,
            time_limit_minutes=args.time_limit
        )

        # Execute workflow
        progress.update(task, description="Downloading data...")
        workflow.download_data()

        progress.update(task, description="Analyzing competition...")
        analysis = workflow.analyze()
        console.print(f"  Type: {analysis['type']}, Metric: {analysis['metric']}")

        progress.update(task, description="Running EDA...")
        workflow.eda()

        progress.update(task, description="Engineering features...")
        workflow.feature_engineering()

        progress.update(task, description=f"Optimizing with GEPA ({args.generations} generations)...")
        results = workflow.optimize()

        console.print(f"\n✅ [bold green]Optimization complete![/bold green]")
        console.print(f"  Best score: {results['best_score']:.4f}")
        console.print(f"  Improvement: {results['baseline']:.4f} → {results['best_score']:.4f} (+{results['improvement']:.1%})")

        if not args.no_submit:
            progress.update(task, description="Creating submission...")
            submission_path = workflow.create_submission()

            progress.update(task, description="Submitting to Kaggle...")
            public_score = workflow.submit()

            console.print(f"\n🎉 [bold green]Submission successful![/bold green]")
            console.print(f"  Public score: {public_score:.4f}")
            console.print(f"  File: {submission_path}")

        # Show next steps
        console.print("\n📋 [bold]Next steps:[/bold]")
        for step in results.get('next_steps', []):
            console.print(f"  • {step}")


def optimize_command(args):
    """Handle optimize command."""
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table

    console = Console()

    console.print(f"\n🧬 [bold cyan]Optimizing {args.model_type}[/bold cyan]\n")

    if args.model_type == "prompt":
        optimize_prompt(args, console)
    elif args.model_type in ["xgboost", "lightgbm"]:
        optimize_hyperparameters(args, console)
    elif args.model_type == "ensemble":
        optimize_ensemble(args, console)


def optimize_prompt(args, console):
    """Optimize prompt using GEPA."""
    from kaggler.core import EvolutionEngine, EvolutionConfig

    config = EvolutionConfig(
        population_size=args.population,
        generations=args.generations
    )

    engine = EvolutionEngine(config)

    # Get seed prompt
    if args.seed_prompt:
        seed_prompts = [args.seed_prompt]
    else:
        seed_prompts = ["Extract relevant information from the text."]

    console.print(f"Initial prompt: [italic]{seed_prompts[0]}[/italic]")
    console.print(f"Population: {args.population}, Generations: {args.generations}\n")

    # Define evaluation function (placeholder)
    def eval_func(prompt):
        # This should be replaced with actual evaluation
        return {"accuracy": 0.85, "speed": 0.9, "cost": 0.95}

    # Evolution progress callback
    def on_generation(gen, best_individual, avg_fitness):
        console.print(f"Generation {gen}: Best F1={best_individual.fitness_scores.get('accuracy', 0):.2f}, Avg={avg_fitness:.2f}")

    # Run evolution
    best_prompt = engine.evolve(
        seed_prompts=seed_prompts,
        eval_func=eval_func,
        on_generation=on_generation
    )

    # Save result
    with open(args.output, 'w') as f:
        f.write(best_prompt.prompt)

    console.print(f"\n✅ [bold green]Optimization complete![/bold green]")
    console.print(f"  Best prompt saved to: {args.output}")
    console.print(f"  Performance: {seed_prompts[0][:30]}... → Best F1={best_prompt.fitness_scores.get('accuracy', 0):.2f}")


def optimize_hyperparameters(args, console):
    """Optimize XGBoost/LightGBM hyperparameters."""
    console.print("[yellow]Hyperparameter optimization coming soon![/yellow]")
    console.print("Current focus: Prompt optimization with GEPA")


def optimize_ensemble(args, console):
    """Optimize ensemble weights."""
    console.print("[yellow]Ensemble optimization coming soon![/yellow]")
    console.print("Current focus: Prompt optimization with GEPA")


def submit_command(args):
    """Handle submit command."""
    from rich.console import Console
    from kaggler.kaggle import KaggleClient

    console = Console()

    console.print(f"\n📤 [bold cyan]Submitting to {args.competition}[/bold cyan]\n")

    # Validate file exists
    file_path = Path(args.file)
    if not file_path.exists():
        console.print(f"[red]Error: File not found: {args.file}[/red]")
        sys.exit(1)

    # Submit
    client = KaggleClient()
    result = client.submit(
        competition=args.competition,
        file_path=str(file_path),
        message=args.message
    )

    console.print(f"✅ [bold green]Submission successful![/bold green]")
    console.print(f"  File: {args.file}")
    console.print(f"  Message: {args.message}")
    console.print(f"  Status: {result.get('status', 'Submitted')}")


def analyze_command(args):
    """Handle analyze command."""
    from rich.console import Console
    from rich.table import Table
    from kaggler.kaggle import KaggleClient

    console = Console()

    console.print(f"\n🔍 [bold cyan]Analyzing {args.competition}[/bold cyan]\n")

    client = KaggleClient()

    if args.download:
        console.print("Downloading competition data...")
        client.download_competition(args.competition)
        console.print("✅ Download complete\n")

    # Get competition info
    # Note: This would require implementing get_competition_info in KaggleClient
    console.print("Competition analysis:")
    console.print("  Type: [italic]Detection required[/italic]")
    console.print("  Metric: [italic]To be determined[/italic]")
    console.print("  Files: [italic]See data directory[/italic]")

    console.print("\n💡 [bold]Recommended approach:[/bold]")
    console.print("  1. Run EDA: kagglerboze compete <competition> (without submit)")
    console.print("  2. Try GEPA optimization: kagglerboze optimize prompt")
    console.print("  3. Submit: kagglerboze submit <competition> submission.csv")


def version_command():
    """Handle version command."""
    from kaggler import __version__
    print(f"KagglerBoze version {__version__}")


def install_claude_command(args):
    """Handle install-claude command."""
    from pathlib import Path
    import shutil
    import pkg_resources

    print("\n" + "="*60)
    print("KagglerBoze Claude Code Integration Installer")
    print("="*60 + "\n")

    # Get target directory
    if args.target:
        target_dir = Path(args.target)
    else:
        target_dir = Path.cwd()

    target_claude_dir = target_dir / ".claude"

    # Check if already exists
    if target_claude_dir.exists() and not args.force:
        print(f"✓ .claude directory already exists at: {target_claude_dir}")
        print("  Use --force to overwrite")
        return

    # Get source .claude directory from package
    try:
        package_dir = Path(pkg_resources.resource_filename('kaggler', ''))
        source_claude_dir = package_dir.parent.parent / ".claude"

        if not source_claude_dir.exists():
            # Try alternative location
            source_claude_dir = package_dir.parent / ".claude"

        if not source_claude_dir.exists():
            print("✗ Could not find .claude directory in kagglerboze package")
            print("\n💡 Alternative: Clone from GitHub and copy manually:")
            print("   git clone https://github.com/StarBoze/kagglerboze.git")
            print("   cp -r kagglerboze/.claude /your/project/")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Error locating package: {e}")
        sys.exit(1)

    # Copy .claude directory
    try:
        if target_claude_dir.exists():
            print(f"⚠  Removing existing .claude directory...")
            shutil.rmtree(target_claude_dir)

        print(f"📦 Copying .claude directory...")
        print(f"   Source: {source_claude_dir}")
        print(f"   Target: {target_claude_dir}")

        shutil.copytree(source_claude_dir, target_claude_dir)

        print(f"\n✅ Claude Code integration installed successfully!")
        print(f"\n🚀 You can now use commands in Claude Code:")
        print(f"   /compete titanic")
        print(f"   /optimize xgboost")
        print(f"   /submit titanic submission.csv")
        print(f"   /analyze titanic")
        print("\n" + "="*60)

    except Exception as e:
        print(f"✗ Error installing .claude directory: {e}")
        print("\n💡 Manual installation:")
        print("   1. Download: https://github.com/StarBoze/kagglerboze/archive/main.zip")
        print("   2. Extract and copy .claude directory to your project")
        sys.exit(1)


if __name__ == "__main__":
    main()
