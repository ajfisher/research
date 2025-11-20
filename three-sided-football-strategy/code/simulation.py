"""Simulation framework for three-sided football strategies.

This module defines data structures and simulation routines for modelling three-sided
football (Asger Jorn's variant) where three teams compete over three periods on a
hexagonal pitch. The simulation approximates match dynamics using Poisson goal models
parameterised by strategic choices made by each team.

The primary objective is to estimate expected goals conceded and scored under various
strategic profiles so that teams can reason about optimal play depending on their
standing (winning, drawing, or losing) as the game progresses.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Tuple

import numpy as np


class Strategy(Enum):
    """Enumeration of high-level strategies available to each team."""

    DEFENSIVE = auto()
    BALANCED = auto()
    AGGRESSIVE = auto()
    COLLABORATE_WITH_NEXT = auto()
    COLLABORATE_WITH_PREV = auto()


TEAM_NAMES = ("A", "B", "C")
TEAM_INDEX = {name: idx for idx, name in enumerate(TEAM_NAMES)}
STRATEGY_LIST: List[Strategy] = list(Strategy)
STRATEGY_TO_INDEX = {strategy: idx for idx, strategy in enumerate(STRATEGY_LIST)}

_STRATEGY_ATTACK_LOAD = {
    Strategy.DEFENSIVE: 0.7,
    Strategy.BALANCED: 1.0,
    Strategy.AGGRESSIVE: 1.35,
    Strategy.COLLABORATE_WITH_NEXT: 1.2,
    Strategy.COLLABORATE_WITH_PREV: 1.2,
}

_STRATEGY_DEFENSE_LOAD = {
    Strategy.DEFENSIVE: 1.3,
    Strategy.BALANCED: 1.0,
    Strategy.AGGRESSIVE: 0.85,
    Strategy.COLLABORATE_WITH_NEXT: 1.1,
    Strategy.COLLABORATE_WITH_PREV: 1.1,
}


@dataclass(frozen=True)
class TeamState:
    """State of a team entering a period."""

    name: str
    score: int
    conceded: int

    @property
    def net(self) -> int:
        """Goal differential (negative implies trailing)."""

        return self.score - self.conceded


@dataclass
class SimulationConfig:
    """Configuration parameters controlling the simulation."""

    base_rate: float = 0.04
    aggressive_attack_bonus: float = 1.3
    aggressive_defense_penalty: float = 0.85
    defensive_attack_penalty: float = 0.75
    defensive_defense_bonus: float = 1.35
    collaboration_attack_bonus: float = 1.5
    collaboration_defense_penalty: float = 0.9
    offensive_fatigue_rate: float = 0.08
    defensive_fatigue_rate: float = 0.07
    fatigue_recovery: float = 0.03
    fatigue_attack_penalty: float = 0.12
    fatigue_defense_penalty: float = 0.1
    random_seed: int | None = None


@dataclass
class AdaptivePolicy:
    """Heuristic policy describing in-period adaptations for a team."""

    default: Strategy = Strategy.BALANCED
    when_trailing: Strategy | None = Strategy.AGGRESSIVE
    trailing_margin: float = 1.0
    when_trailing_late: Strategy | None = None
    late_minute: int | None = None
    when_leading: Strategy | None = Strategy.DEFENSIVE
    leading_margin: float = 1.0
    collaboration_margin: float | None = None
    collaboration_strategy: Strategy | None = None
    when_fatigued_offense: Strategy | None = None
    offense_fatigue_threshold: float | None = None
    when_fatigued_defense: Strategy | None = None
    defense_fatigue_threshold: float | None = None
    draw_strategy: Strategy | None = None
    draw_minute: int | None = None
    draw_margin: float = 0.5

    def select_strategy(
        self,
        *,
        minute: int,
        total_minutes: int,
        team_index: int,
        total_scored: np.ndarray,
        total_conceded: np.ndarray,
        offensive_fatigue: float,
        defensive_fatigue: float,
    ) -> Strategy:
        """Return the strategy for the given minute and contextual state."""

        _ = total_scored  # retained for possible future use
        _ = total_minutes
        own_conceded = float(total_conceded[team_index])
        others = [float(total_conceded[idx]) for idx in range(len(total_conceded)) if idx != team_index]
        sorted_conceded = sorted(float(x) for x in total_conceded)
        best = sorted_conceded[0]
        second_best = sorted_conceded[1] if len(sorted_conceded) > 1 else sorted_conceded[0]
        trailing_by = max(0.0, own_conceded - best)
        leading_by = max(0.0, second_best - own_conceded)
        draw_gap = max((abs(own_conceded - other) for other in others), default=0.0)

        if (
            self.when_fatigued_offense is not None
            and self.offense_fatigue_threshold is not None
            and offensive_fatigue >= self.offense_fatigue_threshold
        ):
            return self.when_fatigued_offense

        if (
            self.when_fatigued_defense is not None
            and self.defense_fatigue_threshold is not None
            and defensive_fatigue >= self.defense_fatigue_threshold
        ):
            return self.when_fatigued_defense

        if (
            self.collaboration_margin is not None
            and self.collaboration_strategy is not None
            and trailing_by >= self.collaboration_margin
        ):
            return self.collaboration_strategy

        if self.when_trailing is not None and trailing_by >= max(0.0, self.trailing_margin):
            if self.late_minute is not None and minute >= self.late_minute and self.when_trailing_late is not None:
                return self.when_trailing_late
            return self.when_trailing

        if self.when_leading is not None and leading_by >= max(0.0, self.leading_margin):
            return self.when_leading

        if (
            self.draw_strategy is not None
            and self.draw_minute is not None
            and minute >= self.draw_minute
            and draw_gap <= self.draw_margin
        ):
            return self.draw_strategy

        if (
            self.when_trailing_late is not None
            and self.late_minute is not None
            and minute >= self.late_minute
            and trailing_by > 0
        ):
            return self.when_trailing_late

        return self.default


class ThreeSidedFootballGame:
    """Monte Carlo simulator for three-sided football periods."""

    def __init__(self, config: SimulationConfig | None = None) -> None:
        self.config = config or SimulationConfig()
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)

    def simulate_period(
        self,
        team_states: List[TeamState],
        strategies: Dict[str, Strategy],
        minutes: int = 25,
        samples: int = 10_000,
    ) -> Dict[str, Dict[str, float]]:
        """Simulate a single period under fixed strategies.

        Parameters
        ----------
        team_states:
            Current score and concessions for each team in order of TEAM_NAMES.
        strategies:
            Mapping from team name to selected :class:`Strategy`.
        minutes:
            Duration of the simulated period.
        samples:
            Number of Monte Carlo draws.

        Returns
        -------
        dict
            For each team, the expected goals scored, conceded, and net differential
            during the simulated period.
        """

        assert len(team_states) == 3, "Exactly three teams must be provided."
        attack_strength = np.ones(3)
        defense_strength = np.ones(3)

        for idx, team in enumerate(TEAM_NAMES):
            strat = strategies.get(team, Strategy.BALANCED)
            if strat == Strategy.AGGRESSIVE:
                attack_strength[idx] *= self.config.aggressive_attack_bonus
                defense_strength[idx] *= self.config.aggressive_defense_penalty
            elif strat == Strategy.DEFENSIVE:
                attack_strength[idx] *= self.config.defensive_attack_penalty
                defense_strength[idx] *= self.config.defensive_defense_bonus

        collaborators = self._identify_collaborations(strategies)
        attack_modifiers = np.ones((3, 3))

        for pair, target in collaborators:
            i, j = TEAM_INDEX[pair[0]], TEAM_INDEX[pair[1]]
            t_idx = TEAM_INDEX[target]
            attack_modifiers[i, t_idx] *= self.config.collaboration_attack_bonus
            attack_modifiers[j, t_idx] *= self.config.collaboration_attack_bonus
            defense_strength[i] *= self.config.collaboration_defense_penalty
            defense_strength[j] *= self.config.collaboration_defense_penalty

        lam = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                lam[i, j] = (
                    self.config.base_rate
                    * attack_strength[i]
                    * attack_modifiers[i, j]
                    / defense_strength[j]
                )

        aggregate_lam = lam * minutes
        draws = np.random.poisson(aggregate_lam, size=(samples, 3, 3))
        goals_scored = draws.sum(axis=2)
        goals_conceded = draws.sum(axis=1)

        summary = {}
        for idx, team in enumerate(TEAM_NAMES):
            summary[team] = {
                "expected_scored": float(goals_scored[:, idx].mean()),
                "expected_conceded": float(goals_conceded[:, idx].mean()),
                "expected_net": float(
                    goals_scored[:, idx].mean() - goals_conceded[:, idx].mean()
                ),
            }
        return summary

    def simulate_period_adaptive(
        self,
        team_states: List[TeamState],
        policies: Dict[str, AdaptivePolicy],
        minutes: int = 25,
        samples: int = 5_000,
    ) -> Dict[str, object]:
        """Simulate a period with within-period adaptations and fatigue."""

        assert len(team_states) == 3, "Exactly three teams must be provided."
        policies_map = {team: policies.get(team, AdaptivePolicy()) for team in TEAM_NAMES}
        base_scores = np.array([state.score for state in team_states], dtype=float)
        base_conceded = np.array([state.conceded for state in team_states], dtype=float)

        period_scored = np.zeros((samples, 3), dtype=float)
        period_conceded = np.zeros((samples, 3), dtype=float)
        offensive_fatigue = np.zeros((samples, 3), dtype=float)
        defensive_fatigue = np.zeros((samples, 3), dtype=float)
        usage_counts = np.zeros((3, len(STRATEGY_LIST)), dtype=int)
        collaboration_count = 0

        for minute in range(minutes):
            for sample_idx in range(samples):
                total_scored = base_scores + period_scored[sample_idx]
                total_conceded = base_conceded + period_conceded[sample_idx]
                sample_strategies: Dict[str, Strategy] = {}
                for team_idx, team in enumerate(TEAM_NAMES):
                    policy = policies_map[team]
                    strategy = policy.select_strategy(
                        minute=minute,
                        total_minutes=minutes,
                        team_index=team_idx,
                        total_scored=total_scored,
                        total_conceded=total_conceded,
                        offensive_fatigue=offensive_fatigue[sample_idx, team_idx],
                        defensive_fatigue=defensive_fatigue[sample_idx, team_idx],
                    )
                    sample_strategies[team] = strategy
                    usage_counts[team_idx, STRATEGY_TO_INDEX[strategy]] += 1

                attack_strength = np.ones(3)
                defense_strength = np.ones(3)
                for team_idx, team in enumerate(TEAM_NAMES):
                    strat = sample_strategies[team]
                    if strat == Strategy.AGGRESSIVE:
                        attack_strength[team_idx] *= self.config.aggressive_attack_bonus
                        defense_strength[team_idx] *= self.config.aggressive_defense_penalty
                    elif strat == Strategy.DEFENSIVE:
                        attack_strength[team_idx] *= self.config.defensive_attack_penalty
                        defense_strength[team_idx] *= self.config.defensive_defense_bonus

                for team_idx in range(3):
                    fatigue_attack_factor = max(
                        0.2,
                        1.0 - self.config.fatigue_attack_penalty * offensive_fatigue[sample_idx, team_idx],
                    )
                    fatigue_defense_factor = max(
                        0.3,
                        1.0 - self.config.fatigue_defense_penalty * defensive_fatigue[sample_idx, team_idx],
                    )
                    attack_strength[team_idx] *= fatigue_attack_factor
                    defense_strength[team_idx] *= fatigue_defense_factor

                attack_modifiers = np.ones((3, 3))
                collaborators = self._identify_collaborations(sample_strategies)
                if collaborators:
                    collaboration_count += 1
                for pair, target in collaborators:
                    i, j = TEAM_INDEX[pair[0]], TEAM_INDEX[pair[1]]
                    t_idx = TEAM_INDEX[target]
                    attack_modifiers[i, t_idx] *= self.config.collaboration_attack_bonus
                    attack_modifiers[j, t_idx] *= self.config.collaboration_attack_bonus
                    defense_strength[i] *= self.config.collaboration_defense_penalty
                    defense_strength[j] *= self.config.collaboration_defense_penalty

                lam = np.zeros((3, 3))
                for i in range(3):
                    for j in range(3):
                        if i == j:
                            continue
                        lam[i, j] = (
                            self.config.base_rate
                            * attack_strength[i]
                            * attack_modifiers[i, j]
                            / max(0.2, defense_strength[j])
                        )

                draws = np.random.poisson(lam)
                np.fill_diagonal(draws, 0)
                period_scored[sample_idx, :] += draws.sum(axis=1)
                period_conceded[sample_idx, :] += draws.sum(axis=0)

                for team_idx, team in enumerate(TEAM_NAMES):
                    strat = sample_strategies[team]
                    offensive_load = _STRATEGY_ATTACK_LOAD[strat]
                    defensive_load = _STRATEGY_DEFENSE_LOAD[strat]
                    offensive_fatigue[sample_idx, team_idx] = max(
                        0.0,
                        offensive_fatigue[sample_idx, team_idx]
                        + self.config.offensive_fatigue_rate * offensive_load
                        - self.config.fatigue_recovery,
                    )
                    defensive_fatigue[sample_idx, team_idx] = max(
                        0.0,
                        defensive_fatigue[sample_idx, team_idx]
                        + self.config.defensive_fatigue_rate * defensive_load
                        - self.config.fatigue_recovery * 0.7,
                    )

        total_decisions = minutes * samples
        team_summary: Dict[str, Dict[str, float | Dict[str, float]]] = {}
        for team_idx, team in enumerate(TEAM_NAMES):
            usage = {
                STRATEGY_LIST[idx].name: usage_counts[team_idx, idx] / total_decisions
                for idx in range(len(STRATEGY_LIST))
                if usage_counts[team_idx, idx] > 0
            }
            scored = period_scored[:, team_idx]
            conceded = period_conceded[:, team_idx]
            team_summary[team] = {
                "expected_scored": float(scored.mean()),
                "expected_conceded": float(conceded.mean()),
                "expected_net": float((scored - conceded).mean()),
                "avg_offensive_fatigue": float(offensive_fatigue[:, team_idx].mean()),
                "avg_defensive_fatigue": float(defensive_fatigue[:, team_idx].mean()),
                "strategy_usage": usage,
            }

        metadata = {
            "minutes": minutes,
            "samples": samples,
            "collaboration_frequency": collaboration_count / total_decisions,
        }
        return {"team_metrics": team_summary, "metadata": metadata}

    @staticmethod
    def _identify_collaborations(
        strategies: Dict[str, Strategy]
    ) -> List[Tuple[Tuple[str, str], str]]:
        """Return collaborating pairs and their targets.

        Collaboration occurs when two adjacent teams in TEAM_NAMES both select the
        appropriate `COLLABORATE_WITH_*` strategy that points to the third team.
        """

        target_map: Dict[str, List[str]] = {}
        n = len(TEAM_NAMES)
        for idx, team in enumerate(TEAM_NAMES):
            strat = strategies.get(team, Strategy.BALANCED)
            if strat not in {Strategy.COLLABORATE_WITH_NEXT, Strategy.COLLABORATE_WITH_PREV}:
                continue
            target_idx = (idx + 2) % n if strat == Strategy.COLLABORATE_WITH_NEXT else (idx + 1) % n
            target = TEAM_NAMES[target_idx]
            target_map.setdefault(target, []).append(team)

        collaborators: List[Tuple[Tuple[str, str], str]] = []
        for target, participants in target_map.items():
            if len(participants) < 2:
                continue
            for pair in combinations(sorted(participants), 2):
                collaborators.append((pair, target))
        return collaborators


def enumerate_strategies() -> List[Dict[str, Strategy]]:
    """Generate all possible pure strategy profiles for the three teams."""

    strategies = list(Strategy)
    profiles: List[Dict[str, Strategy]] = []
    for a in strategies:
        for b in strategies:
            for c in strategies:
                profiles.append({"A": a, "B": b, "C": c})
    return profiles


def estimate_payoffs(
    game: ThreeSidedFootballGame,
    team_states: List[TeamState],
    minutes: int,
    samples: int,
) -> Dict[Tuple[Strategy, Strategy, Strategy], Dict[str, Dict[str, float]]]:
    """Evaluate all strategy profiles for a given state."""

    results: Dict[Tuple[Strategy, Strategy, Strategy], Dict[str, Dict[str, float]]] = {}
    for profile in enumerate_strategies():
        key = (profile["A"], profile["B"], profile["C"])
        results[key] = game.simulate_period(team_states, profile, minutes=minutes, samples=samples)
    return results


ObjectiveFn = Callable[[Dict[str, float]], float]


def best_responses(
    results: Dict[Tuple[Strategy, Strategy, Strategy], Dict[str, Dict[str, float]]],
    objectives: Dict[str, ObjectiveFn],
) -> Dict[str, Dict[Tuple[Strategy, Strategy], Strategy]]:
    """Compute best responses for each team against opponent strategy pairs.

    Parameters
    ----------
    results:
        Mapping of complete strategy profiles to simulated performance metrics.
    objectives:
        Objective function for each team that converts the metrics dictionary into
        a scalar utility value (lower is better).
    """

    response_map: Dict[str, Dict[Tuple[Strategy, Strategy], Strategy]] = {
        team: {} for team in TEAM_NAMES
    }
    for team in TEAM_NAMES:
        objective = objectives[team]
        for opp_strats in _opponent_profiles():
            best_strategy = None
            best_value = float("inf")
            for own_strategy in Strategy:
                profile = _reconstruct_profile(team, own_strategy, opp_strats)
                metrics = results[profile][team]
                value = objective(metrics)
                if value < best_value:
                    best_value = value
                    best_strategy = own_strategy
            if best_strategy is not None:
                response_map[team][opp_strats] = best_strategy
    return response_map


def _opponent_profiles() -> Iterable[Tuple[Strategy, Strategy]]:
    for strat1 in Strategy:
        for strat2 in Strategy:
            yield (strat1, strat2)


def _reconstruct_profile(
    focus_team: str,
    focus_strategy: Strategy,
    opponent_strategies: Tuple[Strategy, Strategy],
) -> Tuple[Strategy, Strategy, Strategy]:
    order = list(TEAM_NAMES)
    idx = order.index(focus_team)
    profile: List[Strategy | None] = [None, None, None]
    profile[idx] = focus_strategy
    remaining = [s for s in order if s != focus_team]
    for opp_name, opp_strategy in zip(remaining, opponent_strategies):
        profile[order.index(opp_name)] = opp_strategy
    # type ignore is safe because we fill every slot above
    return tuple(profile)  # type: ignore[return-value]


def opponents_from_profile(
    focus_team: str, profile: Tuple[Strategy, Strategy, Strategy]
) -> Tuple[Strategy, Strategy]:
    """Return the opponent strategies from a full profile."""

    order = list(TEAM_NAMES)
    remaining = [s for s in order if s != focus_team]
    return tuple(profile[order.index(name)] for name in remaining)  # type: ignore[return-value]
