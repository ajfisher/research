# Free-Kick Strategy Outcomes

**Team role reference:** Team A strikes the attacking free kick, Team B sets the immediate wall and keeper screen, and Team C manages spill-over space and counter threats.

**Strategy glossary**

*Team A options*

- DIRECT_SHOT: Target the goal directly with power or curl, prioritising immediate scoring chances.
- FAR_POST_CROSS: Loop a cross toward the weak-side runner for knockdowns across goal.
- QUICK_RESTART: Restart rapidly to catch Team B unorganised and exploit open passing lanes.

*Team B options*

- HIGH_WALL: Assemble a dense wall close to the ball, inviting the keeper to guard the far post.
- SPLIT_WALL: Split defenders to cover both the direct shot and runners attacking the channel.
- LATE_PRESS: Hold the line then rush the strike to narrow angles and chase loose balls.

*Team C options*

- PRESS_SECOND_BALL: Crash the box area to attack rebounds and disrupt Team A's follow-up.
- COVER_COUNTER: Sit deeper to screen passing lanes and shut down immediate counter-attacks.
- STAY_CENTRAL: Occupy the central lane to block cut-backs and recycle possession quickly.

Top attacking outcomes (goal-oriented):

| A_strategy     | B_strategy   | C_strategy        |   goal_rate |   counter_rate |   retained_rate |   net_advantage |
|:---------------|:-------------|:------------------|------------:|---------------:|----------------:|----------------:|
| DIRECT_SHOT    | LATE_PRESS   | STAY_CENTRAL      |     0.20805 |        0.0632  |         0.23085 |         0.14485 |
| DIRECT_SHOT    | LATE_PRESS   | COVER_COUNTER     |     0.18905 |        0.04955 |         0.18845 |         0.1395  |
| DIRECT_SHOT    | LATE_PRESS   | PRESS_SECOND_BALL |     0.1833  |        0.11795 |         0.31195 |         0.06535 |
| DIRECT_SHOT    | SPLIT_WALL   | STAY_CENTRAL      |     0.1822  |        0.0303  |         0.2882  |         0.1519  |
| FAR_POST_CROSS | LATE_PRESS   | STAY_CENTRAL      |     0.17695 |        0.0989  |         0.37575 |         0.07805 |

Highest ball retention rates:

| A_strategy     | B_strategy   | C_strategy        |   goal_rate |   counter_rate |   retained_rate |   net_advantage |
|:---------------|:-------------|:------------------|------------:|---------------:|----------------:|----------------:|
| QUICK_RESTART  | SPLIT_WALL   | PRESS_SECOND_BALL |     0.0507  |        0.14845 |         0.53865 |        -0.09775 |
| FAR_POST_CROSS | SPLIT_WALL   | PRESS_SECOND_BALL |     0.12335 |        0.12955 |         0.50445 |        -0.0062  |
| QUICK_RESTART  | HIGH_WALL    | PRESS_SECOND_BALL |     0.02095 |        0.1221  |         0.4928  |        -0.10115 |
| QUICK_RESTART  | LATE_PRESS   | PRESS_SECOND_BALL |     0.0818  |        0.18425 |         0.47295 |        -0.10245 |
| QUICK_RESTART  | SPLIT_WALL   | STAY_CENTRAL      |     0.0805  |        0.09395 |         0.46265 |        -0.01345 |
