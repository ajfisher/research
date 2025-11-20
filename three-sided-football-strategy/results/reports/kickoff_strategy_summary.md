# Kick-off Strategy Outcomes

**Team role reference:** Team A restarts play from the centre circle, Team B lines up opposite as the primary press, and Team C balances between contesting possession and shielding its own goal.

**Strategy glossary**

*Team A options*

- FAST_BREAK: Sprint forward off the whistle seeking a direct shot or overload before defences set.
- CONTROLLED_BUILDUP: Keep the ball through short passes, drawing opponents out before probing gaps.
- BACK_PASS_SWITCH: Drop the ball back then switch flanks rapidly to stretch the defensive shape.

*Team B options*

- HIGH_PRESS: Push players high immediately to trap Team A near the halfway line.
- MID_BLOCK: Hold a compact midfield line that shepherds play wide and buys time.
- DEEP_SHELL: Retreat to the defensive third to absorb pressure and rely on clearances.

*Team C options*

- SWEEP_FORWARD: Step into advanced lanes to contest flick-ons and support early counters.
- MATCH_MARK: Shadow nearby opponents to break passing triangles and slow the buildup.
- SIT_DEEP: Stay close to goal, acting as a safety net against through balls and long shots.

Best immediate attacking bursts:

| A_strategy         | B_strategy   | C_strategy   |   shot_rate |   counter_rate |   possession_rate |   net_advantage |
|:-------------------|:-------------|:-------------|------------:|---------------:|------------------:|----------------:|
| CONTROLLED_BUILDUP | DEEP_SHELL   | SIT_DEEP     |     0.05695 |        0       |           0.77315 |        0.250238 |
| FAST_BREAK         | DEEP_SHELL   | SIT_DEEP     |     0.0978  |        0.02075 |           0.6638  |        0.243    |
| BACK_PASS_SWITCH   | DEEP_SHELL   | SIT_DEEP     |     0.04185 |        0       |           0.79115 |        0.239638 |
| CONTROLLED_BUILDUP | DEEP_SHELL   | MATCH_MARK   |     0.05415 |        0.01165 |           0.71985 |        0.222463 |
| CONTROLLED_BUILDUP | MID_BLOCK    | SIT_DEEP     |     0.0486  |        0.0094  |           0.6993  |        0.214025 |

Safest possession-focused restarts:

| A_strategy         | B_strategy   | C_strategy   |   shot_rate |   counter_rate |   possession_rate |   net_advantage |
|:-------------------|:-------------|:-------------|------------:|---------------:|------------------:|----------------:|
| BACK_PASS_SWITCH   | DEEP_SHELL   | SIT_DEEP     |     0.04185 |        0       |           0.79115 |        0.239638 |
| CONTROLLED_BUILDUP | DEEP_SHELL   | SIT_DEEP     |     0.05695 |        0       |           0.77315 |        0.250238 |
| BACK_PASS_SWITCH   | DEEP_SHELL   | MATCH_MARK   |     0.03575 |        0.04005 |           0.73545 |        0.179563 |
| BACK_PASS_SWITCH   | MID_BLOCK    | SIT_DEEP     |     0.0289  |        0.03915 |           0.72005 |        0.169762 |
| CONTROLLED_BUILDUP | DEEP_SHELL   | MATCH_MARK   |     0.05415 |        0.01165 |           0.71985 |        0.222463 |
