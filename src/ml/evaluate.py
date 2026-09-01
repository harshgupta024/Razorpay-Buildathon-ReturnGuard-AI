"""
ReturnGuard AI — Model Evaluation Module

Computes standard ML classification & probability metrics:
- ROC-AUC
- PR-AUC (Average Precision)
- Precision, Recall, F1 Score
- Accuracy & Specificity
- Brier Score & Log Loss
- Confusion Matrix breakdown

Usage:
    from src.ml.evaluate import evaluate_predictions, ModelEvaluationResult
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class ModelEvaluationResult:
    """Holds comprehensive evaluation metrics for a model."""
    model_name: str
    dataset_split: str
    total_samples: int
    positive_samples: int
    negative_samples: int
    base_rate: float
    threshold: float
    roc_auc: float
    pr_auc: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    specificity: float
    brier_score: float
    log_loss: float
    confusion_matrix: list[list[int]]  # [[TN, FP], [FN, TP]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary_table(self) -> str:
        lines = [
            f"| Metric | Value |",
            f"|:---|:---|",
            f"| **Model** | `{self.model_name}` |",
            f"| **Split** | `{self.dataset_split}` ({self.total_samples:,} samples) |",
            f"| **Decision Threshold** | `{self.threshold:.2f}` |",
            f"| **ROC-AUC** | **`{self.roc_auc:.4f}`** |",
            f"| **PR-AUC (Avg Precision)** | **`{self.pr_auc:.4f}`** |",
            f"| **F1 Score** | `{self.f1:.4f}` |",
            f"| **Precision** | `{self.precision:.4f}` |",
            f"| **Recall (Sensitivity)** | `{self.recall:.4f}` |",
            f"| **Specificity** | `{self.specificity:.4f}` |",
            f"| **Accuracy** | `{self.accuracy:.4f}` |",
            f"| **Brier Score** | `{self.brier_score:.4f}` |",
            f"| **Log Loss** | `{self.log_loss:.4f}` |",
            "",
            "#### Confusion Matrix",
            f"```",
            f"                Predicted 0     Predicted 1",
            f"Actual 0 (No)   TN = {self.confusion_matrix[0][0]:<8} FP = {self.confusion_matrix[0][1]:<8}",
            f"Actual 1 (Yes)  FN = {self.confusion_matrix[1][0]:<8} TP = {self.confusion_matrix[1][1]:<8}",
            f"```",
        ]
        return "\n".join(lines)


def evaluate_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    model_name: str = "Model",
    dataset_split: str = "Validation",
    threshold: float = 0.5,
) -> ModelEvaluationResult:
    """Compute all evaluation metrics given true labels and predicted probabilities."""
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    y_pred = (y_prob >= threshold).astype(int)

    total_samples = len(y_true)
    positive_samples = int(np.sum(y_true))
    negative_samples = total_samples - positive_samples
    base_rate = positive_samples / total_samples if total_samples > 0 else 0.0

    # Classification metrics
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    # Probability ranking & calibration metrics
    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = base_rate

    brier = float(brier_score_loss(y_true, y_prob))

    try:
        ll = float(log_loss(y_true, y_prob))
    except Exception:
        ll = 0.0

    return ModelEvaluationResult(
        model_name=model_name,
        dataset_split=dataset_split,
        total_samples=total_samples,
        positive_samples=positive_samples,
        negative_samples=negative_samples,
        base_rate=base_rate,
        threshold=threshold,
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        accuracy=acc,
        precision=prec,
        recall=rec,
        f1=f1,
        specificity=specificity,
        brier_score=brier,
        log_loss=ll,
        confusion_matrix=[[int(tn), int(fp)], [int(fn), int(tp)]],
    )
