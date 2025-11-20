"""Set piece simulators for three-sided football."""
from __future__ import annotations

from enum import Enum, auto
from typing import Dict, Tuple

import numpy as np


class CornerStrategyA(Enum):
    OVERLOAD_B = auto()
    SPLIT_ATTACK = auto()
    SHORT_CORNER = auto()


class CornerStrategyB(Enum):
    GOAL_LINE = auto()
    MAN_MARK = auto()
    COUNTER_PRESS = auto()


class CornerStrategyC(Enum):
    PRESS_A = auto()
    PRESS_B = auto()
    STAY_BACK = auto()


class FreeKickStrategyA(Enum):
    DIRECT_SHOT = auto()
    FAR_POST_CROSS = auto()
    QUICK_RESTART = auto()


class FreeKickStrategyB(Enum):
    HIGH_WALL = auto()
    SPLIT_WALL = auto()
    LATE_PRESS = auto()


class FreeKickStrategyC(Enum):
    PRESS_SECOND_BALL = auto()
    COVER_COUNTER = auto()
    STAY_CENTRAL = auto()


class KickoffStrategyA(Enum):
    FAST_BREAK = auto()
    CONTROLLED_BUILDUP = auto()
    BACK_PASS_SWITCH = auto()


class KickoffStrategyB(Enum):
    HIGH_PRESS = auto()
    MID_BLOCK = auto()
    DEEP_SHELL = auto()


class KickoffStrategyC(Enum):
    SWEEP_FORWARD = auto()
    MATCH_MARK = auto()
    SIT_DEEP = auto()


class CornerSimulator:
    def __init__(self, seed: int | None = None) -> None:
        if seed is not None:
            np.random.seed(seed)

    def _probabilities(
        self,
        strat_a: CornerStrategyA,
        strat_b: CornerStrategyB,
        strat_c: CornerStrategyC,
    ) -> Tuple[float, float, float]:
        base_goal = 0.12
        base_counter = 0.05

        modifiers_goal = {
            CornerStrategyA.OVERLOAD_B: 0.09,
            CornerStrategyA.SPLIT_ATTACK: 0.04,
            CornerStrategyA.SHORT_CORNER: -0.03,
        }
        modifiers_counter_a = {
            CornerStrategyA.OVERLOAD_B: 0.07,
            CornerStrategyA.SPLIT_ATTACK: 0.03,
            CornerStrategyA.SHORT_CORNER: -0.02,
        }

        modifiers_b_goal = {
            CornerStrategyB.GOAL_LINE: -0.04,
            CornerStrategyB.MAN_MARK: -0.02,
            CornerStrategyB.COUNTER_PRESS: 0.01,
        }
        modifiers_b_counter = {
            CornerStrategyB.GOAL_LINE: -0.01,
            CornerStrategyB.MAN_MARK: 0.0,
            CornerStrategyB.COUNTER_PRESS: 0.04,
        }

        modifiers_c_goal = {
            CornerStrategyC.PRESS_A: -0.02,
            CornerStrategyC.PRESS_B: 0.02,
            CornerStrategyC.STAY_BACK: 0.0,
        }
        modifiers_c_counter = {
            CornerStrategyC.PRESS_A: 0.06,
            CornerStrategyC.PRESS_B: 0.01,
            CornerStrategyC.STAY_BACK: -0.02,
        }

        p_goal = base_goal + modifiers_goal[strat_a] + modifiers_b_goal[strat_b] + modifiers_c_goal[strat_c]
        p_counter = base_counter + modifiers_counter_a[strat_a] + modifiers_b_counter[strat_b] + modifiers_c_counter[strat_c]
        p_goal = max(0.0, min(0.6, p_goal))
        p_counter = max(0.0, min(0.5, p_counter))
        p_neutral = max(0.0, 1.0 - p_goal - p_counter)
        total = p_goal + p_counter + p_neutral
        if total == 0:
            return 0.0, 0.0, 1.0
        p_goal /= total
        p_counter /= total
        p_neutral /= total
        return p_goal, p_counter, p_neutral

    def simulate(
        self,
        strat_a: CornerStrategyA,
        strat_b: CornerStrategyB,
        strat_c: CornerStrategyC,
        samples: int = 10000,
    ) -> Dict[str, float]:
        p_goal, p_counter, _ = self._probabilities(strat_a, strat_b, strat_c)
        draws = np.random.choice(
            ["goal", "counter", "neutral"],
            size=samples,
            p=[p_goal, p_counter, 1 - p_goal - p_counter],
        )
        goal_rate = float((draws == "goal").mean())
        counter_rate = float((draws == "counter").mean())
        return {
            "goal_rate": goal_rate,
            "counter_rate": counter_rate,
            "net_advantage": goal_rate - counter_rate,
        }


