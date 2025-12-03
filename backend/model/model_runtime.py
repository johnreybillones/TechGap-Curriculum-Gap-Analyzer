from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except ImportError as exc:  # pragma: no cover - caught at runtime if deps are missing
    raise RuntimeError(
        "PyTorch is required for running the siamese model; add torch to your environment."
    ) from exc

BASE_DIR = Path(__file__).parent

# Logistic Regression models (no more Naive Bayes)
LR_COARSE_MODEL_PATH = BASE_DIR / "techgap_lr_coarse.pkl"
LR_CLUSTERS_MODEL_PATH = BASE_DIR / "techgap_lr_clusters_kmeans.pkl"

# Siamese model (SBERT+projector) saved as state_dict (NOT TorchScript)
SIAMESE_MODEL_PATH = BASE_DIR / "techgap_siamese_kmeans.pth"

# Both LR and Siamese use 384-dim SBERT embeddings
EXPECTED_FEATURES = 384


# ==========================
# Siamese network definition
# (must match the training script)
# ==========================

class SiameseNetwork(nn.Module):
    def __init__(self, input_dim: int = 384, output_dim: int = 128):
        super().__init__()
        self.projector = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, output_dim),
        )

    def forward_one(self, x: torch.Tensor) -> torch.Tensor:
        """
        Project a batch of SBERT embeddings (batch, 384)
        into normalized embedding space (batch, 128).
        """
        x = self.projector(x)
        x = torch.nn.functional.normalize(x, p=2, dim=-1)
        return x

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        """
        Standard Siamese forward: returns two projected embeddings.
        Not used in runtime, but kept for completeness.
        """
        out1 = self.forward_one(x1)
        out2 = self.forward_one(x2)
        return out1, out2


# ==========================
# Helper: pull LR model out of tuple/dict
# ==========================

def _extract_prob_model(obj: Any):
    """
    Given the loaded object from joblib, return the classifier that has predict_proba.

    Handles cases where the file contains:
      - a single estimator, or
      - a tuple/dict like (model, label_encoder, kmeans_model), etc.
    """
    # Already a classifier
    if hasattr(obj, "predict_proba"):
        return obj

    # Tuple or list of things
    if isinstance(obj, (tuple, list)):
        for item in obj:
            if hasattr(item, "predict_proba"):
                return item

    # Dict of things
    if isinstance(obj, dict):
        for v in obj.values():
            if hasattr(v, "predict_proba"):
                return v

    raise TypeError("Could not find a model with predict_proba in the loaded object.")


# ==========================
# Model loaders
# ==========================

@lru_cache
def get_lr_coarse_model():
    if not LR_COARSE_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Logistic Regression (coarse) model not found at {LR_COARSE_MODEL_PATH}"
        )
    raw = joblib.load(LR_COARSE_MODEL_PATH)
    return _extract_prob_model(raw)


@lru_cache
def get_lr_clusters_model():
    if not LR_CLUSTERS_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Logistic Regression (clusters) model not found at {LR_CLUSTERS_MODEL_PATH}"
        )
    raw = joblib.load(LR_CLUSTERS_MODEL_PATH)
    return _extract_prob_model(raw)


@lru_cache
def get_siamese_model() -> SiameseNetwork:
    """
    Load SiameseNetwork from a state_dict saved via:
        torch.save(siamese_net.state_dict(), "techgap_siamese_kmeans.pth")

    This mirrors the architecture from your training script.
    """
    if not SIAMESE_MODEL_PATH.exists():
        raise FileNotFoundError(f"Siamese model not found at {SIAMESE_MODEL_PATH}")

    state_dict = torch.load(str(SIAMESE_MODEL_PATH), map_location="cpu")

    model = SiameseNetwork(input_dim=EXPECTED_FEATURES, output_dim=128)
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return model


# ==========================
# Utility
# ==========================

