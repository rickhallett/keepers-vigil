"""
Session analysis and cross-session reporting.
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from collections import Counter

from ..harness.recorder import SessionRecord

logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """A pattern of errors found across sessions."""

    error_type: str
    count: int
    example_messages: list[str] = field(default_factory=list)
    affected_sessions: list[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class AnalysisReport:
    """Cross-session analysis report."""

    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    sessions_analyzed: int = 0

    # Coverage metrics
    endings_reached: dict[str, int] = field(default_factory=dict)
    rooms_coverage: dict[str, int] = field(default_factory=dict)
    flags_coverage: dict[str, int] = field(default_factory=dict)
    commands_usage: dict[str, int] = field(default_factory=dict)

    # Performance metrics
    average_turns_to_ending: float = 0.0
    average_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0

    # Error analysis
    total_errors: int = 0
    error_patterns: list[dict] = field(default_factory=list)

    # Persona performance
    persona_outcomes: dict[str, dict] = field(default_factory=dict)

    # UX insights
    stuck_sessions: int = 0
    incomplete_sessions: int = 0
    common_failure_points: list[str] = field(default_factory=list)


class SessionAnalyzer:
    """Analyzes test sessions to find patterns and issues."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.sessions: list[SessionRecord] = []

    def load_sessions(self, session_dirs: Optional[list[Path]] = None) -> int:
        """Load session records from disk."""
        if session_dirs is None:
            # Load all sessions from output directory
            session_dirs = [
                d for d in self.output_dir.iterdir()
                if d.is_dir() and d.name != "summary"
            ]

        self.sessions = []
        for session_dir in session_dirs:
            json_file = session_dir / "session.json"
            if json_file.exists():
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                        record = SessionRecord(**data)
                        self.sessions.append(record)
                except Exception as e:
                    logger.warning("Failed to load session %s: %s", session_dir, e)

        logger.info("Loaded %d sessions", len(self.sessions))
        return len(self.sessions)

    def analyze(self) -> AnalysisReport:
        """Perform cross-session analysis."""
        if not self.sessions:
            return AnalysisReport()

        report = AnalysisReport(sessions_analyzed=len(self.sessions))

        # Analyze endings
        report.endings_reached = self._analyze_endings()

        # Analyze coverage
        report.rooms_coverage = self._analyze_room_coverage()
        report.flags_coverage = self._analyze_flag_coverage()
        report.commands_usage = self._analyze_command_usage()

        # Performance metrics
        report.average_turns_to_ending = self._calculate_average_turns()
        report.average_response_time_ms = self._calculate_average_response_time()
        report.max_response_time_ms = self._calculate_max_response_time()

        # Error analysis
        report.total_errors = sum(len(s.errors) for s in self.sessions)
        report.error_patterns = self._find_error_patterns()

        # Persona outcomes
        report.persona_outcomes = self._analyze_persona_outcomes()

        # UX insights
        report.stuck_sessions = self._count_stuck_sessions()
        report.incomplete_sessions = self._count_incomplete_sessions()
        report.common_failure_points = self._find_failure_points()

        return report

    def _analyze_endings(self) -> dict[str, int]:
        """Count endings reached across sessions."""
        endings = Counter()
        for session in self.sessions:
            ending = session.ending_reached or "none"
            endings[ending] += 1
        return dict(endings)

    def _analyze_room_coverage(self) -> dict[str, int]:
        """Count room visits across sessions."""
        rooms = Counter()
        for session in self.sessions:
            for room in session.rooms_visited:
                rooms[room] += 1
        return dict(rooms)

    def _analyze_flag_coverage(self) -> dict[str, int]:
        """Count flag discoveries across sessions."""
        flags = Counter()
        for session in self.sessions:
            for flag in session.flags_discovered:
                flags[flag] += 1
        return dict(flags)

    def _analyze_command_usage(self) -> dict[str, int]:
        """Aggregate command usage across sessions."""
        commands = Counter()
        for session in self.sessions:
            for cmd, count in session.commands_used.items():
                commands[cmd] += count
        return dict(commands)

    def _calculate_average_turns(self) -> float:
        """Calculate average turns to reach ending."""
        completed = [s for s in self.sessions if s.ending_reached]
        if not completed:
            return 0.0
        return sum(s.total_turns for s in completed) / len(completed)

    def _calculate_average_response_time(self) -> float:
        """Calculate average API response time."""
        times = [s.average_response_time_ms for s in self.sessions if s.average_response_time_ms > 0]
        if not times:
            return 0.0
        return sum(times) / len(times)

    def _calculate_max_response_time(self) -> float:
        """Find maximum response time."""
        max_time = 0.0
        for session in self.sessions:
            for interaction in session.interactions:
                resp_time = interaction.get("response", {}).get("elapsed_ms", 0)
                max_time = max(max_time, resp_time)
        return max_time

    def _find_error_patterns(self) -> list[dict]:
        """Find patterns in errors across sessions."""
        error_types = Counter()
        error_examples: dict[str, list] = {}
        error_sessions: dict[str, list] = {}

        for session in self.sessions:
            for error in session.errors:
                err_type = error.get("type", "unknown")
                error_types[err_type] += 1

                if err_type not in error_examples:
                    error_examples[err_type] = []
                    error_sessions[err_type] = []

                if len(error_examples[err_type]) < 3:
                    error_examples[err_type].append(error.get("message", ""))

                if session.session_id not in error_sessions[err_type]:
                    error_sessions[err_type].append(session.session_id)

        patterns = []
        for err_type, count in error_types.items():
            severity = "low"
            if count > len(self.sessions) * 0.5:
                severity = "critical"
            elif count > len(self.sessions) * 0.25:
                severity = "high"
            elif count > len(self.sessions) * 0.1:
                severity = "medium"

            pattern = ErrorPattern(
                error_type=err_type,
                count=count,
                example_messages=error_examples.get(err_type, []),
                affected_sessions=error_sessions.get(err_type, []),
                severity=severity,
            )
            patterns.append(asdict(pattern))

        return sorted(patterns, key=lambda x: x["count"], reverse=True)

    def _analyze_persona_outcomes(self) -> dict[str, dict]:
        """Analyze outcomes by persona."""
        persona_data: dict[str, dict] = {}

        for session in self.sessions:
            persona = session.persona_name
            if persona not in persona_data:
                persona_data[persona] = {
                    "sessions": 0,
                    "completed": 0,
                    "endings": {},
                    "avg_turns": [],
                    "errors": 0,
                    "rooms_visited": set(),
                    "flags_found": set(),
                }

            data = persona_data[persona]
            data["sessions"] += 1
            data["errors"] += len(session.errors)
            data["avg_turns"].append(session.total_turns)
            data["rooms_visited"].update(session.rooms_visited)
            data["flags_found"].update(session.flags_discovered)

            if session.ending_reached:
                data["completed"] += 1
                ending = session.ending_reached
                data["endings"][ending] = data["endings"].get(ending, 0) + 1

        # Calculate averages and convert sets to lists
        for persona, data in persona_data.items():
            if data["avg_turns"]:
                data["avg_turns"] = sum(data["avg_turns"]) / len(data["avg_turns"])
            else:
                data["avg_turns"] = 0
            data["completion_rate"] = data["completed"] / data["sessions"] if data["sessions"] > 0 else 0
            data["rooms_visited"] = list(data["rooms_visited"])
            data["flags_found"] = list(data["flags_found"])

        return persona_data

    def _count_stuck_sessions(self) -> int:
        """Count sessions that got stuck."""
        # Session is stuck if it has many turns but no ending
        stuck = 0
        for session in self.sessions:
            if not session.ending_reached and session.total_turns >= 50:
                # Check for repeated commands or lack of progress
                if len(session.rooms_visited) <= 2:
                    stuck += 1
        return stuck

    def _count_incomplete_sessions(self) -> int:
        """Count sessions that didn't reach an ending."""
        return sum(1 for s in self.sessions if not s.ending_reached)

    def _find_failure_points(self) -> list[str]:
        """Find common points where sessions fail or get stuck."""
        failure_points = Counter()

        for session in self.sessions:
            if not session.ending_reached:
                # Record last room and action before failure
                if session.narratives:
                    last = session.narratives[-1]
                    failure_point = f"{session.rooms_visited[-1] if session.rooms_visited else 'unknown'}: {last.get('command', 'unknown')}"
                    failure_points[failure_point] += 1

        return [point for point, _ in failure_points.most_common(10)]

    def save_report(self, report: AnalysisReport) -> Path:
        """Save analysis report to disk."""
        summary_dir = self.output_dir / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_path = summary_dir / "analysis.json"
        with open(json_path, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        # Save markdown summary
        md_path = summary_dir / "analysis_summary.md"
        self._write_markdown_summary(report, md_path)

        logger.info("Analysis report saved to %s", summary_dir)
        return summary_dir

    def _write_markdown_summary(self, report: AnalysisReport, path: Path) -> None:
        """Write a human-readable markdown summary."""
        lines = [
            "# Test Session Analysis Report",
            "",
            f"**Generated:** {report.generated_at}",
            f"**Sessions Analyzed:** {report.sessions_analyzed}",
            "",
            "---",
            "",
            "## Coverage Summary",
            "",
            "### Endings Reached",
            "",
        ]

        for ending, count in sorted(report.endings_reached.items()):
            pct = count / report.sessions_analyzed * 100 if report.sessions_analyzed > 0 else 0
            lines.append(f"- **{ending}:** {count} ({pct:.1f}%)")

        lines.extend([
            "",
            "### Room Coverage",
            "",
        ])
        for room, count in sorted(report.rooms_coverage.items(), key=lambda x: -x[1]):
            pct = count / report.sessions_analyzed * 100 if report.sessions_analyzed > 0 else 0
            lines.append(f"- **{room}:** {count} visits ({pct:.1f}%)")

        lines.extend([
            "",
            "### Flag Discovery Coverage",
            "",
        ])
        for flag, count in sorted(report.flags_coverage.items(), key=lambda x: -x[1]):
            pct = count / report.sessions_analyzed * 100 if report.sessions_analyzed > 0 else 0
            lines.append(f"- **{flag}:** {count} ({pct:.1f}%)")

        lines.extend([
            "",
            "---",
            "",
            "## Performance Metrics",
            "",
            f"- **Average Turns to Ending:** {report.average_turns_to_ending:.1f}",
            f"- **Average Response Time:** {report.average_response_time_ms:.2f}ms",
            f"- **Max Response Time:** {report.max_response_time_ms:.2f}ms",
            "",
            "---",
            "",
            "## Error Analysis",
            "",
            f"**Total Errors:** {report.total_errors}",
            "",
        ])

        if report.error_patterns:
            lines.append("### Error Patterns")
            lines.append("")
            for pattern in report.error_patterns:
                lines.append(f"#### {pattern['error_type']} (Severity: {pattern['severity']})")
                lines.append(f"- Count: {pattern['count']}")
                lines.append(f"- Affected Sessions: {len(pattern['affected_sessions'])}")
                if pattern['example_messages']:
                    lines.append("- Examples:")
                    for ex in pattern['example_messages'][:2]:
                        lines.append(f"  - `{ex[:100]}`")
                lines.append("")

        lines.extend([
            "---",
            "",
            "## Persona Performance",
            "",
        ])

        for persona, data in report.persona_outcomes.items():
            lines.append(f"### {persona}")
            lines.append("")
            lines.append(f"- Sessions: {data['sessions']}")
            lines.append(f"- Completion Rate: {data['completion_rate']*100:.1f}%")
            lines.append(f"- Average Turns: {data['avg_turns']:.1f}")
            lines.append(f"- Errors: {data['errors']}")
            lines.append(f"- Rooms Visited: {', '.join(data['rooms_visited'])}")
            lines.append(f"- Flags Found: {', '.join(data['flags_found'])}")
            if data['endings']:
                lines.append(f"- Endings: {data['endings']}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## UX Insights",
            "",
            f"- **Stuck Sessions:** {report.stuck_sessions}",
            f"- **Incomplete Sessions:** {report.incomplete_sessions}",
            "",
        ])

        if report.common_failure_points:
            lines.append("### Common Failure Points")
            lines.append("")
            for point in report.common_failure_points:
                lines.append(f"- {point}")
            lines.append("")

        with open(path, "w") as f:
            f.write("\n".join(lines))
