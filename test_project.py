from project import bond_price, bond_spread, bond_cr01, bond_ir01, get_settlement_date_from_trade_date, extract_date_from_string
import numpy as np
import datetime as dt


def test_bond_price():
    assert np.abs(bond_price(5, 0.04, 0.02, 0, 0.4) - 1.0951625819640405) < 1e-9
    assert np.abs(bond_price(5, 0.04, 0.02, 0.02, 0.4) - 1.0) < 1e-9
    assert np.abs(bond_price(5, 0.04, 0.04, 0.02, 0.4) - 0.9162838054781204) < 1e-9
    assert np.abs(bond_price(10, 0.07,  0.02, 0.05, 0.4) - 1.0) < 1e-9
    assert np.isnan(bond_price(10, 0.07, 0.0, 0.00, 0.4))

def test_bond_cr01():
    assert np.abs(bond_cr01(5, 0.04, 0.02, 0, 0.4) + 0.05148033004156449) < 1e-9
    assert np.abs(bond_cr01(5, 0.04, 0.02, 0.02, 0.4) + 0.043888441301065395) < 1e-9
    assert np.abs(bond_cr01(5, 0.04, 0.04, 0.02, 0.4) + 0.03858261682568864) < 1e-9
    assert np.abs(bond_cr01(10, 0.07, 0.02, 0.05, 0.4) + 0.06234012644289466) < 1e-9

def test_bond_ir01():
    assert np.abs(bond_ir01(5, 0.04, 0.02, 0, 0.4) + 0.049920713043494214) < 1e-9
    assert np.abs(bond_ir01(5, 0.04, 0.02, 0.02, 0.4) + 0.04388843826462763) < 1e-9
    assert np.abs(bond_ir01(5, 0.04, 0.04, 0.02, 0.4) + 0.03989280801128259) < 1e-9
    assert np.abs(bond_ir01(10, 0.07, 0.02, 0.05, 0.4) + 0.062340112500358646) < 1e-9

def test_bond_spread():
    assert np.max(
        np.abs(
        np.subtract(
            bond_spread([1,2,3,4,5,6,7,8,9,10], 0.05, 0.04, 90, 0.4),
            [0.12272492, 0.06806376, 0.04986697, 0.04078629, 0.03535207, 0.03174108, 0.02917192, 0.02725389, 0.02576993, 0.02458979]
            )
            )
        ) < 1e-6

    assert np.max(
        np.abs(
        np.subtract(
        bond_spread([1,2,3,4,5,6,7,8,9,10], 0.05, 0.04, [98, 96, 94, 92, 90, 88, 86, 84, 82, 80], 0.4),
        [0.03092946, 0.03192194, 0.03298433, 0.03412461, 0.03535207, 0.03667766, 0.03811435, 0.03967759, 0.04138602, 0.04326234]
        )
        )
    ) < 1e-6

def test_get_settlement_date_from_trade_date():
    assert get_settlement_date_from_trade_date(dt.date.fromisoformat('2023-08-13')) == dt.date.fromisoformat('2023-08-16')
    assert get_settlement_date_from_trade_date(dt.date.fromisoformat('2023-08-09')) == dt.date.fromisoformat('2023-08-11')

def test_extract_date_from_string():
    assert extract_date_from_string("12-08-2023") == dt.date(2023, 8, 12)
    assert extract_date_from_string("12/8/2023") == dt.date(2023, 8, 12)
    assert extract_date_from_string("12-08-23") is None
    assert extract_date_from_string("2023-08-12") is None
