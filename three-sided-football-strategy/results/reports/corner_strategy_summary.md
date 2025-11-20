# Corner Strategy Outcomes

**Team role reference:** Team A delivers the corner, Team B defends the targeted goal directly, and Team C chooses between supporting the defence or springing a counter.

**Strategy glossary**

*Team A options*

- OVERLOAD_B: Crowd Team B's six-yard box with runners to overwhelm their keeper and attack the first ball.
- SPLIT_ATTACK: Divide attackers between B and C's zones to force mismatches and attack the second phase.
- SHORT_CORNER: Play a quick short pass to create a better crossing angle or draw out defenders before delivering.

*Team B options*

- GOAL_LINE: Station extra cover on the line to clear headers and protect the keeper.
- MAN_MARK: Track individual runners tightly, trading zonal coverage for duels.
- COUNTER_PRESS: Immediately swarm the taker and edge of box to launch a fast break once possession is won.

*Team C options*

- PRESS_A: Charge the corner taker and nearby outlets to disrupt short routines and spark a counter.
- PRESS_B: Drop into B's box to add aerial support and contest the first contact.
- STAY_BACK: Hold midfield shape to collect clearances and slow Team A's counter-press.

Top five attacking payoffs for Team A:

| A_strategy   | B_strategy    | C_strategy   |   goal_rate |   counter_rate |   net_advantage |
|:-------------|:--------------|:-------------|------------:|---------------:|----------------:|
| OVERLOAD_B   | MAN_MARK      | STAY_BACK    |     0.18715 |        0.0981  |         0.08905 |
| OVERLOAD_B   | COUNTER_PRESS | STAY_BACK    |     0.21865 |        0.136   |         0.08265 |
| OVERLOAD_B   | GOAL_LINE     | PRESS_B      |     0.19705 |        0.11705 |         0.08    |
| SPLIT_ATTACK | MAN_MARK      | STAY_BACK    |     0.13975 |        0.06225 |         0.0775  |
| OVERLOAD_B   | MAN_MARK      | PRESS_B      |     0.20635 |        0.1314  |         0.07495 |

Top five counter opportunities for Team C:

| A_strategy   | B_strategy    | C_strategy   |   goal_rate |   counter_rate |   net_advantage |
|:-------------|:--------------|:-------------|------------:|---------------:|----------------:|
| OVERLOAD_B   | COUNTER_PRESS | PRESS_A      |     0.1945  |        0.22205 |        -0.02755 |
| SPLIT_ATTACK | COUNTER_PRESS | PRESS_A      |     0.1473  |        0.18345 |        -0.03615 |
| OVERLOAD_B   | MAN_MARK      | PRESS_A      |     0.1687  |        0.18335 |        -0.01465 |
| OVERLOAD_B   | GOAL_LINE     | PRESS_A      |     0.15165 |        0.17325 |        -0.0216  |
| OVERLOAD_B   | COUNTER_PRESS | PRESS_B      |     0.23735 |        0.16535 |         0.072   |
