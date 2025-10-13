from bioelectea.modules.lca_engine import LCAEngine, LCAItem


def test_lca_engine_basic():
    eng = LCAEngine(
        [
            LCAItem("Electricity", 100, gwp_factor=0.45, ce_factor=0.0),
            LCAItem("Water", 1000, gwp_factor=0.0003, ce_factor=0.0),
        ]
    )
    res = eng.evaluate()
    assert res.total_gwp > 0
    assert len(res.breakdown) == 2
