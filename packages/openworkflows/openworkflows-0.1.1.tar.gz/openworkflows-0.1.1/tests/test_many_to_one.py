"""Tests for many-to-one routing (fan-in patterns and multiple input sources)."""

import pytest
from openworkflows import Workflow


@pytest.mark.asyncio
async def test_simple_fan_in():
    """Test multiple nodes feeding into one node."""
    workflow = Workflow("Simple Fan In")

    # Three separate inputs converge into one sum node
    workflow.add_node("input1", "input", {"name": "a"})
    workflow.add_node("input2", "input", {"name": "b"})
    workflow.add_node("input3", "input", {"name": "c"})
    workflow.add_node("sum", "merge_sum", {})

    workflow.connect("input1.value", "sum.input1")
    workflow.connect("input2.value", "sum.input2")
    workflow.connect("input3.value", "sum.input3")

    result = await workflow.run(inputs={"a": 10, "b": 20, "c": 30})

    assert result["sum"]["result"] == 60


@pytest.mark.asyncio
async def test_multiple_paths_converging():
    """Test multiple computation paths converging to one node."""
    workflow = Workflow("Converging Paths")

    # Start with one input, split into different paths, converge
    workflow.add_node("start", "input", {"name": "x"})

    # Path 1: x * 2
    workflow.add_node("path1", "multiply", {})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.connect("start.value", "path1.a")
    workflow.connect("c2.value", "path1.b")

    # Path 2: x + 10
    workflow.add_node("path2", "add", {})
    workflow.add_node("c10", "input", {"name": "c10", "default": 10})
    workflow.connect("start.value", "path2.a")
    workflow.connect("c10.value", "path2.b")

    # Path 3: x * 3
    workflow.add_node("path3", "multiply", {})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.connect("start.value", "path3.a")
    workflow.connect("c3.value", "path3.b")

    # Converge: multiply all three results
    workflow.add_node("converge_mult1", "multiply", {})
    workflow.add_node("converge_mult2", "multiply", {})

    workflow.connect("path1.result", "converge_mult1.a")
    workflow.connect("path2.result", "converge_mult1.b")
    workflow.connect("converge_mult1.result", "converge_mult2.a")
    workflow.connect("path3.result", "converge_mult2.b")

    result = await workflow.run(inputs={"x": 5})

    # Path results
    assert result["path1"]["result"] == 10  # 5 * 2
    assert result["path2"]["result"] == 15  # 5 + 10
    assert result["path3"]["result"] == 15  # 5 * 3

    # Convergence: 10 * 15 * 15 = 2250
    assert result["converge_mult1"]["result"] == 150  # 10 * 15
    assert result["converge_mult2"]["result"] == 2250  # 150 * 15


@pytest.mark.asyncio
async def test_multiple_sources_to_single_handle():
    """Test that a node can receive input from first available source (first edge wins)."""
    workflow = Workflow("Multiple Sources Priority")

    # Create two sources, both connect to same target
    # The execution order should determine which one "wins"
    workflow.add_node("source1", "input", {"name": "s1"})
    workflow.add_node("source2", "input", {"name": "s2"})
    workflow.add_node("target", "passthrough", {})

    # Both connect to the same handle - first one in execution order should be used
    workflow.connect("source1.value", "target.input")
    workflow.connect("source2.value", "target.input")

    result = await workflow.run(inputs={"s1": "first", "s2": "second"})

    # The workflow should use the first edge (source1)
    # Note: This tests current behavior - we only take first edge in _resolve_input
    assert result["target"]["output"] == "first"


@pytest.mark.asyncio
async def test_multi_stage_aggregation():
    """Test multiple stages of aggregation (tree-like fan-in)."""
    workflow = Workflow("Multi-Stage Aggregation")

    # Create 4 leaf nodes
    workflow.add_node("leaf1", "input", {"name": "v1"})
    workflow.add_node("leaf2", "input", {"name": "v2"})
    workflow.add_node("leaf3", "input", {"name": "v3"})
    workflow.add_node("leaf4", "input", {"name": "v4"})

    # Stage 1: Pair-wise aggregation
    workflow.add_node("stage1_a", "add", {})
    workflow.add_node("stage1_b", "add", {})

    workflow.connect("leaf1.value", "stage1_a.a")
    workflow.connect("leaf2.value", "stage1_a.b")
    workflow.connect("leaf3.value", "stage1_b.a")
    workflow.connect("leaf4.value", "stage1_b.b")

    # Stage 2: Final aggregation
    workflow.add_node("stage2", "add", {})
    workflow.connect("stage1_a.result", "stage2.a")
    workflow.connect("stage1_b.result", "stage2.b")

    result = await workflow.run(inputs={"v1": 1, "v2": 2, "v3": 3, "v4": 4})

    # Stage 1
    assert result["stage1_a"]["result"] == 3  # 1 + 2
    assert result["stage1_b"]["result"] == 7  # 3 + 4

    # Stage 2
    assert result["stage2"]["result"] == 10  # 3 + 7


