# Three-Sided Football Strategy Analysis

## Team Label Reference

- Team A: Primary focus team in each scenario; when a side is leading this label denotes the leader.
- Team B: Clockwise neighbour to Team A, typically reacting to A's tempo and protecting its own goal next in rotation.
- Team C: Counter-clockwise neighbour balancing pressure between the other two teams and looking for opportunistic swings.

## Core Strategy Glossary

- DEFENSIVE: Low block shape, extra cover around goal, prioritises damage limitation over pressing.
- BALANCED: Even distribution of players with measured pressing and counters, aiming for stability.
- AGGRESSIVE: High-risk press and overloads that chase turnovers and fast goals at the cost of exposure.
- COLLABORATE_WITH_NEXT: Signals a pact with the clockwise neighbour to gang up on the remaining team and flood their zone.
- COLLABORATE_WITH_PREV: Signals a pact with the counter-clockwise neighbour to compress the third team's build-up lanes.

## period1_all_tied

All teams level on concessions and scores.

### Team Roles in this Scenario

- Team A: Completely level with both rivals; initiative is up for grabs.
- Team B: Completely level with both rivals; initiative is up for grabs.
- Team C: Completely level with both rivals; initiative is up for grabs.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 0.0% across 2000 simulations.

- Team A: conceded 2.09, scored 2.21, net 0.13; fatigue (off 1.45, def 1.20); mix AGGRESSIVE 43%, BALANCED 42%, DEFENSIVE 16%
- Team B: conceded 2.18, scored 2.15, net -0.03; fatigue (off 1.46, def 1.19); mix AGGRESSIVE 43%, BALANCED 42%, DEFENSIVE 15%
- Team C: conceded 2.19, scored 2.09, net -0.10; fatigue (off 1.46, def 1.19); mix AGGRESSIVE 43%, BALANCED 41%, DEFENSIVE 16%

## period1_one_leads

Team A leading, Teams B and C trailing.

### Team Roles in this Scenario

- Team A: Protecting a cushion—fewest concessions so far and managing risk.
- Team B: Chasing the game—has conceded more and must recover ground.
- Team C: Chasing the game—has conceded more and must recover ground.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 9.8% across 2000 simulations.

- Team A: conceded 2.04, scored 2.05, net 0.02; fatigue (off 1.45, def 1.19); mix BALANCED 45%, AGGRESSIVE 41%, DEFENSIVE 14%
- Team B: conceded 2.00, scored 2.00, net -0.00; fatigue (off 1.36, def 1.33); mix BALANCED 44%, COLLABORATE_WITH_NEXT 30%, DEFENSIVE 15%, AGGRESSIVE 11%
- Team C: conceded 1.98, scored 1.96, net -0.01; fatigue (off 1.35, def 1.33); mix BALANCED 44%, COLLABORATE_WITH_PREV 30%, DEFENSIVE 16%, AGGRESSIVE 11%

## period1_two_tied

Teams A and B tied, Team C trailing.

### Team Roles in this Scenario

- Team A: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team B: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team C: Chasing the game—has conceded more and must recover ground.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 5.9% across 2000 simulations.

- Team A: conceded 1.96, scored 2.03, net 0.07; fatigue (off 1.38, def 1.28); mix BALANCED 44%, AGGRESSIVE 22%, COLLABORATE_WITH_PREV 18%, DEFENSIVE 16%
- Team B: conceded 1.99, scored 1.97, net -0.01; fatigue (off 1.39, def 1.28); mix BALANCED 43%, AGGRESSIVE 23%, COLLABORATE_WITH_NEXT 18%, DEFENSIVE 15%
- Team C: conceded 2.00, scored 1.94, net -0.06; fatigue (off 1.36, def 1.32); mix BALANCED 44%, COLLABORATE_WITH_PREV 30%, DEFENSIVE 15%, AGGRESSIVE 11%

## period1_one_trails

Team A trailing, Teams B and C level ahead.

### Team Roles in this Scenario

- Team A: Chasing the game—has conceded more and must recover ground.
- Team B: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team C: Level with one opponent but marginally separated from the third, juggling pressure in two directions.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 6.0% across 2000 simulations.

- Team A: conceded 1.93, scored 1.96, net 0.04; fatigue (off 1.35, def 1.33); mix BALANCED 44%, COLLABORATE_WITH_PREV 29%, DEFENSIVE 16%, AGGRESSIVE 11%
- Team B: conceded 2.02, scored 1.93, net -0.10; fatigue (off 1.40, def 1.28); mix BALANCED 43%, AGGRESSIVE 23%, COLLABORATE_WITH_PREV 19%, DEFENSIVE 15%
- Team C: conceded 1.98, scored 2.04, net 0.06; fatigue (off 1.40, def 1.27); mix BALANCED 43%, AGGRESSIVE 24%, COLLABORATE_WITH_NEXT 18%, DEFENSIVE 15%

## period2_all_tied

All teams level on concessions and scores.

### Team Roles in this Scenario

- Team A: Completely level with both rivals; initiative is up for grabs.
- Team B: Completely level with both rivals; initiative is up for grabs.
- Team C: Completely level with both rivals; initiative is up for grabs.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 0.0% across 2000 simulations.