def _run_sklearn_feature_model(
    model: Any,
    features: list[float],
    model_name: str,
):
    """
    Shared helper for Logistic Regression models that take 384-dim feature vectors.
    """
    if len(features) != EXPECTED_FEATURES:
        raise ValueError(f"features must have length {EXPECTED_FEATURES}")

    x = np.array([features], dtype=np.float32)  # shape: (1, 384)
    proba = model.predict_proba(x)[0]
    classes = getattr(model, "classes_", None)
    top_idx = int(np.argmax(proba))
    label = classes[top_idx] if classes is not None else str(top_idx)

    return {
        "model_type": model_name,
        "label": str(label),
        "score": float(proba[top_idx]),
        "probabilities": proba.tolist(),
        "raw_output": proba.tolist(),
    }


# ==========================
# Public inference functions
# ==========================

def run_lr_coarse_inference(features: list[float]):
    """
    Inference for the coarse Logistic Regression model (real job-family labels).
    Input: 384-d SBERT embedding.
    """
    model = get_lr_coarse_model()
    return _run_sklearn_feature_model(model, features, "lr_coarse")


def run_lr_clusters_inference(features: list[float]):
    """
    Inference for the Logistic Regression model trained on KMeans clusters.
    Input: 384-d SBERT embedding.
    """
    model = get_lr_clusters_model()
    return _run_sklearn_feature_model(model, features, "lr_clusters")


def run_siamese_inference(features: list[float]):
    """
    Project a 384-d SBERT embedding through the Siamese projector.

    Returns:
      - embedding: the 128-d L2-normalized vector (for cosine similarity)
      - score: just the first element of the embedding (not a real similarity)
    """
    if len(features) != EXPECTED_FEATURES:
        raise ValueError(f"features must have length {EXPECTED_FEATURES}")

    model = get_siamese_model()
    x = torch.tensor([features], dtype=torch.float32)  # shape (1, 384)

    with torch.no_grad():
        emb = model.forward_one(x)  # (1, 128)

    emb_np = emb.squeeze(0).cpu().numpy()  # (128,)

    score = float(emb_np[0]) if emb_np.size else 0.0

    return {
        "model_type": "siamese",
        "score": score,               # you can ignore this and just use the embedding
        "raw_output": emb_np.tolist(),
        "embedding": emb_np.tolist(),
    }


def run_inference(
    model_type: str,
    *,
    features: list[float] | None = None,
):
    """
    Unified entry point for inference.

    Parameters
    ----------
    model_type:
        - "lr_coarse"   -> uses techgap_lr_coarse.pkl
        - "lr_clusters" -> uses techgap_lr_clusters_kmeans.pkl
        - "siamese"     -> uses techgap_siamese_kmeans.pth (state_dict)

    features:
        384-dimensional embedding (e.g., from SBERT / sentence-transformers).
    """
    if model_type == "lr_coarse":
        if features is None:
            raise ValueError("features are required for the lr_coarse model")
        return run_lr_coarse_inference(features)

    if model_type == "lr_clusters":
        if features is None:
            raise ValueError("features are required for the lr_clusters model")
        return run_lr_clusters_inference(features)

    if model_type == "siamese":
        if features is None:
            raise ValueError("features are required for the Siamese model")
        return run_siamese_inference(features)

    raise ValueError(f"Unsupported model_type '{model_type}'")


if __name__ == "__main__":
    # Minimal sanity check when running this file directly
    print("model_runtime loaded. Running a quick dummy test...")

    dummy_features = [0.0] * EXPECTED_FEATURES
    try:
        res_lr = run_inference("lr_coarse", features=dummy_features)
        print("Dummy lr_coarse result:", res_lr)
    except Exception as e:
        print("Error during lr_coarse dummy test:", e)

    try:
        res_siam = run_inference("siamese", features=dummy_features)
        print("Dummy siamese embedding length:", len(res_siam.get("embedding", [])))
    except Exception as e:
        print("Error during siamese dummy test:", e)