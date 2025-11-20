"""Enumerate corner kick strategies for three-sided football."""
from __future__ import annotations

from itertools import product
from pathlib import Path
import sys
from typing import List

import pandas as pd

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from set_piece import (
    CornerSimulator,
    CornerStrategyA,
    CornerStrategyB,
    CornerStrategyC,
    FreeKickSimulator,
    FreeKickStrategyA,
    FreeKickStrategyB,
    FreeKickStrategyC,
    KickoffSimulator,
    KickoffStrategyA,
    KickoffStrategyB,
    KickoffStrategyC,
)


SET_PIECE_TEAM_ROLES = {
    "corner": "Team A delivers the corner, Team B defends the targeted goal directly, and Team C chooses between supporting the defence or springing a counter.",
    "free_kick": "Team A strikes the attacking free kick, Team B sets the immediate wall and keeper screen, and Team C manages spill-over space and counter threats.",
    "kickoff": "Team A restarts play from the centre circle, Team B lines up opposite as the primary press, and Team C balances between contesting possession and shielding its own goal.",
}


CORNER_STRATEGY_DESCRIPTIONS = {
    "A": {
        CornerStrategyA.OVERLOAD_B: "Crowd Team B's six-yard box with runners to overwhelm their keeper and attack the first ball.",
        CornerStrategyA.SPLIT_ATTACK: "Divide attackers between B and C's zones to force mismatches and attack the second phase.",
        CornerStrategyA.SHORT_CORNER: "Play a quick short pass to create a better crossing angle or draw out defenders before delivering.",
    },
    "B": {
        CornerStrategyB.GOAL_LINE: "Station extra cover on the line to clear headers and protect the keeper.",
        CornerStrategyB.MAN_MARK: "Track individual runners tightly, trading zonal coverage for duels.",
        CornerStrategyB.COUNTER_PRESS: "Immediately swarm the taker and edge of box to launch a fast break once possession is won.",
    },
    "C": {
        CornerStrategyC.PRESS_A: "Charge the corner taker and nearby outlets to disrupt short routines and spark a counter.",
        CornerStrategyC.PRESS_B: "Drop into B's box to add aerial support and contest the first contact.",
        CornerStrategyC.STAY_BACK: "Hold midfield shape to collect clearances and slow Team A's counter-press.",
    },
}


FREE_KICK_STRATEGY_DESCRIPTIONS = {
    "A": {
        FreeKickStrategyA.DIRECT_SHOT: "Target the goal directly with power or curl, prioritising immediate scoring chances.",
        FreeKickStrategyA.FAR_POST_CROSS: "Loop a cross toward the weak-side runner for knockdowns across goal.",
        FreeKickStrategyA.QUICK_RESTART: "Restart rapidly to catch Team B unorganised and exploit open passing lanes.",
    },
    "B": {
        FreeKickStrategyB.HIGH_WALL: "Assemble a dense wall close to the ball, inviting the keeper to guard the far post.",
        FreeKickStrategyB.SPLIT_WALL: "Split defenders to cover both the direct shot and runners attacking the channel.",
        FreeKickStrategyB.LATE_PRESS: "Hold the line then rush the strike to narrow angles and chase loose balls.",
    },
    "C": {
        FreeKickStrategyC.PRESS_SECOND_BALL: "Crash the box area to attack rebounds and disrupt Team A's follow-up.",
        FreeKickStrategyC.COVER_COUNTER: "Sit deeper to screen passing lanes and shut down immediate counter-attacks.",
        FreeKickStrategyC.STAY_CENTRAL: "Occupy the central lane to block cut-backs and recycle possession quickly.",
    },
}


KICKOFF_STRATEGY_DESCRIPTIONS = {
    "A": {
        KickoffStrategyA.FAST_BREAK: "Sprint forward off the whistle seeking a direct shot or overload before defences set.",
        KickoffStrategyA.CONTROLLED_BUILDUP: "Keep the ball through short passes, drawing opponents out before probing gaps.",
        KickoffStrategyA.BACK_PASS_SWITCH: "Drop the ball back then switch flanks rapidly to stretch the defensive shape.",
    },
    "B": {
        KickoffStrategyB.HIGH_PRESS: "Push players high immediately to trap Team A near the halfway line.",
        KickoffStrategyB.MID_BLOCK: "Hold a compact midfield line that shepherds play wide and buys time.",
        KickoffStrategyB.DEEP_SHELL: "Retreat to the defensive third to absorb pressure and rely on clearances.",
    },
    "C": {
        KickoffStrategyC.SWEEP_FORWARD: "Step into advanced lanes to contest flick-ons and support early counters.",
        KickoffStrategyC.MATCH_MARK: "Shadow nearby opponents to break passing triangles and slow the buildup.",
        KickoffStrategyC.SIT_DEEP: "Stay close to goal, acting as a safety net against through balls and long shots.",
    },
}


