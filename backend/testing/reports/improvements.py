"""
Improvement tracking and recommendations.
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

from anthropic import Anthropic

from .analyzer import AnalysisReport

logger = logging.getLogger(__name__)


class ImprovementCategory(str, Enum):
    """Categories of improvements."""

    ERROR_HANDLING = "error_handling"
    UX_FLOW = "ux_flow"
    PERFORMANCE = "performance"
    CONTENT = "content"
    ACCESSIBILITY = "accessibility"
    BALANCE = "balance"
    BUG_FIX = "bug_fix"


class Priority(str, Enum):
    """Priority levels for improvements."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Improvement:
    """A suggested improvement with justification."""

    id: str
    title: str
    category: str
    priority: str
    description: str
    justification: str
    evidence: list[str] = field(default_factory=list)
    affected_files: list[str] = field(default_factory=list)
    estimated_effort: str = "medium"  # low, medium, high
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ImprovementTracker:
    """Tracks and generates improvement recommendations."""

    def __init__(self, output_dir: Path, model: str = "claude-sonnet-4-20250514"):
        self.output_dir = output_dir
        self.model = model
        self.improvements: list[Improvement] = []
        self._improvement_counter = 0
        self.client: Optional[Anthropic] = None

    def _ensure_client(self) -> Anthropic:
        """Lazily initialize the Anthropic client."""
        if self.client is None:
            self.client = Anthropic()
        return self.client

    def _next_id(self) -> str:
        """Generate the next improvement ID."""
        self._improvement_counter += 1
        return f"IMP-{self._improvement_counter:04d}"

    def add_improvement(
        self,
        title: str,
        category: ImprovementCategory,
        priority: Priority,
        description: str,
        justification: str,
        evidence: Optional[list[str]] = None,
        affected_files: Optional[list[str]] = None,
        estimated_effort: str = "medium",
    ) -> Improvement:
        """Add a new improvement recommendation."""
        improvement = Improvement(
            id=self._next_id(),
            title=title,
            category=category.value,
            priority=priority.value,
            description=description,
            justification=justification,
            evidence=evidence or [],
            affected_files=affected_files or [],
            estimated_effort=estimated_effort,
        )
        self.improvements.append(improvement)
        logger.info("Added improvement: %s - %s", improvement.id, title)
        return improvement

    def analyze_and_suggest(self, report: AnalysisReport) -> list[Improvement]:
        """Analyze report and suggest improvements."""
        suggestions = []

        # Error-based improvements
        suggestions.extend(self._suggest_from_errors(report))

        # Coverage-based improvements
        suggestions.extend(self._suggest_from_coverage(report))

        # Performance-based improvements
        suggestions.extend(self._suggest_from_performance(report))

        # UX-based improvements
        suggestions.extend(self._suggest_from_ux(report))

        return suggestions

    def _suggest_from_errors(self, report: AnalysisReport) -> list[Improvement]:
        """Generate suggestions from error patterns."""
        suggestions = []

        for pattern in report.error_patterns:
            if pattern["severity"] in ["critical", "high"]:
                priority = Priority.HIGH if pattern["severity"] == "critical" else Priority.MEDIUM
                improvement = self.add_improvement(
                    title=f"Fix {pattern['error_type']} errors",
                    category=ImprovementCategory.ERROR_HANDLING,
                    priority=priority,
                    description=f"Address {pattern['error_type']} errors occurring in {pattern['count']} instances across {len(pattern['affected_sessions'])} sessions.",
                    justification=f"These errors affect multiple sessions and may indicate a systematic issue. Error messages include: {'; '.join(pattern['example_messages'][:2])}",
                    evidence=pattern["example_messages"],
                    estimated_effort="medium" if pattern["count"] < 5 else "high",
                )
                suggestions.append(improvement)

        return suggestions

    def _suggest_from_coverage(self, report: AnalysisReport) -> list[Improvement]:
        """Generate suggestions from coverage gaps."""
        suggestions = []

        # Check for rooms never visited
        expected_rooms = ["threshold", "keeper_cell", "archive", "letter_room", "passage"]
        for room in expected_rooms:
            if room not in report.rooms_coverage or report.rooms_coverage[room] == 0:
                improvement = self.add_improvement(
                    title=f"Improve discoverability of {room}",
                    category=ImprovementCategory.UX_FLOW,
                    priority=Priority.MEDIUM,
                    description=f"The {room} room was never visited across all test sessions.",
                    justification="If a room is consistently missed, players may be lacking guidance on how to reach it or why they should explore it.",
                    affected_files=["backend/data/rooms.py", "backend/llm/narrative.py"],
                    estimated_effort="low",
                )
                suggestions.append(improvement)

        # Check for flags rarely discovered
        expected_flags = [
            "found_technical_diagrams",
            "found_creator_journal",
            "found_companion_origin",
            "found_keeper_logs",
            "found_old_letter",
        ]
        for flag in expected_flags:
            coverage = report.flags_coverage.get(flag, 0)
            if coverage < report.sessions_analyzed * 0.3:  # Less than 30% discovery rate
                improvement = self.add_improvement(
                    title=f"Improve hint system for {flag}",
                    category=ImprovementCategory.UX_FLOW,
                    priority=Priority.MEDIUM,
                    description=f"The flag '{flag}' was only discovered in {coverage}/{report.sessions_analyzed} sessions ({coverage/report.sessions_analyzed*100:.1f}%).",
                    justification="Low discovery rates suggest players may need better hints or more obvious pathways to find this content.",
                    affected_files=["backend/data/objects.py", "backend/llm/prompts.py"],
                    estimated_effort="medium",
                )
                suggestions.append(improvement)

        # Check for endings distribution
        if report.endings_reached:
            none_count = report.endings_reached.get("none", 0)
            if none_count > report.sessions_analyzed * 0.5:
                improvement = self.add_improvement(
                    title="Reduce difficulty of reaching endings",
                    category=ImprovementCategory.BALANCE,
                    priority=Priority.HIGH,
                    description=f"{none_count}/{report.sessions_analyzed} sessions failed to reach any ending.",
                    justification="Over 50% of sessions not reaching an ending indicates the game may be too difficult or confusing for players to complete.",
                    affected_files=["backend/engine/actions.py", "backend/llm/narrative.py"],
                    estimated_effort="high",
                )
                suggestions.append(improvement)

        return suggestions

    def _suggest_from_performance(self, report: AnalysisReport) -> list[Improvement]:
        """Generate suggestions from performance metrics."""
        suggestions = []

        # Slow response times
        if report.average_response_time_ms > 3000:  # 3 seconds
            improvement = self.add_improvement(
                title="Optimize API response times",
                category=ImprovementCategory.PERFORMANCE,
                priority=Priority.HIGH,
                description=f"Average response time is {report.average_response_time_ms:.0f}ms, which may feel slow to users.",
                justification="Response times over 3 seconds can frustrate users and break immersion in a narrative game.",
                affected_files=["backend/llm/intent.py", "backend/llm/narrative.py"],
                estimated_effort="high",
            )
            suggestions.append(improvement)

        if report.max_response_time_ms > 10000:  # 10 seconds
            improvement = self.add_improvement(
                title="Add timeout handling for slow requests",
                category=ImprovementCategory.ERROR_HANDLING,
                priority=Priority.MEDIUM,
                description=f"Maximum response time was {report.max_response_time_ms:.0f}ms. Very slow responses should be handled gracefully.",
                justification="Occasional very slow responses can make the game appear frozen. Adding timeouts and feedback improves perceived reliability.",
                affected_files=["backend/api/routes.py", "frontend/src/api/client.ts"],
                estimated_effort="medium",
            )
            suggestions.append(improvement)

        return suggestions

    def _suggest_from_ux(self, report: AnalysisReport) -> list[Improvement]:
        """Generate suggestions from UX insights."""
        suggestions = []

        # Stuck sessions
        if report.stuck_sessions > 0:
            improvement = self.add_improvement(
                title="Add progressive hints for stuck players",
                category=ImprovementCategory.UX_FLOW,
                priority=Priority.HIGH,
                description=f"{report.stuck_sessions} sessions got stuck and couldn't progress.",
                justification="Players getting stuck indicates they need better guidance. A progressive hint system could help without spoiling the experience.",
                affected_files=["backend/engine/actions.py", "backend/llm/narrative.py"],
                estimated_effort="high",
            )
            suggestions.append(improvement)

        # Common failure points
        if report.common_failure_points:
            improvement = self.add_improvement(
                title="Improve guidance at common failure points",
                category=ImprovementCategory.UX_FLOW,
                priority=Priority.MEDIUM,
                description=f"Common failure points identified: {', '.join(report.common_failure_points[:3])}",
                justification="These points represent where players most commonly fail to progress. Improving hints or feedback at these points could significantly improve completion rates.",
                evidence=report.common_failure_points,
                affected_files=["backend/llm/narrative.py", "backend/data/rooms.py"],
                estimated_effort="medium",
            )
            suggestions.append(improvement)

        return suggestions

    async def generate_llm_suggestions(self, report: AnalysisReport) -> list[Improvement]:
        """Use Claude to generate additional improvement suggestions."""
        client = self._ensure_client()

        prompt = f"""Analyze this test session report for a narrative text adventure game and suggest improvements.

## Report Summary
- Sessions analyzed: {report.sessions_analyzed}
- Endings reached: {report.endings_reached}
- Average turns to ending: {report.average_turns_to_ending:.1f}
- Average response time: {report.average_response_time_ms:.0f}ms
- Total errors: {report.total_errors}
- Stuck sessions: {report.stuck_sessions}
- Incomplete sessions: {report.incomplete_sessions}

## Room Coverage
{json.dumps(report.rooms_coverage, indent=2)}

## Flag Coverage
{json.dumps(report.flags_coverage, indent=2)}

## Error Patterns
{json.dumps(report.error_patterns, indent=2)}

## Common Failure Points
{report.common_failure_points}

Based on this data, suggest 3-5 specific, actionable improvements. For each, provide:
1. A clear title
2. Category (error_handling, ux_flow, performance, content, accessibility, balance, bug_fix)
3. Priority (critical, high, medium, low)
4. Description of the improvement
5. Justification based on the data

Respond in JSON format as an array of objects with keys: title, category, priority, description, justification
"""

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text

            # Extract JSON from response
            import re
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                suggestions_data = json.loads(json_match.group())
                for item in suggestions_data:
                    self.add_improvement(
                        title=item["title"],
                        category=ImprovementCategory(item["category"]),
                        priority=Priority(item["priority"]),
                        description=item["description"],
                        justification=item["justification"],
                    )

        except Exception as e:
            logger.warning("Failed to generate LLM suggestions: %s", e)

        return self.improvements

    def save_improvements(self) -> Path:
        """Save improvements to disk."""
        summary_dir = self.output_dir / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON
        json_path = summary_dir / "improvements.json"
        with open(json_path, "w") as f:
            json.dump([asdict(i) for i in self.improvements], f, indent=2)

        # Save Markdown
        md_path = summary_dir / "improvements.md"
        self._write_markdown(md_path)

        logger.info("Improvements saved to %s", summary_dir)
        return md_path

    def _write_markdown(self, path: Path) -> None:
        """Write improvements as a markdown file."""
        lines = [
            "# Improvement Recommendations",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Improvements:** {len(self.improvements)}",
            "",
            "---",
            "",
        ]

        # Group by priority
        by_priority = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for improvement in self.improvements:
            by_priority[improvement.priority].append(improvement)

        for priority in ["critical", "high", "medium", "low"]:
            items = by_priority[priority]
            if not items:
                continue

            lines.append(f"## {priority.upper()} Priority")
            lines.append("")

            for imp in items:
                lines.append(f"### [{imp.id}] {imp.title}")
                lines.append("")
                lines.append(f"**Category:** {imp.category}")
                lines.append(f"**Estimated Effort:** {imp.estimated_effort}")
                lines.append("")
                lines.append(f"**Description:**")
                lines.append(imp.description)
                lines.append("")
                lines.append(f"**Justification:**")
                lines.append(imp.justification)
                lines.append("")

                if imp.evidence:
                    lines.append("**Evidence:**")
                    for ev in imp.evidence[:3]:
                        lines.append(f"- {ev}")
                    lines.append("")

                if imp.affected_files:
                    lines.append(f"**Affected Files:** {', '.join(imp.affected_files)}")
                    lines.append("")

                lines.append("---")
                lines.append("")

        with open(path, "w") as f:
            f.write("\n".join(lines))
