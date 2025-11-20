# Three-Sided Football Strategy Research

## Objective
Investigate strategic decision making in three-sided football using computational game theory. The research addresses:

1. Optimal team strategies across the three 25-minute periods depending on whether a team is leading, trailing, or drawing (with one or two opponents).
2. Conditions under which collaboration between teams is preferable to direct competition.
3. Effective approaches for set-piece situations (corner kicks, free kicks, and kick-offs) involving three teams.
4. Adaptive within-period decision rules that react to changing scorelines and player fatigue.

## Background
Three-sided football replaces the binary nature of traditional football with a triadic contest where the winner is the team that concedes the fewest goals. Alliances are fluid and can shift in response to the scoreboard, and matches are played over three equal periods. Understanding how strategic incentives change throughout the match requires modelling both cooperative and competitive dynamics.

## Methodology
- Implemented a Monte Carlo simulator for three-team periods with configurable strategies, fatigue accumulation, and adaptive policies that trigger tactical shifts based on scoreboard margins, collaboration opportunities, and fatigue thresholds.【F:code/simulation.py†L21-L400】
- Enumerated strategy profiles and built scenario-specific objectives plus adaptive policy generators to compare static equilibria against fatigue-aware dynamics; exported markdown and JSON reports that capture best responses, Nash equilibria, and in-period strategy mixes.【F:code/analyze_strategies.py†L19-L220】【F:results/reports/strategy_analysis.md†L1-L360】
- Expanded set-piece modelling to cover corners, free kicks, and kick-offs, capturing goal, counter, possession, and retention probabilities, and produced ranked CSV/markdown summaries for each phase.【F:code/set_piece.py†L10-L260】【F:code/analyze_set_pieces.py†L31-L130】【F:results/reports/corner_strategy_summary.md†L1-L21】【F:results/reports/free_kick_strategy_summary.md†L1-L16】【F:results/reports/kickoff_strategy_summary.md†L1-L16】

## Setup
```bash
pip install numpy pandas
python code/analyze_strategies.py
python code/analyze_set_pieces.py
```
The scripts recreate the analytical reports in `results/reports/`.

## Results
### Period-by-period strategic insights
- **Periods 1 & 2 (static):** Defensive play remains the unique best response regardless of scoreboard state; deviating to balanced or collaborative plans increases expected concessions from ~1.53 to roughly 2.05–2.10 goals per period, offering insufficient scoring upside.【F:results/reports/strategy_analysis.md†L9-L23】【F:results/reports/strategy_analysis.md†L129-L143】
- **Periods 1 & 2 (adaptive):** Dynamic policies push trailing sides into aggressive or collaborative actions roughly 40–50% of the time, lifting their scoring above two goals but also inflating concessions and fatigue (offensive fatigue ~1.45 versus ~1.2 for leaders). Leaders exploit the cushion by staying mostly balanced/defensive with positive net margins.【F:results/reports/strategy_analysis.md†L25-L61】【F:results/reports/strategy_analysis.md†L145-L181】
- **Period 3:** Static best responses introduce collaborative options for chasers, and an alternate equilibrium appears where both trailing teams collaborate against the leader, doubling the leader’s concessions from 1.11 to 2.26 expected goals.【F:results/reports/strategy_analysis.md†L249-L289】 Adaptive policies amplify this behaviour—trailing teams spend over half of late-period minutes in aggressive or collaborative modes while leaders lean 60% defensive, trading higher fatigue for counter-pressure windows.【F:results/reports/strategy_analysis.md†L300-L332】

### Collaboration versus competition
- Alliances become attractive only when chasing: collaborative equilibria raise each chaser’s scoring to ~2.27 while forcing the leader above two conceded goals, but static leaders still prefer pure defense.【F:results/reports/strategy_analysis.md†L285-L303】
- Under adaptive play, isolated trailers invest ~57% of minutes in aggressive/collaborative tactics and generate small positive net returns despite higher fatigue, whereas teams already leading see diminishing returns from collaboration.【F:results/reports/strategy_analysis.md†L340-L360】

### Set-piece strategies
- Corners: overloading with a man-marking primary defender and a conservative third team yields the top net advantage (+0.089) with an 18.7% scoring rate; aggressive third-team presses flip the payoff in favour of counters.【F:results/reports/corner_strategy_summary.md†L1-L20】
- Free kicks: direct shots against a late-pressing wall and central third team deliver ~20.8% goal probability and the strongest net advantage, while quick restarts with second-ball pressure maximise retention above 53%.【F:results/reports/free_kick_strategy_summary.md†L1-L16】
- Kick-offs: controlled build-up or back-pass switches against deep blocks secure possession retention above 77% and net advantages above 0.22, outperforming high-risk fast breaks when opponents press high.【F:results/reports/kickoff_strategy_summary.md†L1-L16】

## Conclusions
- Conservative defensive setups still minimise concessions in early periods; adaptive risk-taking only pays off when a side is chasing and willing to absorb extra fatigue and counter pressure.
- Late-game collaboration is a high-variance lever: coordinated coalitions can double a leader’s concessions, but the required aggressive workload rapidly drives fatigue toward critical thresholds.
- Set-piece choices should mirror match context—direct free kicks and structured kick-offs reward teams needing possession or goals, while conservative coverage suppresses counter-threats for leaders.

## Future Work
- Calibrate fatigue parameters and recovery rates with empirical or expert data to strengthen the adaptive model.
- Explore mixed-strategy equilibria or reinforcement learning agents to capture stochastic play and evolving alliances.
- Incorporate additional restarts (e.g., throw-ins) and spatial pitch constraints to extend the set-piece toolkit.
