import pytest

from glitchlings import Typogre, summon
from glitchlings.zoo.core import Gaggle


def test_gaggle_determinism(sample_text):
    g1 = summon(["reduple", "mim1c", "typogre", "rushmore", "redactyl"], seed=777)
    out1 = g1(sample_text)
    g2 = summon(["reduple", "mim1c", "typogre", "rushmore", "redactyl"], seed=777)
    out2 = g2(sample_text)
    assert out1 == out2


def test_gaggle_seed_changes_output(sample_text):
    g1 = summon(["reduple", "mim1c", "typogre", "rushmore", "redactyl"], seed=1)
    out1 = g1(sample_text)
    g2 = summon(["reduple", "mim1c", "typogre", "rushmore", "redactyl"], seed=2)
    out2 = g2(sample_text)
    assert out1 != out2


def test_gaggle_ordering_stable(sample_text):
    # When summoned by name, built-ins choose a stable order by scope, then order, then name
    gaggle = summon(["typogre", "mim1c", "reduple", "rushmore"], seed=42)
    expected = ["Reduple", "Rushmore", "Typogre", "Mim1c"]
    assert [member.name for member in gaggle.apply_order] == expected


def test_gaggle_seed_derivation_regression():
    assert Gaggle.derive_seed(151, "Typogre", 0) == 13006513535068165406
    assert Gaggle.derive_seed(151, "Redactyl", 3) == 12503957440331561761


def test_summon_accepts_parameterized_specification():
    gaggle = summon(["Typogre(rate=0.05)"], seed=151)
    assert len(gaggle.apply_order) == 1
    member = gaggle.apply_order[0]
    assert isinstance(member, Typogre)
    assert member.rate == 0.05
    assert member.max_change_rate == 0.05


def test_summon_rejects_positional_parameter_specifications():
    with pytest.raises(ValueError, match="keyword arguments"):
        summon(["Typogre(0.2)"])
