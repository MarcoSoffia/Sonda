import pytest

from strategy import (
    InterleavedStrategy,
    RedundantStrategy,
    TransmissionStrategy,
)


def test_redundant_strategy_plan():
    strategy = RedundantStrategy(["A", "B", "C"], repeat=2)

    assert strategy.plan() == ["A", "A", "B", "B", "C", "C"]