"""Tests for `adapt.memory.csim_store`."""
from adapt.memory.csim_store import commit, query_similar
from adapt.schemas import AttackTechnique, ExploitAttempt


def test_csim_store_commit_and_query():
    tech = AttackTechnique(
        technique_id="T1558",
        name="Steal or Forge Kerberos Tickets",
        tactic="credential-access",
    )
    exploit = ExploitAttempt(
        subtask="request kerberos TGS ticket for spn krbtgt",
        technique=tech,
        payload="kerberoast payload",
        model_used="mistral:7b",
    )
    patch = {"file_path": "krb5.conf", "diff": "+aes256"}

    commit(exploit, patch)

    # Query similar subtask
    results = query_similar("kerberos ticket request")
    assert len(results) >= 1
    assert results[0].outcome == "PASS"
    assert results[0].exploit.technique.technique_id == "T1558"
    assert results[0].patch == patch


def test_csim_store_query_empty():
    results = query_similar("")
    assert results == []
