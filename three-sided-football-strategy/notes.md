# Notes

## 2025-11-15
- Project initiated.
- Set up project structure following repository guidelines.
- Planning simulation approach using Python; intend to model strategy profiles and run Monte Carlo to estimate goal concession probabilities.
- Implemented core simulation module with strategy enumeration and Monte Carlo evaluation.
- Added analysis script to enumerate scenario-specific objectives, compute best responses, and report Nash equilibria.
- Built set-piece simulation exploring corner strategies for attacking and defending teams.
- Reran strategic analysis with additional statistics and JSON export for deeper interpretation.

## 2025-11-16
- Extended set-piece toolkit with free-kick and kick-off simulators plus reporting scripts covering net advantage, retention, and possession metrics.
- Introduced adaptive in-period policies with fatigue modelling in the simulation engine; captures late-game pushes, collaboration triggers, and recovery considerations.
- Updated strategic analysis workflow to build adaptive policies per scenario and summarise fatigue/strategy mixes in generated reports.
- Regenerated reports and CSV outputs for all set-piece and open-play analyses after tuning Monte Carlo sample sizes for tractable runtime.
