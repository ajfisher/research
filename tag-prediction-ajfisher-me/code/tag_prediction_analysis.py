"""Tag prediction analysis for ajfisher.me posts.

This script loads markdown posts with front matter tags and evaluates
multiple multi-label text classification approaches using scikit-learn.
It reports cross-validated performance and generates tag suggestions for
missing, misapplied, or untagged posts.
"""
from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import numpy as np
import pandas as pd
import yaml
from markdown_it import MarkdownIt
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, cross_validate
from sklearn.multiclass import OneVsRestClassifier
from sklearn.multioutput import ClassifierChain
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC
@dataclass
class Post:
    """Represents a markdown post with metadata."""

    slug: str
    title: str
    tags: List[str]
    text: str


FRONT_MATTER_DELIMITER = "---"

warnings.filterwarnings(
    "ignore",
    message="Label not .*present in all training examples.",
    category=UserWarning,
)


def load_posts(posts_dir: Path) -> List[Post]:
    """Load posts from a directory recursively.

    Args:
        posts_dir: Root directory containing markdown files.

    Returns:
        List of Post objects for files that contain front matter.
    """

    posts: List[Post] = []
    md = MarkdownIt()
    for path in sorted(posts_dir.rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if not raw.strip().startswith(FRONT_MATTER_DELIMITER):
            continue
        parts = raw.split(FRONT_MATTER_DELIMITER, 2)
        if len(parts) < 3:
            continue
        _, yaml_block, body = parts
        try:
            front_matter = yaml.safe_load(yaml_block) or {}
        except yaml.YAMLError:
            continue

        tags_value = front_matter.get("tags") or []
        if isinstance(tags_value, str):
            tags_iterable: List[str] = [tags_value]
        else:
            tags_iterable = list(tags_value)

        tags: List[str] = []
        for tag in tags_iterable:
            tag_str = str(tag).strip()
            if not tag_str:
                continue
            pieces = [piece.strip().lower() for piece in tag_str.split(",") if piece.strip()]
            tags.extend(pieces or [tag_str.lower()])

        tags = sorted(set(tags))

        title = str(front_matter.get("title") or path.stem)

        # Render markdown to HTML then strip tags by leveraging MarkdownIt token text.
        # Collect literal text content from the token stream for a cleaner corpus.
        tokens = md.parse(body)
        text_fragments: List[str] = []
        for token in tokens:
            if token.type == "inline" and token.content:
                text_fragments.append(token.content)
        plain_text = " ".join(text_fragments)
        if not plain_text:
            plain_text = body

        combined_text = f"{title}\n{plain_text}"

        slug = str(path.relative_to(posts_dir)).replace("\\", "/")
        posts.append(Post(slug=slug, title=title, tags=tags, text=combined_text))
    return posts


def build_models() -> dict[str, Pipeline]:
    """Create candidate pipelines for evaluation."""

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85,
        sublinear_tf=True,
    )

    pipelines: dict[str, Pipeline] = {
        "logreg_ovr": Pipeline(
            steps=[
                ("tfidf", vectorizer),
                (
                    "clf",
                    OneVsRestClassifier(
                        LogisticRegression(
                            max_iter=2000,
                            solver="lbfgs",
                        )
                    ),
                ),
            ]
        ),
        "linear_svc": Pipeline(
            steps=[
                ("tfidf", vectorizer),
                (
                    "clf",
                    OneVsRestClassifier(
                        LinearSVC(C=1.0),
                    ),
                ),
            ]
        ),
        "complement_nb": Pipeline(
            steps=[
                ("tfidf", vectorizer),
                (
                    "clf",
                    OneVsRestClassifier(ComplementNB(alpha=0.5)),
                ),
            ]
        ),
        "logreg_chain": Pipeline(
            steps=[
                ("tfidf", vectorizer),
                (
                    "clf",
                    ClassifierChain(
                        LogisticRegression(max_iter=2000, solver="lbfgs"),
                        random_state=42,
                    ),
                ),
            ]
        ),
    }
    return pipelines


def evaluate_models(
    models: dict[str, Pipeline],
    X: Sequence[str],
    Y: np.ndarray,
    scoring: dict[str, metrics.Scorer],
    cv_splits: int = 5,
) -> pd.DataFrame:
    """Run cross-validation for each model and return summary DataFrame."""

    results = []
    if Y.ndim == 2 and Y.shape[1] >= 2:
        cv = MultilabelStratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=42)
    else:
        cv = KFold(n_splits=cv_splits, shuffle=True, random_state=42)
    for name, model in models.items():
        cv_result = cross_validate(
            model,
            X,
            Y,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            error_score=np.nan,
            return_train_score=False,
        )
        mean_scores = {
            metric: float(np.nanmean(values))
            for metric, values in cv_result.items()
            if metric.startswith("test_")
        }
        std_scores = {
            f"{metric}_std": float(np.nanstd(values))
            for metric, values in cv_result.items()
            if metric.startswith("test_")
        }
        results.append({"model": name, **mean_scores, **std_scores})
    df_results = pd.DataFrame(results).sort_values(by="test_f1_micro", ascending=False)
    return df_results


