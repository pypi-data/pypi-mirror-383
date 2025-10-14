"""
Medical-specific evaluation metrics

Implements metrics used in medical NLP competitions
"""

from typing import Dict, List, Any
import numpy as np


class MedicalMetrics:
    """
    Evaluation metrics for medical data extraction

    Supports:
    - F1 score (micro, macro, weighted)
    - Accuracy
    - Precision/Recall
    - Domain-specific metrics
    """

    @staticmethod
    def calculate_f1(
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]],
        average: str = "weighted"
    ) -> float:
        """
        Calculate F1 score for medical extraction

        Args:
            predictions: List of predicted extractions
            ground_truth: List of ground truth labels
            average: "micro", "macro", or "weighted"

        Returns:
            F1 score (0-1)
        """
        if not predictions or not ground_truth:
            return 0.0

        # Calculate per-field F1
        field_scores = {}

        for field in ["temperature", "symptoms", "medications"]:
            precision = MedicalMetrics._calculate_precision(
                predictions, ground_truth, field
            )
            recall = MedicalMetrics._calculate_recall(
                predictions, ground_truth, field
            )

            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0.0

            field_scores[field] = f1

        # Average
        if average == "macro":
            return np.mean(list(field_scores.values()))
        elif average == "weighted":
            # Weight by frequency in ground truth
            weights = MedicalMetrics._calculate_field_weights(ground_truth)
            weighted_sum = sum(f1 * weights.get(field, 0)
                             for field, f1 in field_scores.items())
            return weighted_sum
        else:  # micro
            # Calculate globally
            total_tp = sum(MedicalMetrics._count_tp(predictions, ground_truth, field)
                          for field in field_scores.keys())
            total_fp = sum(MedicalMetrics._count_fp(predictions, ground_truth, field)
                          for field in field_scores.keys())
            total_fn = sum(MedicalMetrics._count_fn(predictions, ground_truth, field)
                          for field in field_scores.keys())

            precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
            recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0

            if precision + recall > 0:
                return 2 * (precision * recall) / (precision + recall)
            return 0.0

    @staticmethod
    def _calculate_precision(predictions, ground_truth, field):
        """Calculate precision for a specific field"""
        tp = MedicalMetrics._count_tp(predictions, ground_truth, field)
        fp = MedicalMetrics._count_fp(predictions, ground_truth, field)
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0

    @staticmethod
    def _calculate_recall(predictions, ground_truth, field):
        """Calculate recall for a specific field"""
        tp = MedicalMetrics._count_tp(predictions, ground_truth, field)
        fn = MedicalMetrics._count_fn(predictions, ground_truth, field)
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0

    @staticmethod
    def _count_tp(predictions, ground_truth, field):
        """Count true positives"""
        tp = 0
        for pred, gt in zip(predictions, ground_truth):
            pred_val = pred.get(field)
            gt_val = gt.get(field)

            if pred_val is None or gt_val is None:
                continue

            if MedicalMetrics._values_match(pred_val, gt_val, field):
                tp += 1

        return tp

    @staticmethod
    def _count_fp(predictions, ground_truth, field):
        """Count false positives"""
        fp = 0
        for pred, gt in zip(predictions, ground_truth):
            pred_val = pred.get(field)
            gt_val = gt.get(field)

            if pred_val is not None and (gt_val is None or not MedicalMetrics._values_match(pred_val, gt_val, field)):
                fp += 1

        return fp

    @staticmethod
    def _count_fn(predictions, ground_truth, field):
        """Count false negatives"""
        fn = 0
        for pred, gt in zip(predictions, ground_truth):
            pred_val = pred.get(field)
            gt_val = gt.get(field)

            if gt_val is not None and (pred_val is None or not MedicalMetrics._values_match(pred_val, gt_val, field)):
                fn += 1

        return fn

    @staticmethod
    def _values_match(pred_val, gt_val, field):
        """Check if predicted and ground truth values match"""
        if field == "temperature":
            # For temperature, check classification
            if isinstance(pred_val, dict) and isinstance(gt_val, dict):
                return pred_val.get("classification") == gt_val.get("classification")
            return pred_val == gt_val

        elif field == "symptoms":
            # For symptoms, check if symptom lists match
            if isinstance(pred_val, list) and isinstance(gt_val, list):
                pred_symptoms = set(s["symptom"] if isinstance(s, dict) else s for s in pred_val)
                gt_symptoms = set(s["symptom"] if isinstance(s, dict) else s for s in gt_val)
                return pred_symptoms == gt_symptoms
            return pred_val == gt_val

        elif field == "medications":
            # For medications, check medication names
            if isinstance(pred_val, list) and isinstance(gt_val, list):
                pred_meds = set(m["name"] if isinstance(m, dict) else m for m in pred_val)
                gt_meds = set(m["name"] if isinstance(m, dict) else m for m in gt_val)
                return pred_meds == gt_meds
            return pred_val == gt_val

        else:
            return pred_val == gt_val

    @staticmethod
    def _calculate_field_weights(ground_truth):
        """Calculate weights based on field frequency"""
        field_counts = {"temperature": 0, "symptoms": 0, "medications": 0}

        for gt in ground_truth:
            for field in field_counts.keys():
                if gt.get(field) is not None:
                    field_counts[field] += 1

        total = sum(field_counts.values())
        if total == 0:
            return {field: 1.0/3 for field in field_counts.keys()}

        return {field: count / total for field, count in field_counts.items()}

    @staticmethod
    def temperature_accuracy(predictions, ground_truth) -> float:
        """Specialized accuracy for temperature classification"""
        correct = 0
        total = 0

        for pred, gt in zip(predictions, ground_truth):
            pred_temp = pred.get("temperature", {})
            gt_temp = gt.get("temperature", {})

            if gt_temp and gt_temp.get("classification"):
                total += 1
                pred_class = pred_temp.get("classification") if pred_temp else None
                gt_class = gt_temp.get("classification")

                if pred_class == gt_class:
                    correct += 1

        return correct / total if total > 0 else 0.0

    @staticmethod
    def symptom_f1(predictions, ground_truth) -> float:
        """Specialized F1 for symptom extraction"""
        return MedicalMetrics.calculate_f1(
            predictions, ground_truth, average="macro"
        )

    @staticmethod
    def evaluate_all(predictions, ground_truth) -> Dict[str, float]:
        """
        Comprehensive evaluation

        Returns dict with all metrics
        """
        return {
            "overall_f1": MedicalMetrics.calculate_f1(predictions, ground_truth, "weighted"),
            "temperature_accuracy": MedicalMetrics.temperature_accuracy(predictions, ground_truth),
            "symptom_f1": MedicalMetrics.symptom_f1(predictions, ground_truth),
            "macro_f1": MedicalMetrics.calculate_f1(predictions, ground_truth, "macro"),
            "micro_f1": MedicalMetrics.calculate_f1(predictions, ground_truth, "micro"),
        }
