"""
Main test orchestrator - runs automated test sessions with multiple personas.
"""
import asyncio
import argparse
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import TestConfig
from .harness import ServerManager, TestClient, SessionRecorder
from .personas import PersonaRegistry, Persona
from .agents import PlayerAgent, HybridStrategy, RuleBasedStrategy, LLMStrategy
from .reports import SessionAnalyzer, ImprovementTracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Orchestrates automated test sessions."""

    def __init__(self, config: Optional[TestConfig] = None):
        self.config = config or TestConfig()
        self.server = ServerManager(
            host=self.config.server_host,
            port=self.config.server_port,
            startup_timeout=self.config.server_startup_timeout,
        )
        self.sessions_run: list[str] = []

    async def run_session(
        self,
        persona: Persona,
        strategy_type: str = "hybrid",
    ) -> SessionRecorder:
        """Run a single test session with the given persona."""
        session_id = f"{persona.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        logger.info("=" * 60)
        logger.info("Starting session: %s", session_id)
        logger.info("Persona: %s", persona.name)
        logger.info("Description: %s", persona.description)
        logger.info("=" * 60)

        # Create components
        client = TestClient(
            base_url=self.config.base_url,
            timeout=self.config.request_timeout,
        )

        recorder = SessionRecorder(
            output_dir=self.config.output_dir,
            session_id=session_id,
            persona_name=persona.name,
            persona_description=persona.description,
        )

        # Create strategy
        if strategy_type == "llm":
            strategy = LLMStrategy(
                model=self.config.agent_model,
                temperature=self.config.agent_temperature,
            )
        elif strategy_type == "rules":
            strategy = RuleBasedStrategy()
        else:
            strategy = HybridStrategy(
                model=self.config.agent_model,
                temperature=self.config.agent_temperature,
            )

        # Create and run agent
        agent = PlayerAgent(
            persona=persona,
            client=client,
            recorder=recorder,
            config=self.config,
            strategy=strategy,
        )

        await agent.play_session()
        self.sessions_run.append(session_id)

        logger.info("Session completed: %s", session_id)
        logger.info("Turns: %d, Ending: %s", recorder.record.total_turns, recorder.record.ending_reached)

        return recorder

    async def run_all_personas(
        self,
        strategy_type: str = "hybrid",
        parallel: bool = False,
    ) -> list[SessionRecorder]:
        """Run sessions for all registered personas."""
        personas = PersonaRegistry.get_all()

        logger.info("Running %d personas: %s", len(personas), [p.name for p in personas])

        if parallel:
            # Run all sessions in parallel
            tasks = [
                self.run_session(persona, strategy_type)
                for persona in personas
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions
            recorders = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error("Persona %s failed: %s", personas[i].name, result)
                else:
                    recorders.append(result)
            return recorders
        else:
            # Run sequentially
            recorders = []
            for persona in personas:
                try:
                    recorder = await self.run_session(persona, strategy_type)
                    recorders.append(recorder)
                except Exception as e:
                    logger.error("Persona %s failed: %s", persona.name, e)
            return recorders

    async def run_specific_personas(
        self,
        persona_names: list[str],
        strategy_type: str = "hybrid",
    ) -> list[SessionRecorder]:
        """Run sessions for specific personas by name."""
        recorders = []

        for name in persona_names:
            persona = PersonaRegistry.get(name)
            if persona is None:
                logger.warning("Unknown persona: %s", name)
                continue

            try:
                recorder = await self.run_session(persona, strategy_type)
                recorders.append(recorder)
            except Exception as e:
                logger.error("Persona %s failed: %s", name, e)

        return recorders

    def analyze_sessions(self, generate_llm_suggestions: bool = False) -> tuple:
        """Analyze all recorded sessions and generate improvements."""
        analyzer = SessionAnalyzer(self.config.output_dir)
        analyzer.load_sessions()

        report = analyzer.analyze()
        analyzer.save_report(report)

        tracker = ImprovementTracker(self.config.output_dir, model=self.config.agent_model)
        tracker.analyze_and_suggest(report)

        if generate_llm_suggestions:
            asyncio.get_event_loop().run_until_complete(
                tracker.generate_llm_suggestions(report)
            )

        tracker.save_improvements()

        return report, tracker.improvements

    async def run_full_test_suite(
        self,
        personas: Optional[list[str]] = None,
        strategy_type: str = "hybrid",
        analyze: bool = True,
        llm_suggestions: bool = False,
    ) -> dict:
        """Run the complete test suite with server management."""
        results = {
            "sessions": [],
            "analysis": None,
            "improvements": [],
            "success": False,
        }

        async with self.server.running():
            logger.info("Server running at %s", self.server.base_url)

            # Run sessions
            if personas:
                recorders = await self.run_specific_personas(personas, strategy_type)
            else:
                recorders = await self.run_all_personas(strategy_type)

            results["sessions"] = [r.record.session_id for r in recorders]

            # Analyze if requested
            if analyze and recorders:
                report, improvements = self.analyze_sessions(llm_suggestions)
                results["analysis"] = {
                    "sessions_analyzed": report.sessions_analyzed,
                    "endings_reached": report.endings_reached,
                    "total_errors": report.total_errors,
                }
                results["improvements"] = [i.title for i in improvements]

            results["success"] = True

        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic Testing Framework for Keepers Vigil",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all personas with hybrid strategy
  python -m testing.runner

  # Run specific personas
  python -m testing.runner --personas methodical_explorer speedrunner

  # Run with only LLM-based decisions
  python -m testing.runner --strategy llm

  # Run with rule-based decisions only (faster, no API calls for decisions)
  python -m testing.runner --strategy rules

  # Skip analysis
  python -m testing.runner --no-analyze

  # List available personas
  python -m testing.runner --list-personas
""",
    )

    parser.add_argument(
        "--personas",
        nargs="+",
        help="Specific personas to run (default: all)",
    )
    parser.add_argument(
        "--strategy",
        choices=["hybrid", "llm", "rules"],
        default="hybrid",
        help="Decision strategy (default: hybrid)",
    )
    parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Skip post-session analysis",
    )
    parser.add_argument(
        "--llm-suggestions",
        action="store_true",
        help="Use LLM to generate additional improvement suggestions",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for session records",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        help="Override max turns per session",
    )
    parser.add_argument(
        "--list-personas",
        action="store_true",
        help="List available personas and exit",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze existing sessions, don't run new ones",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # List personas
    if args.list_personas:
        print("\nAvailable Personas:")
        print("-" * 60)
        for persona in PersonaRegistry.get_all():
            print(f"\n{persona.name}")
            print(f"  {persona.description}")
            print(f"  Max turns: {persona.max_turns}")
        return 0

    # Build config
    config = TestConfig(
        server_host=args.host,
        server_port=args.port,
    )
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.max_turns:
        config.max_turns = args.max_turns

    runner = TestRunner(config)

    # Analyze only mode
    if args.analyze_only:
        print("\nAnalyzing existing sessions...")
        report, improvements = runner.analyze_sessions(args.llm_suggestions)
        print(f"\nAnalysis complete:")
        print(f"  Sessions analyzed: {report.sessions_analyzed}")
        print(f"  Endings reached: {report.endings_reached}")
        print(f"  Total errors: {report.total_errors}")
        print(f"  Improvements suggested: {len(improvements)}")
        print(f"\nResults saved to: {config.output_dir / 'summary'}")
        return 0

    # Run test suite
    print("\n" + "=" * 60)
    print("AGENTIC TESTING FRAMEWORK")
    print("Keepers Vigil - Automated Play Sessions")
    print("=" * 60)

    try:
        results = asyncio.run(
            runner.run_full_test_suite(
                personas=args.personas,
                strategy_type=args.strategy,
                analyze=not args.no_analyze,
                llm_suggestions=args.llm_suggestions,
            )
        )

        print("\n" + "=" * 60)
        print("TEST SUITE COMPLETE")
        print("=" * 60)
        print(f"\nSessions run: {len(results['sessions'])}")

        if results["analysis"]:
            print(f"\nAnalysis:")
            print(f"  Sessions analyzed: {results['analysis']['sessions_analyzed']}")
            print(f"  Endings reached: {results['analysis']['endings_reached']}")
            print(f"  Total errors: {results['analysis']['total_errors']}")

        if results["improvements"]:
            print(f"\nImprovements suggested: {len(results['improvements'])}")
            for imp in results["improvements"][:5]:
                print(f"  - {imp}")
            if len(results["improvements"]) > 5:
                print(f"  ... and {len(results['improvements']) - 5} more")

        print(f"\nResults saved to: {config.output_dir}")

        return 0 if results["success"] else 1

    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user")
        return 130
    except Exception as e:
        logger.exception("Test suite failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
