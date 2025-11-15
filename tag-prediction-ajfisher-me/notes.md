# Notes

## 2025-11-14 21:50 UTC - Project setup
- Created task directory structure.

## 2025-11-14 21:51 UTC - Retrieved content repo
- Cloned ajfisher/ajfisher.me into data/raw for analysis (will not commit repo).

## 2025-11-14 21:51 UTC - Documented dependencies
- Added requirements.txt with analysis dependencies.

## 2025-11-14 21:52 UTC - Installed dependencies
- Installed pandas, scikit-learn, markdown-it-py for analysis.

## 2025-11-14 21:53 UTC - Implemented analysis script
- Added code/tag_prediction_analysis.py to evaluate multiple models and generate tag suggestions.

## 2025-11-14 21:55 UTC - Added iterative stratification
- Installed iterative-stratification to enable multi-label stratified CV.

## 2025-11-14 22:00 UTC - Improved tag parsing and outputs
- Normalized comma-separated tags into individual lowercase entries.
- Added candidate suggestions from top-5 predictions and low-confidence diagnostics.
- Re-ran analysis to regenerate results.

## 2025-11-14 22:01 UTC - Evaluation snapshot
- Cross-validated linear SVC achieved micro-F1 ~0.08 on 5-fold stratified CV; naive Bayes around 0.03; logistic-based variants collapsed to zero recall.
- Generated 42 posts with high-probability additional tag candidates (web/development dominate).

## 2025-11-14 22:02 UTC - Git hygiene
- Added .gitignore to exclude the cloned source repo from commits.