- Team A: conceded 2.11, scored 2.18, net 0.07; fatigue (off 1.45, def 1.20); mix BALANCED 43%, AGGRESSIVE 42%, DEFENSIVE 16%
- Team B: conceded 2.15, scored 2.17, net 0.02; fatigue (off 1.45, def 1.20); mix BALANCED 43%, AGGRESSIVE 41%, DEFENSIVE 15%
- Team C: conceded 2.19, scored 2.10, net -0.09; fatigue (off 1.46, def 1.19); mix AGGRESSIVE 43%, BALANCED 42%, DEFENSIVE 15%

## period2_one_leads

Team A leading, Teams B and C trailing.

### Team Roles in this Scenario

- Team A: Protecting a cushion—fewest concessions so far and managing risk.
- Team B: Chasing the game—has conceded more and must recover ground.
- Team C: Chasing the game—has conceded more and must recover ground.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 10.2% across 2000 simulations.

- Team A: conceded 2.23, scored 2.15, net -0.07; fatigue (off 1.45, def 1.21); mix AGGRESSIVE 43%, BALANCED 38%, DEFENSIVE 18%
- Team B: conceded 2.17, scored 2.27, net 0.10; fatigue (off 1.61, def 1.24); mix AGGRESSIVE 51%, COLLABORATE_WITH_NEXT 29%, DEFENSIVE 18%, BALANCED 2%
- Team C: conceded 2.25, scored 2.23, net -0.03; fatigue (off 1.63, def 1.23); mix AGGRESSIVE 51%, COLLABORATE_WITH_PREV 30%, DEFENSIVE 17%, BALANCED 2%

## period2_two_tied

Teams A and B tied, Team C trailing.

### Team Roles in this Scenario

- Team A: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team B: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team C: Chasing the game—has conceded more and must recover ground.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 6.2% across 2000 simulations.

- Team A: conceded 2.05, scored 2.06, net 0.01; fatigue (off 1.38, def 1.29); mix BALANCED 41%, AGGRESSIVE 22%, COLLABORATE_WITH_PREV 20%, DEFENSIVE 17%
- Team B: conceded 2.06, scored 2.04, net -0.02; fatigue (off 1.39, def 1.28); mix BALANCED 42%, AGGRESSIVE 23%, COLLABORATE_WITH_NEXT 19%, DEFENSIVE 17%
- Team C: conceded 2.12, scored 2.13, net 0.01; fatigue (off 1.65, def 1.22); mix AGGRESSIVE 54%, COLLABORATE_WITH_PREV 29%, DEFENSIVE 15%, BALANCED 2%

## period2_one_trails

Team A trailing, Teams B and C level ahead.

### Team Roles in this Scenario

- Team A: Chasing the game—has conceded more and must recover ground.
- Team B: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team C: Level with one opponent but marginally separated from the third, juggling pressure in two directions.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 6.0% across 2000 simulations.

- Team A: conceded 2.11, scored 2.13, net 0.02; fatigue (off 1.65, def 1.22); mix AGGRESSIVE 54%, COLLABORATE_WITH_PREV 29%, DEFENSIVE 16%, BALANCED 2%
- Team B: conceded 2.05, scored 2.02, net -0.04; fatigue (off 1.38, def 1.29); mix BALANCED 42%, AGGRESSIVE 23%, COLLABORATE_WITH_PREV 19%, DEFENSIVE 17%
- Team C: conceded 2.05, scored 2.07, net 0.02; fatigue (off 1.40, def 1.28); mix BALANCED 42%, AGGRESSIVE 23%, COLLABORATE_WITH_NEXT 19%, DEFENSIVE 15%

## period3_all_tied

All teams level on concessions and scores.

### Team Roles in this Scenario

- Team A: Completely level with both rivals; initiative is up for grabs.
- Team B: Completely level with both rivals; initiative is up for grabs.
- Team C: Completely level with both rivals; initiative is up for grabs.

### Strategy Preferences

