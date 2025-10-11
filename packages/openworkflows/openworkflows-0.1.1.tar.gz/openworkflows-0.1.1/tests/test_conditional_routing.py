"""Tests for conditional routing and dynamic path selection."""

import pytest
from openworkflows import Workflow


@pytest.mark.asyncio
async def test_basic_conditional_routing():
    """Test basic conditional routing based on threshold."""
    workflow = Workflow("Basic Conditional")

    workflow.add_node("input", "input", {"name": "value"})
    workflow.add_node("router", "conditional", {"threshold": 50})

    # High path
    workflow.add_node("high_proc", "multiply", {})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.connect("router.high", "high_proc.a")
    workflow.connect("c2.value", "high_proc.b")

    # Low path
    workflow.add_node("low_proc", "add", {})
    workflow.add_node("c10", "input", {"name": "c10", "default": 10})
    workflow.connect("router.low", "low_proc.a")
    workflow.connect("c10.value", "low_proc.b")

    workflow.connect("input.value", "router.value")

    # Test high value
    result_high = await workflow.run(inputs={"value": 75})
    assert result_high["router"]["high"] == 75
    assert result_high["router"]["low"] == 0
    assert result_high["high_proc"]["result"] == 150  # 75 * 2
    # low_proc gets 0, so result is 10
    assert result_high["low_proc"]["result"] == 10

    # Test low value
    result_low = await workflow.run(inputs={"value": 25})
    assert result_low["router"]["high"] == 0
    assert result_low["router"]["low"] == 25
    # high_proc gets 0, so result is 0
    assert result_low["high_proc"]["result"] == 0
    assert result_low["low_proc"]["result"] == 35  # 25 + 10


@pytest.mark.asyncio
async def test_conditional_with_convergence():
    """Test conditional routing that converges back to a single node."""
    workflow = Workflow("Conditional with Convergence")

    workflow.add_node("input", "input", {"name": "score"})
    workflow.add_node("router", "conditional", {"threshold": 70})

    # High score path - bonus multiplier
    workflow.add_node("high_bonus", "multiply", {})
    workflow.add_node("bonus_mult", "input", {"name": "bonus", "default": 1.5})

    # Low score path - penalty divider
    workflow.add_node("low_penalty", "multiply", {})
    workflow.add_node("penalty_mult", "input", {"name": "penalty", "default": 0.8})

    workflow.connect("input.value", "router.value")
    workflow.connect("router.high", "high_bonus.a")
    workflow.connect("bonus_mult.value", "high_bonus.b")
    workflow.connect("router.low", "low_penalty.a")
    workflow.connect("penalty_mult.value", "low_penalty.b")

    # Converge to final score (sum of both paths, only one will be non-zero)
    workflow.add_node("final", "add", {})
    workflow.connect("high_bonus.result", "final.a")
    workflow.connect("low_penalty.result", "final.b")

    # Test high score
    result_high = await workflow.run(inputs={"score": 85})
    assert result_high["final"]["result"] == 127.5  # 85 * 1.5 + 0

    # Test low score
    result_low = await workflow.run(inputs={"score": 45})
    assert result_low["final"]["result"] == 36.0  # 0 + 45 * 0.8


@pytest.mark.asyncio
async def test_multi_stage_conditional():
    """Test multiple conditional routing stages in sequence."""
    workflow = Workflow("Multi-Stage Conditional")

    workflow.add_node("input", "input", {"name": "x"})

    # First stage conditional
    workflow.add_node("stage1", "conditional", {"threshold": 50})

    # Second stage conditionals for each path
    workflow.add_node("stage2_high", "conditional", {"threshold": 75})
    workflow.add_node("stage2_low", "conditional", {"threshold": 25})

    workflow.connect("input.value", "stage1.value")
    workflow.connect("stage1.high", "stage2_high.value")
    workflow.connect("stage1.low", "stage2_low.value")

    # Final processors for each leaf path
    workflow.add_node("very_high", "passthrough", {})
    workflow.add_node("med_high", "passthrough", {})
    workflow.add_node("med_low", "passthrough", {})
    workflow.add_node("very_low", "passthrough", {})

    workflow.connect("stage2_high.high", "very_high.input")
    workflow.connect("stage2_high.low", "med_high.input")
    workflow.connect("stage2_low.high", "med_low.input")
    workflow.connect("stage2_low.low", "very_low.input")

    # Test very high (> 75)
    result = await workflow.run(inputs={"x": 90})
    assert result["very_high"]["output"] == 90
    assert result["med_high"]["output"] == 0  # Conditional returns 0 for non-taken path
    assert result["med_low"]["output"] == 0
    assert result["very_low"]["output"] == 0

    # Test med high (50-75)
    result = await workflow.run(inputs={"x": 60})
    assert result["very_high"]["output"] == 0
    assert result["med_high"]["output"] == 60

    # Test med low (25-50)
    result = await workflow.run(inputs={"x": 35})
    assert result["med_low"]["output"] == 35

    # Test very low (< 25)
    result = await workflow.run(inputs={"x": 15})
    assert result["very_low"]["output"] == 15


