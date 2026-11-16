import unittest
from pathlib import Path
from types import SimpleNamespace

from M.i1_model_integration import I1ModelNotReady, I1QualityBundle


def model(factor, *, schema="shared-phi-test", fitted=True, prediction=None):
    artifact = {
        "space_id": "test-space",
        "feature_schema": schema,
        "feature_dimension": 2,
        "mean": [0.0, 0.0],
        "scale": [1.0, 1.0],
        "heads": {"peer_review": None, "later_community_use": None},
        "trained_until": "2023-12-31",
        "training_data_fingerprint": "fixture-training-fingerprint",
        "training_snapshot_ids": ["fixture-snapshot"],
    }
    artifact["heads"][factor] = {"coefficients": [0.0, 0.0], "intercept": 0.0} if fitted else None
    return SimpleNamespace(
        artifact=artifact,
        predict=lambda phi: {factor: {"prediction": prediction, "status": "unavailable"}},
    )


class I1QualityBundleTests(unittest.TestCase):
    def test_current_untrained_quality_output_is_rejected(self):
        with self.assertRaisesRegex(I1ModelNotReady, "missing quality model artifact"):
            I1QualityBundle.load(Path(__file__).resolve().parents[1] / "results/quality_v2")

    def test_both_fitted_heads_must_share_one_phi_schema(self):
        models = {
            "peer_review": model("peer_review"),
            "later_community_use": model("later_community_use", schema="different-phi"),
        }
        with self.assertRaisesRegex(I1ModelNotReady, "do not share one Phi"):
            I1QualityBundle(models, {factor: "a" * 64 for factor in models})

    def test_unavailable_factor_is_rejected(self):
        models = {
            "peer_review": model("peer_review"),
            "later_community_use": model("later_community_use", fitted=False),
        }
        with self.assertRaisesRegex(I1ModelNotReady, "unfitted quality head"):
            I1QualityBundle(models, {factor: "b" * 64 for factor in models})

    def test_feature_normalization_is_bound_per_factor_without_claiming_output_scale(self):
        models = {factor: model(factor) for factor in ("peer_review", "later_community_use")}
        models["later_community_use"].artifact["mean"] = [1.0, 1.0]
        bundle = I1QualityBundle(models, {factor: "c" * 64 for factor in models})
        peer = bundle.provenance["peer_review"]
        community = bundle.provenance["later_community_use"]
        self.assertEqual(peer["fit_split"], "TRAIN")
        self.assertNotEqual(peer["feature_statistics_sha256"], community["feature_statistics_sha256"])
        self.assertIsNone(peer["output_coordinate_normalization"])

    def test_unavailable_predictions_fail_closed(self):
        models = {factor: model(factor) for factor in ("peer_review", "later_community_use")}
        bundle = I1QualityBundle(models, {factor: "d" * 64 for factor in models})
        with self.assertRaisesRegex(I1ModelNotReady, "unavailable quality prediction"):
            bundle.predict(object())


if __name__ == "__main__":
    unittest.main()
