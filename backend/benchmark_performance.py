#!/usr/bin/env python3
"""
Performance benchmark script for API response times.
Measures intent classification and narrative generation separately.
"""
import asyncio
import time
import statistics
import json
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

from models.state import GameState, GameFlags, Room
from llm.intent import classify_intent
from llm.narrative import generate_narrative, generate_opening_narrative, clear_cache, get_cache_stats
from engine.actions import ActionResult


# Test commands that exercise different code paths
TEST_COMMANDS = [
    "look around",
    "examine the archway",
    "go to the archive",
    "talk to the companion",
    "examine technical diagrams",
    "ask companion about the station",
    "go to keeper cell",
    "examine the desk",
    "help",
    "inventory",
]


async def benchmark_intent_classification(commands: list[str], state: GameState) -> dict:
    """Benchmark intent classification times."""
    times = []

    for cmd in commands:
        start = time.perf_counter()
        await classify_intent(cmd, state)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        times.append(elapsed)
        print(f"  Intent '{cmd[:20]}...': {elapsed:.0f}ms")

    return {
        "count": len(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) >= 2 else max(times),
    }


async def benchmark_narrative_generation(state: GameState) -> dict:
    """Benchmark narrative generation times."""
    times = []

    # Test different action types
    test_cases = [
        ("LOOK", ActionResult(success=True, context={
            "action": "LOOK",
            "room_id": "threshold",
            "room_name": "The Threshold",
            "visible_objects": ["archway", "stone_floor", "strange_light"],
            "characters": ["traveler", "companion"],
            "exits": ["keeper_cell", "archive"],
        })),
        ("EXAMINE", ActionResult(success=True, context={
            "action": "EXAMINE",
            "target": "archway",
            "object_name": "Stone Archway",
            "base_description": "Ancient stonework, worn smooth by time.",
        })),
        ("MOVE", ActionResult(success=True, context={
            "action": "MOVE",
            "from_room": "threshold",
            "to_room": "archive",
            "room_name": "The Archive",
            "room_description": "Shelves line the walls.",
        })),
        ("TALK", ActionResult(success=True, context={
            "action": "TALK",
            "target": "companion",
            "prompt_context": "The companion is warm, attentive, helpful.",
        })),
    ]

    for action, result in test_cases:
        start = time.perf_counter()
        await generate_narrative(action, state, result)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"  Narrative '{action}': {elapsed:.0f}ms")

    return {
        "count": len(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) >= 2 else max(times),
    }


async def benchmark_opening_narrative() -> dict:
    """Benchmark opening narrative generation."""
    times = []

    for i in range(3):
        start = time.perf_counter()
        await generate_opening_narrative()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"  Opening narrative {i+1}: {elapsed:.0f}ms")

    return {
        "count": len(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": statistics.mean(times),
    }


async def benchmark_full_command_cycle(state: GameState) -> dict:
    """Benchmark full command processing (intent + narrative)."""
    times = []
    cached_times = []

    commands = ["look around", "examine archway", "go archive", "talk to companion"]

    # First pass - uncached
    print("  [Uncached requests]")
    for cmd in commands:
        start = time.perf_counter()

        # Intent classification
        intent = await classify_intent(cmd, state)

        # Simulate action result
        result = ActionResult(success=True, context={
            "action": intent.intent.value,
            "target": intent.target,
            "room_id": state.current_room.value,
        })

        # Narrative generation
        await generate_narrative(intent.intent.value, state, result)

        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f"    '{cmd}': {elapsed:.0f}ms")

    # Second pass - should hit cache for LOOK/EXAMINE/MOVE
    print("  [Cached requests]")
    for cmd in ["look around", "examine archway", "go archive"]:
        start = time.perf_counter()

        intent = await classify_intent(cmd, state)
        result = ActionResult(success=True, context={
            "action": intent.intent.value,
            "target": intent.target,
            "room_id": state.current_room.value,
        })
        await generate_narrative(intent.intent.value, state, result)

        elapsed = (time.perf_counter() - start) * 1000
        cached_times.append(elapsed)
        print(f"    '{cmd}': {elapsed:.0f}ms (cache hit)")

    return {
        "uncached_count": len(times),
        "uncached_mean_ms": statistics.mean(times),
        "uncached_p95_ms": sorted(times)[int(len(times) * 0.95)] if len(times) >= 2 else max(times),
        "cached_count": len(cached_times),
        "cached_mean_ms": statistics.mean(cached_times),
        "cached_p95_ms": sorted(cached_times)[int(len(cached_times) * 0.95)] if len(cached_times) >= 2 else max(cached_times),
    }


async def run_benchmark():
    """Run complete benchmark suite."""
    print("=" * 60)
    print("PERFORMANCE BENCHMARK")
    print("=" * 60)

    # Clear cache for clean benchmark
    clear_cache()

    # Create test state
    state = GameState(session_id="benchmark-test")

    results = {}

    # Benchmark intent classification
    print("\n[1/4] Intent Classification")
    print("-" * 40)
    results["intent_classification"] = await benchmark_intent_classification(
        TEST_COMMANDS[:5], state  # Use subset for faster benchmark
    )

    # Benchmark narrative generation
    print("\n[2/4] Narrative Generation")
    print("-" * 40)
    results["narrative_generation"] = await benchmark_narrative_generation(state)

    # Benchmark opening narrative
    print("\n[3/4] Opening Narrative")
    print("-" * 40)
    results["opening_narrative"] = await benchmark_opening_narrative()

    # Benchmark full command cycle
    print("\n[4/4] Full Command Cycle (Intent + Narrative)")
    print("-" * 40)
    results["full_cycle"] = await benchmark_full_command_cycle(state)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"\nIntent Classification:")
    print(f"  Mean: {results['intent_classification']['mean_ms']:.0f}ms")
    print(f"  P95:  {results['intent_classification']['p95_ms']:.0f}ms")

    print(f"\nNarrative Generation:")
    print(f"  Mean: {results['narrative_generation']['mean_ms']:.0f}ms")
    print(f"  P95:  {results['narrative_generation']['p95_ms']:.0f}ms")

    print(f"\nFull Command Cycle (Uncached):")
    print(f"  Mean: {results['full_cycle']['uncached_mean_ms']:.0f}ms")
    print(f"  P95:  {results['full_cycle']['uncached_p95_ms']:.0f}ms")

    print(f"\nFull Command Cycle (Cached):")
    print(f"  Mean: {results['full_cycle']['cached_mean_ms']:.0f}ms")
    print(f"  P95:  {results['full_cycle']['cached_p95_ms']:.0f}ms")

    # Calculate improvement
    uncached = results['full_cycle']['uncached_mean_ms']
    cached = results['full_cycle']['cached_mean_ms']
    improvement = ((uncached - cached) / uncached) * 100
    print(f"\nCache Improvement: {improvement:.0f}% faster")

    # Cache stats
    cache_stats = get_cache_stats()
    print(f"\nCache Stats:")
    print(f"  Hits: {cache_stats['hits']}")
    print(f"  Misses: {cache_stats['misses']}")
    print(f"  Hit Rate: {cache_stats['hit_rate']*100:.0f}%")

    # Save results
    output_path = Path(__file__).parent / "benchmark_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    asyncio.run(run_benchmark())
