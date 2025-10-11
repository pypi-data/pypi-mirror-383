"""Tests for one-to-many node connections (fan-out patterns)."""

import pytest
from openworkflows import Workflow


@pytest.mark.asyncio
async def test_simple_fan_out():
    """Test one node output going to multiple nodes."""
    workflow = Workflow("Simple Fan Out")

    # One input feeds three different operations
    workflow.add_node("source", "input", {"name": "value"})
    workflow.add_node("add_op", "add", {})
    workflow.add_node("mult_op", "multiply", {})
    workflow.add_node("pass_op", "passthrough", {})

    workflow.add_node("c10", "input", {"name": "c10", "default": 10})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})

    # Source connects to all three operations
    workflow.connect("source.value", "add_op.a")
    workflow.connect("source.value", "mult_op.a")
    workflow.connect("source.value", "pass_op.input")

    workflow.connect("c10.value", "add_op.b")
    workflow.connect("c3.value", "mult_op.b")

    result = await workflow.run(inputs={"value": 5})

    assert result["add_op"]["result"] == 15  # 5 + 10
    assert result["mult_op"]["result"] == 15  # 5 * 3
    assert result["pass_op"]["output"] == 5  # 5


@pytest.mark.asyncio
async def test_split_node_to_multiple_targets():
    """Test explicit split node distributing to multiple targets."""
    workflow = Workflow("Split Node")

    workflow.add_node("input", "input", {"name": "data"})
    workflow.add_node("splitter", "split", {})
    workflow.add_node("proc1", "passthrough", {})
    workflow.add_node("proc2", "passthrough", {})
    workflow.add_node("proc3", "passthrough", {})

    # Split input to three outputs
    workflow.connect("input.value", "splitter.value")
    workflow.connect("splitter.out1", "proc1.input")
    workflow.connect("splitter.out2", "proc2.input")
    workflow.connect("splitter.out3", "proc3.input")

    result = await workflow.run(inputs={"data": "test_data"})

    assert result["proc1"]["output"] == "test_data"
    assert result["proc2"]["output"] == "test_data"
    assert result["proc3"]["output"] == "test_data"


@pytest.mark.asyncio
async def test_multi_level_fan_out():
    """Test fan-out at multiple levels of the workflow."""
    workflow = Workflow("Multi-Level Fan Out")

    # Level 1: input fans out to 2 nodes
    # Level 2: each of those fans out to 2 more nodes
    # Total: 1 -> 2 -> 4 nodes

    workflow.add_node("root", "input", {"name": "x"})

    # Level 1 fan-out
    workflow.add_node("l1_a", "add", {})
    workflow.add_node("l1_b", "multiply", {})

    workflow.add_node("c1", "input", {"name": "c1", "default": 1})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})

    workflow.connect("root.value", "l1_a.a")
    workflow.connect("c1.value", "l1_a.b")
    workflow.connect("root.value", "l1_b.a")
    workflow.connect("c2.value", "l1_b.b")

    # Level 2 fan-out from l1_a
    workflow.add_node("l2_a1", "multiply", {})
    workflow.add_node("l2_a2", "add", {})

    workflow.connect("l1_a.result", "l2_a1.a")
    workflow.connect("c2.value", "l2_a1.b")
    workflow.connect("l1_a.result", "l2_a2.a")
    workflow.connect("c1.value", "l2_a2.b")

    # Level 2 fan-out from l1_b
    workflow.add_node("l2_b1", "add", {})
    workflow.add_node("l2_b2", "multiply", {})

    workflow.connect("l1_b.result", "l2_b1.a")
    workflow.connect("c1.value", "l2_b1.b")
    workflow.connect("l1_b.result", "l2_b2.a")
    workflow.connect("c2.value", "l2_b2.b")

    result = await workflow.run(inputs={"x": 10})

    # Level 1
    assert result["l1_a"]["result"] == 11  # 10 + 1
    assert result["l1_b"]["result"] == 20  # 10 * 2

    # Level 2 from l1_a (11)
    assert result["l2_a1"]["result"] == 22  # 11 * 2
    assert result["l2_a2"]["result"] == 12  # 11 + 1

    # Level 2 from l1_b (20)
    assert result["l2_b1"]["result"] == 21  # 20 + 1
    assert result["l2_b2"]["result"] == 40  # 20 * 2


@pytest.mark.asyncio
async def test_fan_out_with_different_handle_connections():
    """Test one node output connecting to different input handles of multiple nodes."""
    workflow = Workflow("Fan Out Different Handles")

    workflow.add_node("source", "input", {"name": "base"})
    workflow.add_node("add1", "add", {})
    workflow.add_node("add2", "add", {})
    workflow.add_node("mult1", "multiply", {})

    workflow.add_node("c5", "input", {"name": "c5", "default": 5})
    workflow.add_node("c7", "input", {"name": "c7", "default": 7})

    # Source value goes to different handles
    workflow.connect("source.value", "add1.a")  # as first operand
    workflow.connect("c5.value", "add1.b")

    workflow.connect("c7.value", "add2.a")
    workflow.connect("source.value", "add2.b")  # as second operand

    workflow.connect("source.value", "mult1.a")  # as first operand
    workflow.connect("source.value", "mult1.b")  # as second operand (same value)

    result = await workflow.run(inputs={"base": 3})

    assert result["add1"]["result"] == 8  # 3 + 5
    assert result["add2"]["result"] == 10  # 7 + 3
    assert result["mult1"]["result"] == 9  # 3 * 3


@pytest.mark.asyncio
async def test_broadcast_to_many_similar_nodes():
    """Test broadcasting one value to many identical operation nodes."""
    workflow = Workflow("Broadcast Pattern")

    workflow.add_node("broadcaster", "input", {"name": "message"})

    # Create 5 passthrough nodes that all receive the same input
    for i in range(5):
        workflow.add_node(f"receiver_{i}", "passthrough", {})
        workflow.connect("broadcaster.value", f"receiver_{i}.input")

    result = await workflow.run(inputs={"message": "broadcast_value"})

    # Verify all receivers got the message
    for i in range(5):
        assert result[f"receiver_{i}"]["output"] == "broadcast_value"


@pytest.mark.asyncio
async def test_fan_out_then_converge():
    """Test fan-out followed by convergence (like MapReduce)."""
    workflow = Workflow("Fan Out Converge")

    # Input fans out to 3 operations, then all converge to sum
    workflow.add_node("input", "input", {"name": "x"})

    # Three parallel operations
    workflow.add_node("op1", "multiply", {})  # x * 2
    workflow.add_node("op2", "multiply", {})  # x * 3
    workflow.add_node("op3", "multiply", {})  # x * 4

    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.add_node("c4", "input", {"name": "c4", "default": 4})

    # Fan out
    workflow.connect("input.value", "op1.a")
    workflow.connect("c2.value", "op1.b")

    workflow.connect("input.value", "op2.a")
    workflow.connect("c3.value", "op2.b")

    workflow.connect("input.value", "op3.a")
    workflow.connect("c4.value", "op3.b")

    # Converge - sum all results
    workflow.add_node("sum", "merge_sum", {})
    workflow.connect("op1.result", "sum.input1")
    workflow.connect("op2.result", "sum.input2")
    workflow.connect("op3.result", "sum.input3")

    result = await workflow.run(inputs={"x": 5})

    # Verify parallel ops
    assert result["op1"]["result"] == 10  # 5 * 2
    assert result["op2"]["result"] == 15  # 5 * 3
    assert result["op3"]["result"] == 20  # 5 * 4

    # Verify convergence
    assert result["sum"]["result"] == 45  # 10 + 15 + 20
