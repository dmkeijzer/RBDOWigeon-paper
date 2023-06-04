import sys
import pathlib as pl
import  numpy as np

sys.path.append(str(list(pl.Path(__file__).parents)[2]))

from Validation_analysis.rv_handler import RandVar


def test_randvar():
    test_arr = np.random.randn(8000)
    test_instance = RandVar(test_arr)

    ppf_test = test_instance.ppf(0.5)
    expect_test = test_instance.get_expectation()
    std_test = test_instance.get_std()

    assert np.isclose(ppf_test, 0., atol= 2e-2)
    assert np.isclose(expect_test, 0., atol= 2e-2)
    assert np.isclose(std_test, 1., atol= 2e-2)


