"""Analyze strategic scenarios for three-sided football using simulations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

# Ensure local imports resolve when running as a script
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from simulation import (
    TEAM_NAMES,
    TEAM_INDEX,
    SimulationConfig,
    Strategy,
    TeamState,
    ThreeSidedFootballGame,
    AdaptivePolicy,
    best_responses,
    estimate_payoffs,
    opponents_from_profile,
)


class Status(Enum):
    LEADING = auto()
    TRAILING = auto()
    DRAW_ONE = auto()
    DRAW_ALL = auto()


@dataclass
class Scenario:
    name: str
    period: int
    statuses: Dict[str, Status]
    description: str


TEAM_LABEL_REFERENCE = {
    "A": "Primary focus team in each scenario; when a side is leading this label denotes the leader.",
    "B": "Clockwise neighbour to Team A, typically reacting to A's tempo and protecting its own goal next in rotation.",
    "C": "Counter-clockwise neighbour balancing pressure between the other two teams and looking for opportunistic swings.",
}


STRATEGY_DESCRIPTIONS = {
    Strategy.DEFENSIVE.name: "Low block shape, extra cover around goal, prioritises damage limitation over pressing.",
    Strategy.BALANCED.name: "Even distribution of players with measured pressing and counters, aiming for stability.",
    Strategy.AGGRESSIVE.name: "High-risk press and overloads that chase turnovers and fast goals at the cost of exposure.",
    Strategy.COLLABORATE_WITH_NEXT.name: "Signals a pact with the clockwise neighbour to gang up on the remaining team and flood their zone.",
    Strategy.COLLABORATE_WITH_PREV.name: "Signals a pact with the counter-clockwise neighbour to compress the third team's build-up lanes.",
}


STATUS_ROLE_NOTES = {
    Status.LEADING: "Protecting a cushion—fewest concessions so far and managing risk.",
    Status.TRAILING: "Chasing the game—has conceded more and must recover ground.",
    Status.DRAW_ONE: "Level with one opponent but marginally separated from the third, juggling pressure in two directions.",
    Status.DRAW_ALL: "Completely level with both rivals; initiative is up for grabs.",
}


def build_objectives(period: int, statuses: Dict[str, Status]):
    weights = {
        Status.LEADING: {"conceded": 1.0, "scored": 0.05 + 0.05 * (period - 1)},
        Status.TRAILING: {"conceded": 1.0, "scored": 0.4 + 0.2 * (period - 1)},
        Status.DRAW_ONE: {"conceded": 1.0, "scored": 0.3 + 0.1 * (period - 1)},
        Status.DRAW_ALL: {"conceded": 1.0, "scored": 0.45 + 0.1 * (period - 1)},
    }

    def make_objective(status: Status):
        weight = weights[status]

        def objective(metrics: Dict[str, float]) -> float:
            return weight["conceded"] * metrics["expected_conceded"] - weight["scored"] * metrics[
                "expected_scored"
            ]

        return objective

    return {team: make_objective(status) for team, status in statuses.items()}


def build_adaptive_policies(scenario: Scenario, minutes: int) -> Dict[str, AdaptivePolicy]:
    base_late_minute = max(5, int(minutes * (0.55 + 0.1 * (scenario.period - 1))))
    policies: Dict[str, AdaptivePolicy] = {}
    status_priority = {
        Status.LEADING: 0,
        Status.DRAW_ONE: 1,
        Status.DRAW_ALL: 2,
        Status.TRAILING: 3,
    }

    def choose_collaboration_orientation(team: str) -> Strategy:
        team_idx = TEAM_INDEX[team]
        others = [other for other in TEAM_NAMES if other != team]
        others.sort(key=lambda name: status_priority[scenario.statuses[name]])
        target = others[0]
        next_target = TEAM_NAMES[(team_idx + 2) % len(TEAM_NAMES)]
        prev_target = TEAM_NAMES[(team_idx + 1) % len(TEAM_NAMES)]
        if target == next_target:
            return Strategy.COLLABORATE_WITH_NEXT
        if target == prev_target:
            return Strategy.COLLABORATE_WITH_PREV
        return Strategy.COLLABORATE_WITH_NEXT

    collaboration_orientation = {team: choose_collaboration_orientation(team) for team in TEAM_NAMES}

    for team in TEAM_NAMES:
        status = scenario.statuses[team]
        collab_strategy = collaboration_orientation[team]
        if status == Status.LEADING:
            policies[team] = AdaptivePolicy(
                default=Strategy.BALANCED if scenario.period < 3 else Strategy.DEFENSIVE,
                when_trailing=Strategy.AGGRESSIVE,
                trailing_margin=1.0,
                when_trailing_late=Strategy.AGGRESSIVE,
                late_minute=base_late_minute,
                when_leading=Strategy.DEFENSIVE,
                leading_margin=1.0,
                when_fatigued_offense=Strategy.DEFENSIVE,
                offense_fatigue_threshold=3.0,
                when_fatigued_defense=Strategy.BALANCED,
                defense_fatigue_threshold=3.2,
                draw_strategy=Strategy.BALANCED,
                draw_minute=base_late_minute,
            )
        elif status == Status.TRAILING:
            policies[team] = AdaptivePolicy(
                default=Strategy.AGGRESSIVE if scenario.period > 1 else Strategy.BALANCED,
                when_trailing=Strategy.AGGRESSIVE,
                trailing_margin=0.5,
                when_trailing_late=collab_strategy,
                late_minute=base_late_minute,
                when_leading=Strategy.DEFENSIVE,
                leading_margin=1.0,
                collaboration_margin=2.0,
                collaboration_strategy=collab_strategy,
                when_fatigued_offense=Strategy.BALANCED,
                offense_fatigue_threshold=3.5,
                when_fatigued_defense=Strategy.DEFENSIVE,
                defense_fatigue_threshold=3.8,
                draw_strategy=Strategy.AGGRESSIVE if scenario.period == 3 else Strategy.BALANCED,
                draw_minute=base_late_minute,
            )
        elif status == Status.DRAW_ONE:
            policies[team] = AdaptivePolicy(
                default=Strategy.BALANCED,
                when_trailing=Strategy.AGGRESSIVE,
                trailing_margin=1.0,
                when_trailing_late=Strategy.AGGRESSIVE,
                late_minute=base_late_minute,
                when_leading=Strategy.DEFENSIVE,
                leading_margin=1.0,
                collaboration_margin=2.0,
                collaboration_strategy=collab_strategy,
                when_fatigued_offense=Strategy.DEFENSIVE,
                offense_fatigue_threshold=3.2,
                draw_strategy=Strategy.AGGRESSIVE if scenario.period == 3 else Strategy.BALANCED,
                draw_minute=base_late_minute + 3,
            )
        else:  # Status.DRAW_ALL
            policies[team] = AdaptivePolicy(
                default=Strategy.BALANCED,
                when_trailing=Strategy.AGGRESSIVE,
                trailing_margin=1.0,
                when_trailing_late=Strategy.AGGRESSIVE,
                late_minute=base_late_minute + 2,
                when_leading=Strategy.DEFENSIVE,
                leading_margin=1.0,
                when_fatigued_offense=Strategy.DEFENSIVE,
                offense_fatigue_threshold=3.0,
                draw_strategy=Strategy.AGGRESSIVE,
                draw_minute=base_late_minute + 4,
                draw_margin=0.6,
            )
    return policies


def enumerate_scenarios() -> List[Scenario]:
    periods = [1, 2, 3]
    scenarios: List[Scenario] = []
    for period in periods:
        scenarios.append(
            Scenario(
                name=f"period{period}_all_tied",
                period=period,
                statuses={team: Status.DRAW_ALL for team in ("A", "B", "C")},
                description="All teams level on concessions and scores",
            )
        )
        scenarios.append(
            Scenario(
                name=f"period{period}_one_leads",
                period=period,
                statuses={"A": Status.LEADING, "B": Status.TRAILING, "C": Status.TRAILING},
                description="Team A leading, Teams B and C trailing",
            )
        )
        scenarios.append(
            Scenario(
                name=f"period{period}_two_tied",
                period=period,
                statuses={"A": Status.DRAW_ONE, "B": Status.DRAW_ONE, "C": Status.TRAILING},
                description="Teams A and B tied, Team C trailing",
            )
        )
        scenarios.append(
            Scenario(
                name=f"period{period}_one_trails",
                period=period,
                statuses={"A": Status.TRAILING, "B": Status.DRAW_ONE, "C": Status.DRAW_ONE},
                description="Team A trailing, Teams B and C level ahead",
            )
        )
    return scenarios


def analyze_scenario(
    scenario: Scenario,
    minutes: int = 25,
    samples: int = 4000,
) -> Dict[str, Any]:
    game = ThreeSidedFootballGame(SimulationConfig(random_seed=42))
    team_states = [TeamState(name=team, score=0, conceded=0) for team in ("A", "B", "C")]
    results = estimate_payoffs(game, team_states, minutes=minutes, samples=samples)
    objectives = build_objectives(scenario.period, scenario.statuses)
    br_map = best_responses(results, objectives)
    ne_profiles = find_pure_nash(results, br_map)
    strategy_counts = {
        team: pd.Series([br_map[team][opp] for opp in br_map[team]]).value_counts().to_dict()
        for team in br_map
    }
    strategy_stats = compute_strategy_stats(results)
    adaptive_policies = build_adaptive_policies(scenario, minutes)
    adaptive_samples = min(2000, max(1500, samples // 2))
    adaptive_summary = game.simulate_period_adaptive(
        team_states,
        adaptive_policies,
        minutes=minutes,
        samples=adaptive_samples,
    )
    return {
        "scenario": scenario,
        "results": results,
        "best_responses": br_map,
        "nash_equilibria": ne_profiles,
        "strategy_counts": strategy_counts,
        "strategy_stats": strategy_stats,
        "adaptive": adaptive_summary,
    }


def find_pure_nash(
    results: Dict[Tuple[Strategy, Strategy, Strategy], Dict[str, Dict[str, float]]],
    br_map: Dict[str, Dict[Tuple[Strategy, Strategy], Strategy]],
):
    equilibria = []
    for profile, metrics in results.items():
        is_ne = True
        for team in ("A", "B", "C"):
            opponents = opponents_from_profile(team, profile)
            best = br_map[team][opponents]
            if best != profile[{"A": 0, "B": 1, "C": 2}[team]]:
                is_ne = False
                break
        if is_ne:
            equilibria.append((profile, metrics))
    return equilibria


def compute_strategy_stats(
    results: Dict[Tuple[Strategy, Strategy, Strategy], Dict[str, Dict[str, float]]]
) -> Dict[str, Dict[str, Dict[str, float]]]:
    stats: Dict[str, Dict[str, Dict[str, float]]] = {team: {} for team in TEAM_NAMES}
    for team in TEAM_NAMES:
        idx = TEAM_INDEX[team]
        for strategy in Strategy:
            filtered = [metrics[team] for profile, metrics in results.items() if profile[idx] == strategy]
            if not filtered:
                continue
            conceded = np.mean([entry["expected_conceded"] for entry in filtered])
            scored = np.mean([entry["expected_scored"] for entry in filtered])
            stats[team][strategy.name] = {
                "expected_conceded": float(conceded),
                "expected_scored": float(scored),
                "expected_net": float(np.mean([entry["expected_net"] for entry in filtered])),
            }
    return stats


def summarize_equilibria(equilibria):
    rows = []
    for profile, metrics in equilibria:
        row = {
            "profile": "-".join(str(s.name) for s in profile),
        }
        for team in ("A", "B", "C"):
            data = metrics[team]
            row[f"{team}_conceded"] = data["expected_conceded"]
            row[f"{team}_scored"] = data["expected_scored"]
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    np.random.seed(123)
    scenarios = enumerate_scenarios()
    outputs = []
    for scenario in scenarios:
        analysis = analyze_scenario(scenario)
        outputs.append(analysis)
    output_dir = Path("results/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "strategy_analysis.md"
    with report_path.open("w", encoding="utf-8") as fh:
        fh.write("# Three-Sided Football Strategy Analysis\n\n")
        fh.write("## Team Label Reference\n\n")
        for team, note in TEAM_LABEL_REFERENCE.items():
            fh.write(f"- Team {team}: {note}\n")
        fh.write("\n")
        fh.write("## Core Strategy Glossary\n\n")
        for name, description in STRATEGY_DESCRIPTIONS.items():
            fh.write(f"- {name}: {description}\n")
        fh.write("\n")
        for result in outputs:
            scenario = result["scenario"]
            fh.write(f"## {scenario.name}\n\n")
            fh.write(f"{scenario.description}.\n\n")
            fh.write("### Team Roles in this Scenario\n\n")
            for team in TEAM_NAMES:
                status = scenario.statuses[team]
                fh.write(f"- Team {team}: {STATUS_ROLE_NOTES[status]}\n")
            fh.write("\n")
            fh.write("### Strategy Preferences\n\n")
            for team, counts in result["strategy_counts"].items():
                total = sum(counts.values())
                lines = [
                    f"- Team {team}: "
                    + ", ".join(
                        f"{strategy.name} ({count/total:.0%})" for strategy, count in counts.items()
                    )
                ]
                fh.write("\n".join(lines) + "\n")
            fh.write("\n")
            fh.write("### Nash Equilibria\n\n")
            df = summarize_equilibria(result["nash_equilibria"])
            if df.empty:
                fh.write("No pure strategy equilibria found under current assumptions.\n\n")
            else:
                fh.write(df.to_markdown(index=False) + "\n\n")
            fh.write("### Average Performance by Strategy\n\n")
            for team in TEAM_NAMES:
                fh.write(f"- Team {team}: ")
                ranked = sorted(
                    result["strategy_stats"][team].items(),
                    key=lambda item: item[1]["expected_conceded"],
                )
                top = [
                    f"{name} (conceded {values['expected_conceded']:.2f}, scored {values['expected_scored']:.2f})"
                    for name, values in ranked[:3]
                ]
                fh.write(", ".join(top) + "\n")
            fh.write("\n")
            fh.write("### Adaptive Dynamics\n\n")
            adaptive = result["adaptive"]
            metadata = adaptive["metadata"]
            fh.write(
                f"In-period collaboration frequency: {metadata['collaboration_frequency']:.1%}"
                f" across {metadata['samples']} simulations.\n\n"
            )
            team_metrics = adaptive["team_metrics"]
            for team in TEAM_NAMES:
                metrics = team_metrics[team]
                usage = metrics["strategy_usage"]
                if usage:
                    usage_lines = ", ".join(
                        f"{name} {share:.0%}"
                        for name, share in sorted(usage.items(), key=lambda item: item[1], reverse=True)
                    )
                else:
                    usage_lines = "BALANCED 100%"
                fh.write(
                    "- Team {team}: conceded {conceded:.2f}, scored {scored:.2f}, net {net:.2f}; "
                    "fatigue (off {off:.2f}, def {defn:.2f}); mix {usage}\n".format(
                        team=team,
                        conceded=metrics["expected_conceded"],
                        scored=metrics["expected_scored"],
                        net=metrics["expected_net"],
                        off=metrics["avg_offensive_fatigue"],
                        defn=metrics["avg_defensive_fatigue"],
                        usage=usage_lines,
                    )
                )
            fh.write("\n")
    raw_path = output_dir / "strategy_raw.json"
    serializable = []
    for result in outputs:
        serializable.append(
            {
                "scenario": {
                    "name": result["scenario"].name,
                    "period": result["scenario"].period,
                    "statuses": {team: result["scenario"].statuses[team].name for team in TEAM_NAMES},
                    "description": result["scenario"].description,
                },
                "strategy_counts": {
                    team: {strategy.name: count for strategy, count in counts.items()}
                    for team, counts in result["strategy_counts"].items()
                },
                "strategy_stats": result["strategy_stats"],
                "adaptive": result["adaptive"],
            }
        )
    raw_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