@pytest.mark.asyncio
async def test_conditional_fan_out():
    """Test conditional routing followed by fan-out on each branch."""
    workflow = Workflow("Conditional Fan Out")

    workflow.add_node("input", "input", {"name": "val"})
    workflow.add_node("router", "conditional", {"threshold": 100})

    workflow.connect("input.value", "router.value")

    # High path fans out to 2 operations
    workflow.add_node("high_op1", "multiply", {})
    workflow.add_node("high_op2", "add", {})

    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c5", "input", {"name": "c5", "default": 5})

    workflow.connect("router.high", "high_op1.a")
    workflow.connect("c2.value", "high_op1.b")
    workflow.connect("router.high", "high_op2.a")
    workflow.connect("c5.value", "high_op2.b")

    # Low path fans out to 2 operations
    workflow.add_node("low_op1", "multiply", {})
    workflow.add_node("low_op2", "add", {})

    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.add_node("c10", "input", {"name": "c10", "default": 10})

    workflow.connect("router.low", "low_op1.a")
    workflow.connect("c3.value", "low_op1.b")
    workflow.connect("router.low", "low_op2.a")
    workflow.connect("c10.value", "low_op2.b")

    # Test high path
    result_high = await workflow.run(inputs={"val": 150})
    assert result_high["high_op1"]["result"] == 300  # 150 * 2
    assert result_high["high_op2"]["result"] == 155  # 150 + 5
    assert result_high["low_op1"]["result"] == 0  # 0 * 3
    assert result_high["low_op2"]["result"] == 10  # 0 + 10

    # Test low path
    result_low = await workflow.run(inputs={"val": 50})
    assert result_low["high_op1"]["result"] == 0  # 0 * 2
    assert result_low["high_op2"]["result"] == 5  # 0 + 5
    assert result_low["low_op1"]["result"] == 150  # 50 * 3
    assert result_low["low_op2"]["result"] == 60  # 50 + 10


@pytest.mark.asyncio
async def test_parallel_conditionals():
    """Test multiple independent conditional routers in parallel."""
    workflow = Workflow("Parallel Conditionals")

    # Two independent inputs with their own conditionals
    workflow.add_node("input_a", "input", {"name": "a"})
    workflow.add_node("input_b", "input", {"name": "b"})

    workflow.add_node("router_a", "conditional", {"threshold": 50})
    workflow.add_node("router_b", "conditional", {"threshold": 30})

    workflow.connect("input_a.value", "router_a.value")
    workflow.connect("input_b.value", "router_b.value")

    # Outputs for each path
    workflow.add_node("a_high", "passthrough", {})
    workflow.add_node("a_low", "passthrough", {})
    workflow.add_node("b_high", "passthrough", {})
    workflow.add_node("b_low", "passthrough", {})

    workflow.connect("router_a.high", "a_high.input")
    workflow.connect("router_a.low", "a_low.input")
    workflow.connect("router_b.high", "b_high.input")
    workflow.connect("router_b.low", "b_low.input")

    # Test all combinations
    result = await workflow.run(inputs={"a": 60, "b": 40})
    assert result["a_high"]["output"] == 60
    assert result["b_high"]["output"] == 40

    result = await workflow.run(inputs={"a": 60, "b": 20})
    assert result["a_high"]["output"] == 60
    assert result["b_low"]["output"] == 20

    result = await workflow.run(inputs={"a": 40, "b": 40})
    assert result["a_low"]["output"] == 40
    assert result["b_high"]["output"] == 40

    result = await workflow.run(inputs={"a": 40, "b": 20})
    assert result["a_low"]["output"] == 40
    assert result["b_low"]["output"] == 20


@pytest.mark.asyncio
async def test_conditional_with_both_paths_used():
    """Test that both conditional outputs can be used independently."""
    workflow = Workflow("Both Paths Active")

    workflow.add_node("input", "input", {"name": "value"})
    workflow.add_node("router", "conditional", {"threshold": 60})

    workflow.connect("input.value", "router.value")

    # Both outputs are used - one for each separate computation
    workflow.add_node("high_result", "passthrough", {})
    workflow.add_node("low_result", "passthrough", {})

    workflow.connect("router.high", "high_result.input")
    workflow.connect("router.low", "low_result.input")

    # Also use the main result output
    workflow.add_node("main_result", "passthrough", {})
    workflow.connect("router.result", "main_result.input")

    # Test with high value
    result = await workflow.run(inputs={"value": 80})
    assert result["main_result"]["output"] == 80
    assert result["high_result"]["output"] == 80
    assert result["low_result"]["output"] == 0

    # Test with low value
    result = await workflow.run(inputs={"value": 40})
    assert result["main_result"]["output"] == 40
    assert result["high_result"]["output"] == 0
    assert result["low_result"]["output"] == 40