class FreeKickSimulator:
    """Simulate direct and indirect free-kick outcomes."""

    def __init__(self, seed: int | None = None) -> None:
        if seed is not None:
            np.random.seed(seed)

    def _probabilities(
        self,
        strat_a: FreeKickStrategyA,
        strat_b: FreeKickStrategyB,
        strat_c: FreeKickStrategyC,
    ) -> Tuple[float, float, float]:
        base_goal = 0.10
        base_counter = 0.04
        base_retained = 0.36

        modifiers_goal_a = {
            FreeKickStrategyA.DIRECT_SHOT: 0.08,
            FreeKickStrategyA.FAR_POST_CROSS: 0.05,
            FreeKickStrategyA.QUICK_RESTART: -0.02,
        }
        modifiers_goal_b = {
            FreeKickStrategyB.HIGH_WALL: -0.05,
            FreeKickStrategyB.SPLIT_WALL: -0.02,
            FreeKickStrategyB.LATE_PRESS: 0.01,
        }
        modifiers_goal_c = {
            FreeKickStrategyC.PRESS_SECOND_BALL: -0.01,
            FreeKickStrategyC.COVER_COUNTER: 0.0,
            FreeKickStrategyC.STAY_CENTRAL: 0.02,
        }

        modifiers_counter_a = {
            FreeKickStrategyA.DIRECT_SHOT: -0.01,
            FreeKickStrategyA.FAR_POST_CROSS: 0.03,
            FreeKickStrategyA.QUICK_RESTART: 0.05,
        }
        modifiers_counter_b = {
            FreeKickStrategyB.HIGH_WALL: -0.02,
            FreeKickStrategyB.SPLIT_WALL: 0.01,
            FreeKickStrategyB.LATE_PRESS: 0.04,
        }
        modifiers_counter_c = {
            FreeKickStrategyC.PRESS_SECOND_BALL: 0.05,
            FreeKickStrategyC.COVER_COUNTER: -0.02,
            FreeKickStrategyC.STAY_CENTRAL: -0.01,
        }

        modifiers_retained_a = {
            FreeKickStrategyA.DIRECT_SHOT: -0.08,
            FreeKickStrategyA.FAR_POST_CROSS: 0.06,
            FreeKickStrategyA.QUICK_RESTART: 0.09,
        }
        modifiers_retained_b = {
            FreeKickStrategyB.HIGH_WALL: -0.03,
            FreeKickStrategyB.SPLIT_WALL: 0.02,
            FreeKickStrategyB.LATE_PRESS: -0.04,
        }
        modifiers_retained_c = {
            FreeKickStrategyC.PRESS_SECOND_BALL: 0.07,
            FreeKickStrategyC.COVER_COUNTER: -0.05,
            FreeKickStrategyC.STAY_CENTRAL: -0.01,
        }

        p_goal = base_goal + modifiers_goal_a[strat_a] + modifiers_goal_b[strat_b] + modifiers_goal_c[strat_c]
        p_counter = base_counter + modifiers_counter_a[strat_a] + modifiers_counter_b[strat_b] + modifiers_counter_c[strat_c]
        p_retained = base_retained + modifiers_retained_a[strat_a] + modifiers_retained_b[strat_b] + modifiers_retained_c[strat_c]

        p_goal = max(0.0, min(0.55, p_goal))
        p_counter = max(0.0, min(0.5, p_counter))
        p_retained = max(0.0, min(0.8, p_retained))

        remainder = max(0.0, 1.0 - p_goal - p_counter - p_retained)
        total = p_goal + p_counter + p_retained + remainder
        if total == 0:
            return 0.0, 0.0, 0.0
        return p_goal / total, p_counter / total, p_retained / total

    def simulate(
        self,
        strat_a: FreeKickStrategyA,
        strat_b: FreeKickStrategyB,
        strat_c: FreeKickStrategyC,
        samples: int = 10000,
    ) -> Dict[str, float]:
        p_goal, p_counter, p_retained = self._probabilities(strat_a, strat_b, strat_c)
        draws = np.random.choice(
            ["goal", "counter", "retained", "lost"],
            size=samples,
            p=[p_goal, p_counter, p_retained, 1 - p_goal - p_counter - p_retained],
        )
        goal_rate = float((draws == "goal").mean())
        counter_rate = float((draws == "counter").mean())
        retained_rate = float((draws == "retained").mean())
        return {
            "goal_rate": goal_rate,
            "counter_rate": counter_rate,
            "retained_rate": retained_rate,
            "net_advantage": goal_rate - counter_rate,
        }


