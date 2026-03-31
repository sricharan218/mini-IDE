"""Train a RandomForest bug prediction model on synthetic data.

Run:  python -m train.train_model
This generates ml/models/bug_predictor.pkl
"""

import os
import sys
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Feature order must match features.extractor.FEATURE_NAMES
FEATURE_NAMES = [
    "lines_of_code",
    "function_length",
    "nesting_depth",
    "cyclomatic_complexity",
    "loop_count",
    "function_call_count",
    "variable_reuse",
    "exception_handling",
    "code_duplication",
    "import_count",
]

RANDOM_SEED = 42
N_SAMPLES = 5000


def generate_synthetic_data(n=N_SAMPLES):
    """Generate synthetic function-level metrics with bug labels.

    Heuristic: functions with high complexity, deep nesting, and many LOC
    are more likely to be buggy.
    """
    rng = np.random.RandomState(RANDOM_SEED)

    data = np.zeros((n, len(FEATURE_NAMES)))
    labels = np.zeros(n, dtype=int)

    for i in range(n):
        loc = rng.randint(3, 200)
        func_len = rng.randint(3, loc + 1)
        nesting = rng.randint(0, 8)
        complexity = rng.randint(1, 30)
        loops = rng.randint(0, 10)
        calls = rng.randint(0, 30)
        var_reuse = rng.randint(0, 15)
        exceptions = rng.randint(0, 5)
        duplication = rng.randint(0, 10)
        imports = rng.randint(0, 20)

        data[i] = [loc, func_len, nesting, complexity, loops,
                   calls, var_reuse, exceptions, duplication, imports]

        # Bug probability heuristic
        risk_score = (
            (complexity / 30) * 0.30 +
            (nesting / 8) * 0.20 +
            (loc / 200) * 0.15 +
            (loops / 10) * 0.10 +
            (duplication / 10) * 0.10 +
            (var_reuse / 15) * 0.08 +
            (1 - min(exceptions, 3) / 3) * 0.05 +
            (calls / 30) * 0.02
        )
        # Add noise
        risk_score += rng.normal(0, 0.1)
        risk_score = np.clip(risk_score, 0, 1)

        labels[i] = 1 if risk_score > 0.45 else 0

    return data, labels


def train():
    print("=" * 60)
    print("  ML Bug Predictor — Training")
    print("=" * 60)

    X, y = generate_synthetic_data()
    print(f"\nDataset: {len(X)} samples, {sum(y)} buggy ({sum(y)/len(y):.1%})")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Clean", "Buggy"]))

    # Feature importances
    print("Feature Importances:")
    for name, importance in sorted(
        zip(FEATURE_NAMES, model.feature_importances_), key=lambda x: -x[1]
    ):
        print(f"  {name:30s} {importance:.4f}")

    # Save model
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "bug_predictor.pkl")
    joblib.dump(model, model_path)
    print(f"\nModel saved to: {model_path}")
    print("=" * 60)

    return model


if __name__ == "__main__":
    train()