def suggest_tags(
    model: Pipeline,
    X: Sequence[str],
    Y: np.ndarray,
    posts: pd.DataFrame,
    mlb: MultiLabelBinarizer,
    probability_threshold: float = 0.5,
    low_confidence_threshold: float = 0.2,
) -> pd.DataFrame:
    """Generate predictions and compare to existing tags."""

    model.fit(X, Y)
    # Many OneVsRest estimators expose decision_function or predict_proba.
    clf = model.named_steps["clf"]
    if hasattr(clf, "predict_proba"):
        proba = model.predict_proba(posts["text"])
    elif hasattr(clf, "decision_function"):
        scores = model.decision_function(posts["text"])
        # Convert decision scores to probabilities via logistic transform.
        proba = 1 / (1 + np.exp(-scores))
    else:
        raise ValueError("Classifier does not support probability estimates or decision function.")

    predicted_binary = (proba >= probability_threshold).astype(int)
    predicted_tags = mlb.inverse_transform(predicted_binary)

    top_scores = np.argsort(-proba, axis=1)
    top_tags = []
    top_probs = []
    low_confidence_actual: List[List[str]] = []
    candidate_missing: List[List[str]] = []
    for row_idx, indices in enumerate(top_scores):
        tags = []
        probs = []
        for idx in indices[:5]:
            tags.append(mlb.classes_[idx])
            probs.append(float(proba[row_idx, idx]))
        top_tags.append(tags)
        top_probs.append(probs)

        actual_set = set(posts.loc[row_idx, "tags"])
        candidate_missing.append(sorted(list(set(tags) - actual_set)))

        row_low_conf = [
            mlb.classes_[idx]
            for idx in range(proba.shape[1])
            if mlb.classes_[idx] in actual_set and proba[row_idx, idx] < low_confidence_threshold
        ]
        low_confidence_actual.append(sorted(row_low_conf))

    comparison = posts.copy()
    comparison["predicted_tags"] = [list(tags) for tags in predicted_tags]
    comparison["top5_tags"] = top_tags
    comparison["top5_probs"] = top_probs
    comparison["candidate_missing_from_top5"] = candidate_missing
    comparison["low_confidence_actual_tags"] = low_confidence_actual

    actual_sets = comparison["tags"].apply(set)
    predicted_sets = comparison["predicted_tags"].apply(set)

    comparison["missing_tags"] = [
        sorted(list(predicted_sets.iloc[i] - actual_sets.iloc[i])) for i in range(len(comparison))
    ]
    comparison["potential_misapplied_tags"] = [
        sorted(list(actual_sets.iloc[i] - predicted_sets.iloc[i])) for i in range(len(comparison))
    ]
    comparison["has_tags"] = comparison["tags"].apply(bool)
    comparison["predicted_positive"] = predicted_binary.sum(axis=1)
    return comparison


