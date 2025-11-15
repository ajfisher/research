# Auto-tagging analysis for ajfisher.me posts

## Objective
Evaluate classical scikit-learn approaches for predicting front-matter tags on `ajfisher/ajfisher.me` markdown posts and use the predictions to highlight potential tag additions or removals.

## Background
The `site/src/content/posts` directory of `ajfisher.me` contains 92 markdown posts with YAML front matter. Tags are primarily descriptive keywords (e.g., `web`, `development`, `mobile`). Many historical posts repeat similar themes, so automatic tag recommendation could help keep taxonomy consistent, especially when tags are missing from older entries or when new posts are created without tags.

## Methodology
1. **Data acquisition** – Cloned the public repository and parsed front matter to extract titles, normalized lowercase tags (splitting comma-delimited strings), and markdown text converted to inline content.
2. **Feature engineering** – Built TF–IDF matrices (`ngram_range=(1,2)`, `min_df=2`, `max_df=0.85`) on the combined title+body text.
3. **Label encoding** – Used `MultiLabelBinarizer` to transform tag sets (61 unique tags; only `podcast` occurs once).
4. **Model portfolio** – Trained four multi-label estimators:
   - One-vs-rest linear SVM (`LinearSVC`)
   - One-vs-rest logistic regression
   - Complement Naïve Bayes (one-vs-rest)
   - Logistic regression classifier chain
5. **Evaluation** – 5-fold iterative-stratified CV (falling back to KFold when only one tag met the frequency threshold) using micro/macro F1, precision, recall, and subset accuracy. Rare tags with a single occurrence were excluded from CV but retained for full-model training.
6. **Diagnostics** – Fit the best model on all posts to obtain probability estimates. Recorded:
   - Thresholded predictions (default 0.5) for direct comparison with existing tags
   - Top-5 probable tags per post to surface high-confidence additions
   - Existing tags with probability <0.20 (none observed)

All code is in [`code/tag_prediction_analysis.py`](code/tag_prediction_analysis.py). Outputs land in [`results/`](results/).

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python code/tag_prediction_analysis.py \
  --posts-dir data/raw/ajfisher.me/site/src/content/posts \
  --output-dir results
```
Optional flags:
- `--probability-threshold`: adjust decision threshold (default `0.5`).
- `--low-confidence-threshold`: tune the cutoff used to flag existing tags with weak model support (default `0.2`).

## Results
### Model comparison (5-fold CV)
| model | micro F1 | macro F1 | micro precision | micro recall | subset accuracy |
| --- | --- | --- | --- | --- | --- |
| linear_svc | 0.077 ± 0.035 | 0.015 | 0.794 ± 0.134 | 0.041 ± 0.019 | 0.000 |
| complement_nb | 0.034 ± 0.019 | 0.007 | 0.950 ± 0.100 | 0.018 ± 0.009 | 0.000 |
| logreg_ovr | 0.000 ± 0.000 | 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 |
| logreg_chain | 0.000 ± 0.000 | 0.000 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.000 |

Key takeaways for Question 1:
- The one-vs-rest linear SVM consistently outperformed the other baselines but still achieved only ~0.08 micro-F1, indicating limited generalisation when tags are withheld.
- Logistic-regression-based approaches collapsed to predicting no positives with the current feature setup, suggesting heavier regularisation or different solvers (e.g., `saga`, class weights) are needed if they are to be competitive.
- Complement Naïve Bayes captured some frequent tags but lagged the SVM by ~5 percentage points.

### Candidate additions (Question 2)
- 42 of 92 posts surfaced at least one additional high-probability tag in the model’s top-5 predictions despite not clearing the 0.5 threshold.
- The most common suggested additions were `web` (appearing in 25 posts), `development` (15), `internet` (10), `mobile` (9), and `media` (8).
- Example subset:

| slug | candidate_missing_from_top5 |
| --- | --- |
| 2007-02-15-please-nokia-slap-me-again-no-really.md | ['development', 'web'] |
| 2007-04-23-why-is-css-such-a-painful-tool.md | ['media', 'web'] |
| 2007-04-30-super-computer-required-to-simulate-half-a-mouse-brain.md | ['development', 'mobile', 'web'] |
| 2007-08-25-jquery-saves-the-day.md | ['development', 'internet'] |
| 2008-05-12-google-app-engine-and-the-future-of-cloud-computing.md | ['cloud computing', 'development'] |

These candidates align with broad themes already in the taxonomy, implying that many posts are missing consistent umbrella tags like `web`, `development`, or `internet` even when the body focuses on those topics.

### Misapplied or low-confidence tags (Question 3)
- With the linear SVM trained on all posts, thresholded predictions matched the existing tag sets exactly; no direct misapplied tags were flagged.
- No tags fell below the 0.20 probability “low confidence” threshold. The model is confident in the assigned tags, likely because it fits the full dataset perfectly.
- Because CV metrics remain low, the absence of misapplied suggestions should be interpreted cautiously—the model likely overfits the current catalogue. Cross-validation performance highlights that many tags appear in only a handful of posts, making robust misclassification detection difficult without additional labelled data.

## Conclusions
- **Best approach**: The linear SVM provides the strongest baseline but still underperforms when tags are withheld; richer features (e.g., contextual embeddings) or more data are required for production-grade accuracy.
- **Missing tags**: Consistency gaps exist for umbrella tags (`web`, `development`, `internet`, `mobile`). Prioritising these additions would harmonise tag coverage across the archive.
- **Misapplied tags**: None were flagged at current thresholds; however, low CV scores suggest caution when interpreting this absence. Manual review of low-frequency tags (e.g., `podcast`) remains advisable.

## Future Work
- Incorporate pre-trained embeddings (e.g., sentence transformers) or topic models to capture semantics beyond TF–IDF n-grams.
- Tune SVM hyperparameters (C, class weighting) and explore probabilistic calibration to improve thresholded decisions.
- Use semi-supervised or weakly supervised data (e.g., category metadata, hyperlinks) to augment sparse tag classes.
- Build an interactive review notebook/dashboard that lets editors browse candidate additions and accept/reject suggestions.
- Revisit logistic/chain models with alternative solvers and regularisation once more labelled posts are available.
