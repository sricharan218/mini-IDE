"""Loads the pre-trained ML model at IDE startup."""

import os
import joblib


_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
_DEFAULT_MODEL = os.path.join(_MODEL_DIR, "bug_predictor.pkl")


def load_model(path: str = None):
    """Load a scikit-learn model from disk.

    Returns the model object, or None if the file doesn't exist.
    """
    path = path or _DEFAULT_MODEL
    if not os.path.isfile(path):
        print(f"[ModelLoader] WARNING: Model not found at {path}")
        return None
    model = joblib.load(path)
    print(f"[ModelLoader] Loaded model from {path}")
    return model


def get_default_model_path() -> str:
    return _DEFAULT_MODEL