- Team A: DEFENSIVE (92%), COLLABORATE_WITH_PREV (4%), COLLABORATE_WITH_NEXT (4%)
- Team B: DEFENSIVE (92%), COLLABORATE_WITH_PREV (4%), COLLABORATE_WITH_NEXT (4%)
- Team C: DEFENSIVE (92%), COLLABORATE_WITH_NEXT (8%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 0.0% across 2000 simulations.

- Team A: conceded 2.07, scored 2.20, net 0.13; fatigue (off 1.45, def 1.20); mix BALANCED 43%, AGGRESSIVE 41%, DEFENSIVE 16%
- Team B: conceded 2.16, scored 2.14, net -0.03; fatigue (off 1.45, def 1.20); mix BALANCED 44%, AGGRESSIVE 41%, DEFENSIVE 15%
- Team C: conceded 2.20, scored 2.09, net -0.11; fatigue (off 1.45, def 1.19); mix BALANCED 43%, AGGRESSIVE 42%, DEFENSIVE 15%

## period3_one_leads

Team A leading, Teams B and C trailing.

### Team Roles in this Scenario

- Team A: Protecting a cushion—fewest concessions so far and managing risk.
- Team B: Chasing the game—has conceded more and must recover ground.
- Team C: Chasing the game—has conceded more and must recover ground.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (32%), AGGRESSIVE (32%), COLLABORATE_WITH_NEXT (20%), COLLABORATE_WITH_PREV (16%)
- Team C: DEFENSIVE (44%), AGGRESSIVE (20%), COLLABORATE_WITH_NEXT (20%), COLLABORATE_WITH_PREV (16%)

### Nash Equilibria

| profile                                               |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE                         |      1.10575 |    1.0995  |      1.11625 |    1.11825 |      1.11825 |    1.1225  |
| DEFENSIVE-COLLABORATE_WITH_NEXT-COLLABORATE_WITH_PREV |      2.26225 |    1.68825 |      1.94875 |    2.2675  |      1.9725  |    2.22775 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 9.4% across 2000 simulations.

- Team A: conceded 1.99, scored 1.99, net -0.00; fatigue (off 1.15, def 1.45); mix DEFENSIVE 61%, AGGRESSIVE 38%, BALANCED 1%
- Team B: conceded 2.14, scored 2.15, net 0.01; fatigue (off 1.67, def 1.20); mix AGGRESSIVE 57%, COLLABORATE_WITH_NEXT 27%, DEFENSIVE 15%
- Team C: conceded 2.15, scored 2.15, net -0.01; fatigue (off 1.67, def 1.20); mix AGGRESSIVE 58%, COLLABORATE_WITH_PREV 28%, DEFENSIVE 15%

## period3_two_tied

Teams A and B tied, Team C trailing.

### Team Roles in this Scenario

- Team A: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team B: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team C: Chasing the game—has conceded more and must recover ground.

### Strategy Preferences

- Team A: DEFENSIVE (100%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (44%), AGGRESSIVE (20%), COLLABORATE_WITH_NEXT (20%), COLLABORATE_WITH_PREV (16%)

### Nash Equilibria

| profile                       |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| DEFENSIVE-DEFENSIVE-DEFENSIVE |      1.10575 |     1.0995 |      1.11625 |    1.11825 |      1.11825 |     1.1225 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 5.2% across 2000 simulations.

- Team A: conceded 2.11, scored 2.06, net -0.06; fatigue (off 1.39, def 1.29); mix BALANCED 41%, AGGRESSIVE 23%, COLLABORATE_WITH_PREV 20%, DEFENSIVE 17%
- Team B: conceded 2.06, scored 2.05, net -0.01; fatigue (off 1.40, def 1.28); mix BALANCED 41%, AGGRESSIVE 24%, COLLABORATE_WITH_NEXT 18%, DEFENSIVE 16%
- Team C: conceded 2.11, scored 2.17, net 0.06; fatigue (off 1.67, def 1.20); mix AGGRESSIVE 58%, COLLABORATE_WITH_PREV 27%, DEFENSIVE 15%

## period3_one_trails

Team A trailing, Teams B and C level ahead.

### Team Roles in this Scenario

- Team A: Chasing the game—has conceded more and must recover ground.
- Team B: Level with one opponent but marginally separated from the third, juggling pressure in two directions.
- Team C: Level with one opponent but marginally separated from the third, juggling pressure in two directions.

### Strategy Preferences

- Team A: DEFENSIVE (40%), AGGRESSIVE (24%), COLLABORATE_WITH_NEXT (20%), COLLABORATE_WITH_PREV (16%)
- Team B: DEFENSIVE (100%)
- Team C: DEFENSIVE (100%)

### Nash Equilibria

| profile                        |   A_conceded |   A_scored |   B_conceded |   B_scored |   C_conceded |   C_scored |
|:-------------------------------|-------------:|-----------:|-------------:|-----------:|-------------:|-----------:|
| AGGRESSIVE-DEFENSIVE-DEFENSIVE |      1.74625 |      1.931 |        1.503 |     1.4075 |      1.52275 |     1.4335 |

### Average Performance by Strategy

- Team A: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.05, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.10)
- Team B: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_PREV (conceded 2.10, scored 2.10)
- Team C: DEFENSIVE (conceded 1.53, scored 1.48), BALANCED (conceded 2.06, scored 1.97), COLLABORATE_WITH_NEXT (conceded 2.10, scored 2.09)

### Adaptive Dynamics

In-period collaboration frequency: 5.8% across 2000 simulations.

- Team A: conceded 2.09, scored 2.20, net 0.10; fatigue (off 1.67, def 1.20); mix AGGRESSIVE 58%, COLLABORATE_WITH_PREV 27%, DEFENSIVE 16%
- Team B: conceded 2.08, scored 2.04, net -0.04; fatigue (off 1.38, def 1.29); mix BALANCED 41%, AGGRESSIVE 23%, COLLABORATE_WITH_PREV 19%, DEFENSIVE 17%
- Team C: conceded 2.10, scored 2.04, net -0.07; fatigue (off 1.40, def 1.28); mix BALANCED 41%, AGGRESSIVE 24%, COLLABORATE_WITH_NEXT 20%, DEFENSIVE 16%