def export_results(
    evaluation: pd.DataFrame,
    predictions: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Persist evaluation tables to disk."""

    output_dir.mkdir(parents=True, exist_ok=True)
    evaluation.to_csv(output_dir / "model_evaluation.csv", index=False)
    predictions.to_csv(output_dir / "tag_predictions.csv", index=False)

    # Filtered summaries
    tagged = predictions[predictions["has_tags"]]
    missing = tagged[tagged["missing_tags"].apply(len) > 0]
    misapplied = tagged[tagged["potential_misapplied_tags"].apply(len) > 0]
    candidate_missing = tagged[tagged["candidate_missing_from_top5"].apply(len) > 0]
    low_confidence = tagged[tagged["low_confidence_actual_tags"].apply(len) > 0]
    untagged = predictions[~predictions["has_tags"]]

    missing.to_csv(output_dir / "missing_tag_suggestions.csv", index=False)
    misapplied.to_csv(output_dir / "potential_misapplied_tags.csv", index=False)
    candidate_missing.to_csv(output_dir / "candidate_missing_from_top5.csv", index=False)
    low_confidence.to_csv(output_dir / "low_confidence_actual_tags.csv", index=False)
    untagged.to_csv(output_dir / "untagged_post_suggestions.csv", index=False)

    # Store metadata about total tags per post for quick review.
    summary = {
        "total_posts": int(len(predictions)),
        "tagged_posts": int(tagged.shape[0]),
        "untagged_posts": int(untagged.shape[0]),
        "unique_tags": predictions["tags"].explode().dropna().unique().tolist(),
        "candidate_missing_post_count": int(candidate_missing.shape[0]),
    }
    candidate_tag_counts = (
        candidate_missing["candidate_missing_from_top5"].explode().dropna().value_counts()
    )
    summary["candidate_missing_tag_counts"] = {
        str(tag): int(count) for tag, count in candidate_tag_counts.items()
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate tag prediction models.")
    parser.add_argument(
        "--posts-dir",
        type=Path,
        required=True,
        help="Path to ajfisher.me/site/src/content/posts directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Directory to write outputs.",
    )
    parser.add_argument(
        "--probability-threshold",
        type=float,
        default=0.5,
        help="Threshold for assigning predicted tags.",
    )
    parser.add_argument(
        "--low-confidence-threshold",
        type=float,
        default=0.2,
        help="Probability cutoff to flag existing tags as low-confidence.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    posts_dir = args.posts_dir
    output_dir = args.output_dir

    posts = load_posts(posts_dir)
    if not posts:
        raise SystemExit(f"No posts found in {posts_dir}")

    df_posts = pd.DataFrame([post.__dict__ for post in posts])
    df_posts["text"] = df_posts["text"].fillna("")

    tagged_posts = df_posts[df_posts["tags"].apply(bool)].reset_index(drop=True)
    if tagged_posts.empty:
        raise SystemExit("No tagged posts available for training.")

    X = tagged_posts["text"].tolist()
    mlb = MultiLabelBinarizer()
    Y = mlb.fit_transform(tagged_posts["tags"])

    scoring = {
        "f1_micro": metrics.make_scorer(metrics.f1_score, average="micro", zero_division=0),
        "f1_macro": metrics.make_scorer(metrics.f1_score, average="macro", zero_division=0),
        "precision_micro": metrics.make_scorer(metrics.precision_score, average="micro", zero_division=0),
        "recall_micro": metrics.make_scorer(metrics.recall_score, average="micro", zero_division=0),
        "subset_accuracy": metrics.make_scorer(metrics.accuracy_score),
    }

    models = build_models()
    label_counts = Y.sum(axis=0)
    evaluation_mask = label_counts >= 2
    if evaluation_mask.any():
        Y_eval = Y[:, evaluation_mask]
        eval_label_names = mlb.classes_[evaluation_mask]
    else:
        Y_eval = Y
        eval_label_names = mlb.classes_

    evaluation = evaluate_models(models, X, Y_eval, scoring)

    best_model_name = evaluation.iloc[0]["model"]
    best_model = models[best_model_name]

    predictions = suggest_tags(
        best_model,
        X,
        Y,
        df_posts,
        mlb,
        probability_threshold=args.probability_threshold,
        low_confidence_threshold=args.low_confidence_threshold,
    )

    export_results(evaluation, predictions, output_dir)

    # Also provide a concise text summary for quick inspection.
    summary_lines = [
        f"Selected model: {best_model_name}",
        "\nEvaluation metrics:",
    ]
    for _, row in evaluation.iterrows():
        summary_lines.append(
            (
                f"- {row['model']}: F1_micro={row['test_f1_micro']:.3f} ± {row['test_f1_micro_std']:.3f}, "
                f"F1_macro={row['test_f1_macro']:.3f}, SubsetAcc={row['test_subset_accuracy']:.3f}"
            )
        )

    summary_lines.append(
        f"\nTotal posts: {len(df_posts)}, Tagged: {len(tagged_posts)}, Untagged: {len(df_posts) - len(tagged_posts)}"
    )
    summary_lines.append(
        f"Labels evaluated: {len(eval_label_names)} of {len(mlb.classes_)} (>=2 positives)."
    )
    dropped_labels = sorted(set(mlb.classes_) - set(eval_label_names))
    if dropped_labels:
        preview = ", ".join(dropped_labels[:10])
        more = "..." if len(dropped_labels) > 10 else ""
        summary_lines.append(
            f"Labels excluded from CV due to rarity: {preview}{more}"
        )

    missing_count = int((predictions["missing_tags"].apply(len) > 0).sum())
    misapplied_count = int((predictions["potential_misapplied_tags"].apply(len) > 0).sum())
    candidate_missing_count = int((predictions["candidate_missing_from_top5"].apply(len) > 0).sum())
    low_confidence_count = int((predictions["low_confidence_actual_tags"].apply(len) > 0).sum())
    untagged_count = int((predictions["has_tags"] == False).sum())

    summary_lines.append(f"Posts with suggested missing tags: {missing_count}")
    summary_lines.append(f"Posts with potential misapplied tags: {misapplied_count}")
    summary_lines.append(
        f"Posts with high-probability candidate tags (top5): {candidate_missing_count}"
    )
    summary_lines.append(
        f"Posts with low-confidence existing tags (<{args.low_confidence_threshold:.2f} prob): {low_confidence_count}"
    )
    summary_lines.append(f"Untagged posts with suggestions: {untagged_count}")

    (output_dir / "summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