@pytest.mark.asyncio
async def test_multiple_inputs_to_different_handles():
    """Test multiple sources connecting to different handles of same node."""
    workflow = Workflow("Multiple Inputs Different Handles")

    # Three different computations feed different handles of final node
    workflow.add_node("base", "input", {"name": "x"})

    workflow.add_node("comp1", "multiply", {})
    workflow.add_node("comp2", "add", {})
    workflow.add_node("comp3", "multiply", {})

    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.add_node("c5", "input", {"name": "c5", "default": 5})

    workflow.connect("base.value", "comp1.a")
    workflow.connect("c2.value", "comp1.b")

    workflow.connect("base.value", "comp2.a")
    workflow.connect("c5.value", "comp2.b")

    workflow.connect("base.value", "comp3.a")
    workflow.connect("c3.value", "comp3.b")

    # All feed into merge_sum via different handles
    workflow.add_node("merger", "merge_sum", {})
    workflow.connect("comp1.result", "merger.input1")
    workflow.connect("comp2.result", "merger.input2")
    workflow.connect("comp3.result", "merger.input3")

    result = await workflow.run(inputs={"x": 10})

    assert result["comp1"]["result"] == 20  # 10 * 2
    assert result["comp2"]["result"] == 15  # 10 + 5
    assert result["comp3"]["result"] == 30  # 10 * 3
    assert result["merger"]["result"] == 65  # 20 + 15 + 30


@pytest.mark.asyncio
async def test_asymmetric_fan_in():
    """Test asymmetric fan-in where different branches have different depths."""
    workflow = Workflow("Asymmetric Fan In")

    workflow.add_node("input", "input", {"name": "x"})

    # Short path: just multiply by 2
    workflow.add_node("short", "multiply", {})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.connect("input.value", "short.a")
    workflow.connect("c2.value", "short.b")

    # Medium path: multiply by 2, then add 5
    workflow.add_node("med1", "multiply", {})
    workflow.add_node("med2", "add", {})
    workflow.add_node("c5", "input", {"name": "c5", "default": 5})
    workflow.connect("input.value", "med1.a")
    workflow.connect("c2.value", "med1.b")
    workflow.connect("med1.result", "med2.a")
    workflow.connect("c5.value", "med2.b")

    # Long path: multiply by 2, add 5, multiply by 3
    workflow.add_node("long1", "multiply", {})
    workflow.add_node("long2", "add", {})
    workflow.add_node("long3", "multiply", {})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.connect("input.value", "long1.a")
    workflow.connect("c2.value", "long1.b")
    workflow.connect("long1.result", "long2.a")
    workflow.connect("c5.value", "long2.b")
    workflow.connect("long2.result", "long3.a")
    workflow.connect("c3.value", "long3.b")

    # All converge
    workflow.add_node("final", "merge_sum", {})
    workflow.connect("short.result", "final.input1")
    workflow.connect("med2.result", "final.input2")
    workflow.connect("long3.result", "final.input3")

    result = await workflow.run(inputs={"x": 4})

    # Short: 4 * 2 = 8
    assert result["short"]["result"] == 8

    # Medium: (4 * 2) + 5 = 13
    assert result["med2"]["result"] == 13

    # Long: ((4 * 2) + 5) * 3 = 39
    assert result["long3"]["result"] == 39

    # Final: 8 + 13 + 39 = 60
    assert result["final"]["result"] == 60


@pytest.mark.asyncio
async def test_circular_convergence_pattern():
    """Test nodes that form a convergence ring pattern."""
    workflow = Workflow("Circular Convergence")

    # Input splits to A and B
    # A and B each process
    # Both feed into C
    # C result is used by both D and E
    # D and E results converge to F

    workflow.add_node("input", "input", {"name": "x"})

    # Split level
    workflow.add_node("a", "add", {})
    workflow.add_node("b", "multiply", {})

    workflow.add_node("c1", "input", {"name": "c1", "default": 1})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})

    workflow.connect("input.value", "a.a")
    workflow.connect("c1.value", "a.b")
    workflow.connect("input.value", "b.a")
    workflow.connect("c2.value", "b.b")

    # First convergence
    workflow.add_node("c", "add", {})
    workflow.connect("a.result", "c.a")
    workflow.connect("b.result", "c.b")

    # Second split
    workflow.add_node("d", "multiply", {})
    workflow.add_node("e", "add", {})

    workflow.connect("c.result", "d.a")
    workflow.connect("c2.value", "d.b")
    workflow.connect("c.result", "e.a")
    workflow.connect("c1.value", "e.b")

    # Final convergence
    workflow.add_node("f", "add", {})
    workflow.connect("d.result", "f.a")
    workflow.connect("e.result", "f.b")

    result = await workflow.run(inputs={"x": 10})

    # First level
    assert result["a"]["result"] == 11  # 10 + 1
    assert result["b"]["result"] == 20  # 10 * 2

    # First convergence
    assert result["c"]["result"] == 31  # 11 + 20

    # Second level
    assert result["d"]["result"] == 62  # 31 * 2
    assert result["e"]["result"] == 32  # 31 + 1

    # Final convergence
    assert result["f"]["result"] == 94  # 62 + 32
