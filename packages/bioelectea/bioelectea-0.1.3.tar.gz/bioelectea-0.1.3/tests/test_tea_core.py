from bioelectea.modules.tea_core import TEACore, TEAInput


def test_tea_core_basic():
    p = TEAInput(years=3, discount_rate=0.1, capex=1000, opex_yearly=100, revenue_yearly=300)
    res = TEACore(p).run()
    assert len(res.cashflows) == 4  # t0 + 3 years
    assert res.npv != 0
