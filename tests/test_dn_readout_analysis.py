from bio_fly.dn_readout_analysis import behavior_hypothesis_for_family, classify_dn_family


def test_classify_dn_family_known_prefixes():
    assert classify_dn_family("DNge091") == "DNge"
    assert classify_dn_family("DNpe008") == "DNpe"
    assert classify_dn_family("DNg12_b") == "DNg"
    assert classify_dn_family("MDN") == "MDN_backward_walk"
    assert classify_dn_family("oviDNb") == "oviDN_reproductive_state"


def test_behavior_hypothesis_is_interpretable():
    assert "grooming" in behavior_hypothesis_for_family("DNge")
    assert "backward" in behavior_hypothesis_for_family("MDN_backward_walk")
    assert "requires targeted" in behavior_hypothesis_for_family("untyped_DN")
