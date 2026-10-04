"""Tests for the configured ATT&CK skill space."""
from adapt.mitre.skill_space import SkillSpace
from adapt.schemas import AttackTechnique


def test_skill_space_indexes_by_id_and_tactic():
    credential = AttackTechnique(technique_id="T1558", name="Kerberos Tickets", tactic="credential-access")
    discovery = AttackTechnique(technique_id="T1046", name="Service Discovery", tactic="discovery")
    space = SkillSpace([credential, discovery, credential])

    assert space.by_id("T1558") == credential
    assert space.by_tactic("discovery") == [discovery]
    assert space.techniques == [credential, discovery]


def test_skill_space_can_apply_tactic_allowlist(tmp_path):
    config = tmp_path / "mitre.yaml"
    config.write_text("tactics:\n  - discovery\n", encoding="utf-8")
    techniques = [
        AttackTechnique(technique_id="T1558", name="Kerberos Tickets", tactic="credential-access"),
        AttackTechnique(technique_id="T1046", name="Service Discovery", tactic="discovery"),
    ]

    space = SkillSpace.from_config(techniques, config)
    assert [technique.technique_id for technique in space.techniques] == ["T1046"]
