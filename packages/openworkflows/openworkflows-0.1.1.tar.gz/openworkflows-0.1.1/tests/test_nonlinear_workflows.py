"""Tests for nonlinear workflow execution patterns."""

import pytest
from openworkflows import Workflow


@pytest.mark.asyncio
async def test_diamond_pattern():
    """Test diamond pattern: A -> B,C -> D

    One node splits to multiple paths that converge back.
    """
    workflow = Workflow("Diamond Pattern")

    # Create diamond pattern
    #     input (10)
    #      /    \
    #   add(+5) mult(x2)
    #      \    /
    #      add (sum)

    workflow.add_node("input", "input", {"name": "value"})
    workflow.add_node("add1", "add", {})
    workflow.add_node("mult1", "multiply", {})
    workflow.add_node("final_add", "add", {})

    # Input goes to both add and multiply
    workflow.connect("input.value", "add1.a")
    workflow.connect("input.value", "mult1.a")

    # Constants for operations
    workflow.add_node("const5", "input", {"name": "constant", "default": 5})
    workflow.add_node("const2", "input", {"name": "multiplier", "default": 2})

    workflow.connect("const5.value", "add1.b")
    workflow.connect("const2.value", "mult1.b")

    # Both results go to final add
    workflow.connect("add1.result", "final_add.a")
    workflow.connect("mult1.result", "final_add.b")

    # Run workflow
    result = await workflow.run(inputs={"value": 10})

    # Verify: (10 + 5) + (10 * 2) = 15 + 20 = 35
    assert result["add1"]["result"] == 15
    assert result["mult1"]["result"] == 20
    assert result["final_add"]["result"] == 35


@pytest.mark.asyncio
async def test_complex_branching():
    """Test complex branching with multiple levels.

    A -> B -> C -> E
         |    |
         v    v
         D    D
    """
    workflow = Workflow("Complex Branching")

    workflow.add_node("start", "input", {"name": "x"})
    workflow.add_node("step1", "multiply", {})  # x * 2
    workflow.add_node("step2", "add", {})  # result + 3
    workflow.add_node("branch1", "multiply", {})  # step1 * 2
    workflow.add_node("branch2", "add", {})  # step2 + step1

    workflow.add_node("const2", "input", {"name": "const2", "default": 2})
    workflow.add_node("const3", "input", {"name": "const3", "default": 3})

    # Main path: start -> step1 -> step2
    workflow.connect("start.value", "step1.a")
    workflow.connect("const2.value", "step1.b")
    workflow.connect("step1.result", "step2.a")
    workflow.connect("const3.value", "step2.b")

    # Branch 1: step1 -> branch1
    workflow.connect("step1.result", "branch1.a")
    workflow.connect("const2.value", "branch1.b")

    # Branch 2: step2 + step1 -> branch2
    workflow.connect("step2.result", "branch2.a")
    workflow.connect("step1.result", "branch2.b")

    result = await workflow.run(inputs={"x": 5})

    # Verify calculations
    assert result["step1"]["result"] == 10  # 5 * 2
    assert result["step2"]["result"] == 13  # 10 + 3
    assert result["branch1"]["result"] == 20  # 10 * 2
    assert result["branch2"]["result"] == 23  # 13 + 10


@pytest.mark.asyncio
async def test_parallel_independent_paths():
    """Test multiple independent parallel paths in the same workflow."""
    workflow = Workflow("Parallel Paths")

    # Path 1: x -> x*2 -> x*2+5
    workflow.add_node("x", "input", {"name": "x"})
    workflow.add_node("mult_x", "multiply", {})
    workflow.add_node("add_x", "add", {})

    # Path 2: y -> y+3 -> (y+3)*4
    workflow.add_node("y", "input", {"name": "y"})
    workflow.add_node("add_y", "add", {})
    workflow.add_node("mult_y", "multiply", {})

    # Constants
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.add_node("c4", "input", {"name": "c4", "default": 4})
    workflow.add_node("c5", "input", {"name": "c5", "default": 5})

    # Path 1 connections
    workflow.connect("x.value", "mult_x.a")
    workflow.connect("c2.value", "mult_x.b")
    workflow.connect("mult_x.result", "add_x.a")
    workflow.connect("c5.value", "add_x.b")

    # Path 2 connections
    workflow.connect("y.value", "add_y.a")
    workflow.connect("c3.value", "add_y.b")
    workflow.connect("add_y.result", "mult_y.a")
    workflow.connect("c4.value", "mult_y.b")

    result = await workflow.run(inputs={"x": 7, "y": 2})

    # Path 1: 7*2 = 14, 14+5 = 19
    assert result["mult_x"]["result"] == 14
    assert result["add_x"]["result"] == 19

    # Path 2: 2+3 = 5, 5*4 = 20
    assert result["add_y"]["result"] == 5
    assert result["mult_y"]["result"] == 20


@pytest.mark.asyncio
async def test_deep_chain_with_side_branches():
    """Test a deep linear chain with side branches at multiple levels."""
    workflow = Workflow("Deep Chain with Branches")

    # Main chain: A -> B -> C -> D -> E
    # Side branches at B, C, D

    workflow.add_node("a", "input", {"name": "start"})
    workflow.add_node("b", "add", {})
    workflow.add_node("c", "multiply", {})
    workflow.add_node("d", "add", {})
    workflow.add_node("e", "multiply", {})

    # Side branches
    workflow.add_node("b_side", "multiply", {})
    workflow.add_node("c_side", "add", {})
    workflow.add_node("d_side", "multiply", {})

    # Constants
    workflow.add_node("c1", "input", {"name": "c1", "default": 1})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})

    # Main chain connections
    workflow.connect("a.value", "b.a")
    workflow.connect("c1.value", "b.b")

    workflow.connect("b.result", "c.a")
    workflow.connect("c2.value", "c.b")

    workflow.connect("c.result", "d.a")
    workflow.connect("c3.value", "d.b")

    workflow.connect("d.result", "e.a")
    workflow.connect("c2.value", "e.b")

    # Side branch connections
    workflow.connect("b.result", "b_side.a")
    workflow.connect("c2.value", "b_side.b")

    workflow.connect("c.result", "c_side.a")
    workflow.connect("c1.value", "c_side.b")

    workflow.connect("d.result", "d_side.a")
    workflow.connect("c3.value", "d_side.b")

    result = await workflow.run(inputs={"start": 10})

    # Verify main chain
    assert result["b"]["result"] == 11  # 10 + 1
    assert result["c"]["result"] == 22  # 11 * 2
    assert result["d"]["result"] == 25  # 22 + 3
    assert result["e"]["result"] == 50  # 25 * 2

    # Verify side branches
    assert result["b_side"]["result"] == 22  # 11 * 2
    assert result["c_side"]["result"] == 23  # 22 + 1
    assert result["d_side"]["result"] == 75  # 25 * 3
