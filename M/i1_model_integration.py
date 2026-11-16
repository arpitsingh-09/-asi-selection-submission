"""Strict adapter for the two separately fitted Q heads used by I1.

The quality trainer writes one artifact per factor, while ResearchSpace accepts
one object with ``predict(phi)``. This adapter composes those existing artifacts
without refitting, changing scales, or substituting an unavailable head.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from .quality import FACTORS, QualityModels
from .schema import date


class I1ModelNotReady(ValueError):
    """Required frozen quality artifacts or provenance are unavailable."""


def _normalization_provenance(artifact, artifact_sha256):
    stats = json.dumps(
        {"mean": artifact["mean"], "scale": artifact["scale"]},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return {
        "fit_split": "TRAIN",
        "method": "feature-wise z-score using TRAIN mean and standard deviation",
        "feature_statistics_sha256": hashlib.sha256(stats).hexdigest(),
        "training_data_fingerprint": artifact["training_data_fingerprint"],
        "training_snapshot_ids": list(artifact["training_snapshot_ids"]),
        "trained_until": artifact["trained_until"],
        "model_artifact_sha256": artifact_sha256,
        # Feature normalization is not an output-coordinate normalization.
        # No output transform is inferred for the registered I1 drift metric.
        "output_coordinate_normalization": artifact.get("output_coordinate_normalization"),
    }


class I1QualityBundle:
    """Present both trained factor models through the shared ResearchSpace API.

    Each factor retains the normalization fitted with its own eligible TRAIN
    rows. A single bundle instance should be attached to the ResearchSpace used
    for all I1 variants and input conditions.
    """

    def __init__(self, models, artifact_hashes):
        if set(models) != set(FACTORS) or set(artifact_hashes) != set(FACTORS):
            raise I1ModelNotReady("both Q factor artifacts are required")
        signatures = set()
        provenance = {}
        for factor in FACTORS:
            model = models[factor]
            artifact = model.artifact
            head = artifact.get("heads", {}).get(factor)
            if head is None:
                raise I1ModelNotReady("unfitted quality head: " + factor)
            if not artifact.get("training_data_fingerprint") or not artifact.get("training_snapshot_ids"):
                raise I1ModelNotReady("training provenance missing for " + factor)
            if date(artifact["trained_until"]) >= date("2024-01-01"):
                raise I1ModelNotReady("quality model includes post-2023 training labels")
            signatures.add((artifact["space_id"], artifact["feature_schema"], artifact["feature_dimension"]))
            provenance[factor] = _normalization_provenance(artifact, artifact_hashes[factor])
        if len(signatures) != 1:
            raise I1ModelNotReady("Q factor artifacts do not share one Phi representation")
        self.models = dict(models)
        self.provenance = provenance

    @classmethod
    def load(cls, model_dir):
        model_dir = Path(model_dir)
        models = {}
        hashes = {}
        for factor in FACTORS:
            path = model_dir / (factor + ".json")
            if not path.is_file():
                raise I1ModelNotReady("missing quality model artifact: " + str(path))
            body = path.read_bytes()
            hashes[factor] = hashlib.sha256(body).hexdigest()
            models[factor] = QualityModels.load(path)
        return cls(models, hashes)

    def predict(self, phi):
        """Return real fitted Q predictions and their per-factor provenance."""
        predictions = {}
        for factor in FACTORS:
            result = self.models[factor].predict(phi)[factor]
            value = result.get("prediction")
            if result.get("status", "").startswith("unavailable") or value is None:
                raise I1ModelNotReady("unavailable quality prediction: " + factor)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value):
                raise I1ModelNotReady("non-finite quality prediction: " + factor)
            predictions[factor] = {
                **result,
                "normalization_provenance": self.provenance[factor],
            }
        return predictions
