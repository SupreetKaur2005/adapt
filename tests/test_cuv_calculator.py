"""Tests for `adapt.routing.cuv_calculator`."""
from adapt.routing.cuv_calculator import compute_cuv
from adapt.schemas import AttackTechnique


def test_compute_cuv_returns_positive_float():
    technique = AttackTechnique(
        technique_id="T1558", name="Kerberoasting", tactic="credential-access"
    )
    score = compute_cuv("roast a kerberos ticket on dc01", technique, "qwen2.5:0.5b")
    assert isinstance(score, float)
    assert score > 0


def test_compute_cuv_unknown_model_raises():
    technique = AttackTechnique(technique_id="T1046", name="recon", tactic="discovery")
    try:
        compute_cuv("scan ws01", technique, "not-a-real-model")
    except ValueError as e:
        assert "not found" in str(e)
    else:
        raise AssertionError("expected ValueError for unknown model")
