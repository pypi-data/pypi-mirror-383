import pytest

from critical_es_value import linreg


@pytest.mark.parametrize(
    "alternative, confidence, variant, expected, match",
    [
        ("two-sided", 0.95, "ttest", [2.188362006, 0.441676723, 0.5405672546], None),
        (
            "invalid",
            0.95,
            "ttest",
            None,
            r"alternative must be one of 'two-sided', 'greater', or 'less'",
        ),
        ("two-sided", 1.5, "ttest", None, r"confidence must be in \(0, 1\)"),
        (
            "two-sided",
            0.95,
            "invalid",
            None,
            r"variant must be one of 'ttest' or 'ztest'",
        ),
    ],
)
def test_critical_for_linear_regression(
    test_dataset4, alternative, confidence, variant, expected, match
):
    X = test_dataset4[["x1", "x2"]]
    y = test_dataset4["y"]

    if match:
        with pytest.raises(ValueError, match=match):
            linreg.critical_for_linear_regression(
                X=X,
                y=y,
                alternative=alternative,
                confidence=confidence,
                variant=variant,
            )
    else:
        result = linreg.critical_for_linear_regression(
            X=X,
            y=y,
            alternative=alternative,
            confidence=confidence,
            variant=variant,
        )
        for c_ex, c_act in zip(expected, result["coef_critical"]):
            assert pytest.approx(c_ex) == c_act