def write_glossary(fh, *, set_piece: str, descriptions: dict) -> None:
    fh.write(f"**Team role reference:** {SET_PIECE_TEAM_ROLES[set_piece]}\n\n")
    fh.write("**Strategy glossary**\n\n")
    for team in ("A", "B", "C"):
        if team not in descriptions:
            continue
        fh.write(f"*Team {team} options*\n\n")
        for strategy, description in descriptions[team].items():
            fh.write(f"- {strategy.name}: {description}\n")
        fh.write("\n")




def main():
    output_dir = Path("results/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    corner_sim = CornerSimulator(seed=7)
    corner_rows: List[dict] = []
    for strat_a, strat_b, strat_c in product(CornerStrategyA, CornerStrategyB, CornerStrategyC):
        metrics = corner_sim.simulate(strat_a, strat_b, strat_c, samples=20000)
        corner_rows.append(
            {
                "A_strategy": strat_a.name,
                "B_strategy": strat_b.name,
                "C_strategy": strat_c.name,
                **metrics,
            }
        )
    corner_df = pd.DataFrame(corner_rows)
    corner_df.sort_values(by="net_advantage", ascending=False, inplace=True)
    corner_table_path = output_dir / "corner_strategy_analysis.csv"
    corner_df.to_csv(corner_table_path, index=False)
    corner_summary_path = output_dir / "corner_strategy_summary.md"
    with corner_summary_path.open("w", encoding="utf-8") as fh:
        fh.write("# Corner Strategy Outcomes\n\n")
        write_glossary(fh, set_piece="corner", descriptions=CORNER_STRATEGY_DESCRIPTIONS)
        fh.write("Top five attacking payoffs for Team A:\n\n")
        fh.write(corner_df.head().to_markdown(index=False) + "\n\n")
        fh.write("Top five counter opportunities for Team C:\n\n")
        fh.write(corner_df.sort_values(by="counter_rate", ascending=False).head().to_markdown(index=False) + "\n")

    free_kick_sim = FreeKickSimulator(seed=11)
    free_kick_rows: List[dict] = []
    for strat_a, strat_b, strat_c in product(FreeKickStrategyA, FreeKickStrategyB, FreeKickStrategyC):
        metrics = free_kick_sim.simulate(strat_a, strat_b, strat_c, samples=20000)
        free_kick_rows.append(
            {
                "A_strategy": strat_a.name,
                "B_strategy": strat_b.name,
                "C_strategy": strat_c.name,
                **metrics,
            }
        )
    free_kick_df = pd.DataFrame(free_kick_rows)
    free_kick_df.sort_values(by="net_advantage", ascending=False, inplace=True)
    free_kick_table = output_dir / "free_kick_strategy_analysis.csv"
    free_kick_df.to_csv(free_kick_table, index=False)
    free_kick_summary = output_dir / "free_kick_strategy_summary.md"
    with free_kick_summary.open("w", encoding="utf-8") as fh:
        fh.write("# Free-Kick Strategy Outcomes\n\n")
        write_glossary(fh, set_piece="free_kick", descriptions=FREE_KICK_STRATEGY_DESCRIPTIONS)
        fh.write("Top attacking outcomes (goal-oriented):\n\n")
        fh.write(
            free_kick_df.sort_values(by="goal_rate", ascending=False)
            .head()
            .to_markdown(index=False)
            + "\n\n"
        )
        fh.write("Highest ball retention rates:\n\n")
        fh.write(
            free_kick_df.sort_values(by="retained_rate", ascending=False)
            .head()
            .to_markdown(index=False)
            + "\n"
        )

    kickoff_sim = KickoffSimulator(seed=19)
    kickoff_rows: List[dict] = []
    for strat_a, strat_b, strat_c in product(KickoffStrategyA, KickoffStrategyB, KickoffStrategyC):
        metrics = kickoff_sim.simulate(strat_a, strat_b, strat_c, samples=20000)
        kickoff_rows.append(
            {
                "A_strategy": strat_a.name,
                "B_strategy": strat_b.name,
                "C_strategy": strat_c.name,
                **metrics,
            }
        )
    kickoff_df = pd.DataFrame(kickoff_rows)
    kickoff_df.sort_values(by="net_advantage", ascending=False, inplace=True)
    kickoff_table = output_dir / "kickoff_strategy_analysis.csv"
    kickoff_df.to_csv(kickoff_table, index=False)
    kickoff_summary = output_dir / "kickoff_strategy_summary.md"
    with kickoff_summary.open("w", encoding="utf-8") as fh:
        fh.write("# Kick-off Strategy Outcomes\n\n")
        write_glossary(fh, set_piece="kickoff", descriptions=KICKOFF_STRATEGY_DESCRIPTIONS)
        fh.write("Best immediate attacking bursts:\n\n")
        fh.write(kickoff_df.head().to_markdown(index=False) + "\n\n")
        fh.write("Safest possession-focused restarts:\n\n")
        fh.write(
            kickoff_df.sort_values(by="possession_rate", ascending=False)
            .head()
            .to_markdown(index=False)
            + "\n"
        )

    print(
        "Wrote set-piece analyses to",
        corner_table_path,
        corner_summary_path,
        free_kick_table,
        free_kick_summary,
        kickoff_table,
        kickoff_summary,
    )


if __name__ == "__main__":
    main()
