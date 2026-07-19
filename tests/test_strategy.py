import pytest

from strategy import (
    InterleavedStrategy,
    RedundantStrategy,
    TransmissionStrategy,
)


def test_redundant_strategy_plan():
    strategy = RedundantStrategy(["A", "B", "C"], repeat=2)

    assert strategy.plan() == ["A", "A", "B", "B", "C", "C"]

def test_interleaved_strategy_plan():
    strategy = InterleavedStrategy(["A", "B", "C"], cycles=2)

    assert strategy.plan() == ["A", "B", "C", "A", "B", "C"]

def test_strategy_rejects_empty_packet_list():
    with pytest.raises(ValueError, match="packets cannot be empty"):
        RedundantStrategy([], repeat=2)