class KickoffSimulator:
    """Simulate restart dynamics from a centre kick-off."""

    def __init__(self, seed: int | None = None) -> None:
        if seed is not None:
            np.random.seed(seed)

    def _probabilities(
        self,
        strat_a: KickoffStrategyA,
        strat_b: KickoffStrategyB,
        strat_c: KickoffStrategyC,
    ) -> Tuple[float, float, float]:
        base_shot = 0.05
        base_counter = 0.03
        base_possession = 0.62

        modifiers_shot_a = {
            KickoffStrategyA.FAST_BREAK: 0.05,
            KickoffStrategyA.CONTROLLED_BUILDUP: 0.01,
            KickoffStrategyA.BACK_PASS_SWITCH: -0.01,
        }
        modifiers_shot_b = {
            KickoffStrategyB.HIGH_PRESS: -0.02,
            KickoffStrategyB.MID_BLOCK: -0.01,
            KickoffStrategyB.DEEP_SHELL: 0.0,
        }
        modifiers_shot_c = {
            KickoffStrategyC.SWEEP_FORWARD: -0.015,
            KickoffStrategyC.MATCH_MARK: -0.005,
            KickoffStrategyC.SIT_DEEP: 0.0,
        }

        modifiers_counter_a = {
            KickoffStrategyA.FAST_BREAK: 0.04,
            KickoffStrategyA.CONTROLLED_BUILDUP: -0.01,
            KickoffStrategyA.BACK_PASS_SWITCH: 0.02,
        }
        modifiers_counter_b = {
            KickoffStrategyB.HIGH_PRESS: 0.05,
            KickoffStrategyB.MID_BLOCK: 0.02,
            KickoffStrategyB.DEEP_SHELL: -0.02,
        }
        modifiers_counter_c = {
            KickoffStrategyC.SWEEP_FORWARD: 0.03,
            KickoffStrategyC.MATCH_MARK: 0.01,
            KickoffStrategyC.SIT_DEEP: -0.03,
        }

        modifiers_possession_a = {
            KickoffStrategyA.FAST_BREAK: -0.05,
            KickoffStrategyA.CONTROLLED_BUILDUP: 0.06,
            KickoffStrategyA.BACK_PASS_SWITCH: 0.08,
        }
        modifiers_possession_b = {
            KickoffStrategyB.HIGH_PRESS: -0.08,
            KickoffStrategyB.MID_BLOCK: -0.02,
            KickoffStrategyB.DEEP_SHELL: 0.05,
        }
        modifiers_possession_c = {
            KickoffStrategyC.SWEEP_FORWARD: -0.04,
            KickoffStrategyC.MATCH_MARK: -0.01,
            KickoffStrategyC.SIT_DEEP: 0.04,
        }

        p_shot = base_shot + modifiers_shot_a[strat_a] + modifiers_shot_b[strat_b] + modifiers_shot_c[strat_c]
        p_counter = base_counter + modifiers_counter_a[strat_a] + modifiers_counter_b[strat_b] + modifiers_counter_c[strat_c]
        p_possession = base_possession + modifiers_possession_a[strat_a] + modifiers_possession_b[strat_b] + modifiers_possession_c[strat_c]

        p_shot = max(0.0, min(0.25, p_shot))
        p_counter = max(0.0, min(0.4, p_counter))
        p_possession = max(0.0, min(0.9, p_possession))
        remainder = max(0.0, 1.0 - p_shot - p_counter - p_possession)
        total = p_shot + p_counter + p_possession + remainder
        if total == 0:
            return 0.0, 0.0, 0.0
        return p_shot / total, p_counter / total, p_possession / total

    def simulate(
        self,
        strat_a: KickoffStrategyA,
        strat_b: KickoffStrategyB,
        strat_c: KickoffStrategyC,
        samples: int = 10000,
    ) -> Dict[str, float]:
        p_shot, p_counter, p_possession = self._probabilities(strat_a, strat_b, strat_c)
        draws = np.random.choice(
            ["shot", "counter", "possession", "stalled"],
            size=samples,
            p=[p_shot, p_counter, p_possession, 1 - p_shot - p_counter - p_possession],
        )
        shot_rate = float((draws == "shot").mean())
        counter_rate = float((draws == "counter").mean())
        possession_rate = float((draws == "possession").mean())
        net = shot_rate - counter_rate + 0.25 * possession_rate
        return {
            "shot_rate": shot_rate,
            "counter_rate": counter_rate,
            "possession_rate": possession_rate,
            "net_advantage": net,
        }
