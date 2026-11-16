"""K2 reprend l'ajout de A, y compris sur une ligne déjà détenue."""
import math

import pytest

from alphaforge.moteurs.allocation import blend


@pytest.mark.parametrize("part", [-0.1, 1.1, float("nan"), float("inf")])
def test_part_hors_domaine_refusee(part):
    with pytest.raises(ValueError):
        blend({"XIU.TO": 1}, "TSLA", part)


def test_ajout_sur_ligne_deja_detenue_et_budget_sans_mutation():
    avant = {"TSLA": 0.2, "XIU.TO": 0.8}
    apres = blend(avant, "TSLA", 0.25)
    assert apres == pytest.approx({"TSLA": 0.4, "XIU.TO": 0.6})
    assert math.fsum(apres.values()) == pytest.approx(1)
    assert avant == {"TSLA": 0.2, "XIU.TO": 0.8}
    assert blend(avant, "TSLA", 0) == avant
    assert blend(avant, "TSLA", 1) == {"TSLA": 1}
