"""Async inference engine running ML predictions in a background thread."""

from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np

from features.extractor import FEATURE_NAMES, features_to_vector
from .cache import PredictionCache


class PredictionResult:
    """Holds the result of a single prediction."""

    def __init__(self, function_name: str, start_line: int, end_line: int,
                 probability: float, label: str, features: dict,
                 feature_importances: dict):
        self.function_name = function_name
        self.start_line = start_line
        self.end_line = end_line
        self.probability = probability
        self.label = label
        self.features = features
        self.feature_importances = feature_importances

    def __repr__(self):
        return f"<Prediction {self.function_name}: {self.label} ({self.probability:.0%})>"


def classify_risk(probability: float) -> str:
    if probability <= 0.40:
        return "Low Risk"
    elif probability <= 0.70:
        return "Medium Risk"
    else:
        return "High Risk"


class PredictorWorker(QThread):
    """Runs ML inference on a list of functions in a background thread."""

    predictions_ready = pyqtSignal(list)  # List[PredictionResult]

    def __init__(self, model, functions_with_features, parent=None):
        super().__init__(parent)
        self._model = model
        self._functions_with_features = functions_with_features  # list of (FunctionInfo, features_dict)

    def run(self):
        results = []
        for func_info, features in self._functions_with_features:
            vector = features_to_vector(features)
            X = np.array([vector])

            try:
                proba = self._model.predict_proba(X)[0]
                bug_prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
            except Exception:
                bug_prob = 0.0

            label = classify_risk(bug_prob)

            # Feature importances from model
            importances = {}
            if hasattr(self._model, "feature_importances_"):
                fi = self._model.feature_importances_
                for i, name in enumerate(FEATURE_NAMES):
                    if i < len(fi):
                        importances[name] = float(fi[i])

            result = PredictionResult(
                function_name=func_info.name,
                start_line=func_info.start_line,
                end_line=func_info.end_line,
                probability=bug_prob,
                label=label,
                features=features,
                feature_importances=importances,
            )
            results.append(result)

        self.predictions_ready.emit(results)


class Predictor:
    """High-level predictor that manages cache and worker threads."""

    def __init__(self, model):
        self.model = model
        self.cache = PredictionCache()
        self._worker = None

    def predict_async(self, functions_with_features, callback):
        """Run predictions in background. Calls callback(results) when done.

        functions_with_features: list of (FunctionInfo, features_dict)
        """
        if self.model is None:
            return

        # Check cache and filter
        to_predict = []
        cached_results = []

        for func_info, features in functions_with_features:
            cached = self.cache.get(func_info.code)
            if cached:
                cached_results.append(cached)
            else:
                to_predict.append((func_info, features))

        if not to_predict:
            callback(cached_results)
            return

        self._worker = PredictorWorker(self.model, to_predict)

        def on_done(new_results):
            # Cache new results
            for i, result in enumerate(new_results):
                func_info = to_predict[i][0]
                self.cache.put(func_info.code, result)
            callback(cached_results + new_results)

        self._worker.predictions_ready.connect(on_done)
        self._worker.start()
