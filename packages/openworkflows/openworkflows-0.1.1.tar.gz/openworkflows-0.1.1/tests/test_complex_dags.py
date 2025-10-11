"""Tests for complex DAG workflows combining multiple patterns."""

import pytest
from openworkflows import Workflow


@pytest.mark.asyncio
async def test_full_pipeline_etl_pattern():
    """Test a complete ETL-like pipeline with extract, transform, load stages."""
    workflow = Workflow("ETL Pipeline")

    # Extract stage - multiple sources
    workflow.add_node("source1", "input", {"name": "data1"})
    workflow.add_node("source2", "input", {"name": "data2"})
    workflow.add_node("source3", "input", {"name": "data3"})

    # Transform stage - parallel transformations
    workflow.add_node("transform1", "multiply", {})
    workflow.add_node("transform2", "add", {})
    workflow.add_node("transform3", "multiply", {})

    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c10", "input", {"name": "c10", "default": 10})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})

    workflow.connect("source1.value", "transform1.a")
    workflow.connect("c2.value", "transform1.b")

    workflow.connect("source2.value", "transform2.a")
    workflow.connect("c10.value", "transform2.b")

    workflow.connect("source3.value", "transform3.a")
    workflow.connect("c3.value", "transform3.b")

    # Load stage - aggregate results
    workflow.add_node("aggregate", "merge_sum", {})
    workflow.connect("transform1.result", "aggregate.input1")
    workflow.connect("transform2.result", "aggregate.input2")
    workflow.connect("transform3.result", "aggregate.input3")

    # Final validation
    workflow.add_node("validate", "conditional", {"threshold": 100})
    workflow.connect("aggregate.result", "validate.value")

    workflow.add_node("success", "passthrough", {})
    workflow.add_node("failure", "passthrough", {})
    workflow.connect("validate.high", "success.input")
    workflow.connect("validate.low", "failure.input")

    # Test successful case
    result = await workflow.run(inputs={"data1": 10, "data2": 20, "data3": 30})

    assert result["transform1"]["result"] == 20  # 10 * 2
    assert result["transform2"]["result"] == 30  # 20 + 10
    assert result["transform3"]["result"] == 90  # 30 * 3
    assert result["aggregate"]["result"] == 140  # 20 + 30 + 90
    assert result["success"]["output"] == 140

    # Test failure case
    result = await workflow.run(inputs={"data1": 5, "data2": 10, "data3": 5})
    assert result["aggregate"]["result"] == 45  # 10 + 20 + 15
    assert result["failure"]["output"] == 45


@pytest.mark.asyncio
async def test_recursive_aggregation_tree():
    """Test a binary tree aggregation pattern."""
    workflow = Workflow("Binary Tree Aggregation")

    # 8 leaf nodes
    leaves = []
    for i in range(8):
        node_id = f"leaf{i}"
        workflow.add_node(node_id, "input", {"name": f"v{i}"})
        leaves.append(node_id)

    # Level 1: 8 -> 4
    level1 = []
    for i in range(4):
        node_id = f"l1_{i}"
        workflow.add_node(node_id, "add", {})
        workflow.connect(f"{leaves[i * 2]}.value", f"{node_id}.a")
        workflow.connect(f"{leaves[i * 2 + 1]}.value", f"{node_id}.b")
        level1.append(node_id)

    # Level 2: 4 -> 2
    level2 = []
    for i in range(2):
        node_id = f"l2_{i}"
        workflow.add_node(node_id, "add", {})
        workflow.connect(f"{level1[i * 2]}.result", f"{node_id}.a")
        workflow.connect(f"{level1[i * 2 + 1]}.result", f"{node_id}.b")
        level2.append(node_id)

    # Level 3: 2 -> 1
    workflow.add_node("root", "add", {})
    workflow.connect(f"{level2[0]}.result", "root.a")
    workflow.connect(f"{level2[1]}.result", "root.b")

    # Input values 1-8
    inputs = {f"v{i}": i + 1 for i in range(8)}
    result = await workflow.run(inputs=inputs)

    # Sum should be 1+2+3+4+5+6+7+8 = 36
    assert result["root"]["result"] == 36


@pytest.mark.asyncio
async def test_complex_multi_path_with_crossover():
    """Test complex workflow with paths that cross and merge multiple times."""
    workflow = Workflow("Complex Crossover")

    # Start with two inputs
    workflow.add_node("x", "input", {"name": "x"})
    workflow.add_node("y", "input", {"name": "y"})

    # First operations
    workflow.add_node("x_mult", "multiply", {})
    workflow.add_node("y_add", "add", {})

    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c5", "input", {"name": "c5", "default": 5})

    workflow.connect("x.value", "x_mult.a")
    workflow.connect("c2.value", "x_mult.b")
    workflow.connect("y.value", "y_add.a")
    workflow.connect("c5.value", "y_add.b")

    # Cross operations - x result goes to y path and vice versa
    workflow.add_node("cross1", "add", {})  # x_mult + y_add
    workflow.add_node("cross2", "multiply", {})  # x_mult * y_add

    workflow.connect("x_mult.result", "cross1.a")
    workflow.connect("y_add.result", "cross1.b")
    workflow.connect("x_mult.result", "cross2.a")
    workflow.connect("y_add.result", "cross2.b")

    # Parallel operations on crossed results
    workflow.add_node("p1", "multiply", {})
    workflow.add_node("p2", "add", {})

    workflow.add_node("c3", "input", {"name": "c3", "default": 3})

    workflow.connect("cross1.result", "p1.a")
    workflow.connect("c2.value", "p1.b")
    workflow.connect("cross2.result", "p2.a")
    workflow.connect("c3.value", "p2.b")

    # Final merge
    workflow.add_node("final", "add", {})
    workflow.connect("p1.result", "final.a")
    workflow.connect("p2.result", "final.b")

    result = await workflow.run(inputs={"x": 10, "y": 3})

    # x_mult = 10 * 2 = 20
    # y_add = 3 + 5 = 8
    assert result["x_mult"]["result"] == 20
    assert result["y_add"]["result"] == 8

    # cross1 = 20 + 8 = 28
    # cross2 = 20 * 8 = 160
    assert result["cross1"]["result"] == 28
    assert result["cross2"]["result"] == 160

    # p1 = 28 * 2 = 56
    # p2 = 160 + 3 = 163
    assert result["p1"]["result"] == 56
    assert result["p2"]["result"] == 163

    # final = 56 + 163 = 219
    assert result["final"]["result"] == 219


@pytest.mark.asyncio
async def test_multi_stage_filtering_pipeline():
    """Test a multi-stage filtering pipeline with conditional routing at each stage."""
    workflow = Workflow("Multi-Stage Filter")

    # Input
    workflow.add_node("input", "input", {"name": "score"})

    # Stage 1: Filter out very low scores (< 30)
    workflow.add_node("filter1", "conditional", {"threshold": 30})
    workflow.connect("input.value", "filter1.value")

    workflow.add_node("rejected_low", "passthrough", {})
    workflow.connect("filter1.low", "rejected_low.input")

    # Stage 2: Filter out medium scores (< 60)
    workflow.add_node("filter2", "conditional", {"threshold": 60})
    workflow.connect("filter1.high", "filter2.value")

    workflow.add_node("rejected_medium", "passthrough", {})
    workflow.connect("filter2.low", "rejected_medium.input")

    # Stage 3: Filter out high scores (< 90)
    workflow.add_node("filter3", "conditional", {"threshold": 90})
    workflow.connect("filter2.high", "filter3.value")

    workflow.add_node("accepted_high", "passthrough", {})
    workflow.add_node("accepted_very_high", "passthrough", {})
    workflow.connect("filter3.low", "accepted_high.input")
    workflow.connect("filter3.high", "accepted_very_high.input")

    # Test very low
    result = await workflow.run(inputs={"score": 20})
    assert result["rejected_low"]["output"] == 20

    # Test medium
    result = await workflow.run(inputs={"score": 45})
    assert result["rejected_medium"]["output"] == 45

    # Test high
    result = await workflow.run(inputs={"score": 75})
    assert result["accepted_high"]["output"] == 75

    # Test very high
    result = await workflow.run(inputs={"score": 95})
    assert result["accepted_very_high"]["output"] == 95


@pytest.mark.asyncio
async def test_scatter_gather_pattern():
    """Test scatter-gather pattern: distribute work, process in parallel, gather results."""
    workflow = Workflow("Scatter-Gather")

    # Scatter: One input distributed to multiple workers
    workflow.add_node("work_item", "input", {"name": "task"})
    workflow.add_node("scatter", "split", {})
    workflow.connect("work_item.value", "scatter.value")

    # Process in parallel with different operations
    workflow.add_node("worker1", "multiply", {})
    workflow.add_node("worker2", "multiply", {})
    workflow.add_node("worker3", "multiply", {})

    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})
    workflow.add_node("c4", "input", {"name": "c4", "default": 4})

    workflow.connect("scatter.out1", "worker1.a")
    workflow.connect("c2.value", "worker1.b")

    workflow.connect("scatter.out2", "worker2.a")
    workflow.connect("c3.value", "worker2.b")

    workflow.connect("scatter.out3", "worker3.a")
    workflow.connect("c4.value", "worker3.b")

    # Gather: Aggregate all worker results
    workflow.add_node("gather", "merge_sum", {})
    workflow.connect("worker1.result", "gather.input1")
    workflow.connect("worker2.result", "gather.input2")
    workflow.connect("worker3.result", "gather.input3")

    result = await workflow.run(inputs={"task": 10})

    assert result["worker1"]["result"] == 20  # 10 * 2
    assert result["worker2"]["result"] == 30  # 10 * 3
    assert result["worker3"]["result"] == 40  # 10 * 4
    assert result["gather"]["result"] == 90  # 20 + 30 + 40


@pytest.mark.asyncio
async def test_layered_processing_pipeline():
    """Test a layered neural-network-like processing pattern."""
    workflow = Workflow("Layered Pipeline")

    # Input layer
    workflow.add_node("input", "input", {"name": "x"})

    # Hidden layer 1: 3 nodes
    workflow.add_node("h1_1", "multiply", {})
    workflow.add_node("h1_2", "add", {})
    workflow.add_node("h1_3", "multiply", {})

    workflow.add_node("c1", "input", {"name": "c1", "default": 1})
    workflow.add_node("c2", "input", {"name": "c2", "default": 2})
    workflow.add_node("c3", "input", {"name": "c3", "default": 3})

    workflow.connect("input.value", "h1_1.a")
    workflow.connect("c2.value", "h1_1.b")

    workflow.connect("input.value", "h1_2.a")
    workflow.connect("c1.value", "h1_2.b")

    workflow.connect("input.value", "h1_3.a")
    workflow.connect("c3.value", "h1_3.b")

    # Hidden layer 2: 2 nodes (each receives from multiple layer 1 nodes)
    workflow.add_node("h2_1", "add", {})
    workflow.add_node("h2_2", "add", {})

    workflow.connect("h1_1.result", "h2_1.a")
    workflow.connect("h1_2.result", "h2_1.b")

    workflow.connect("h1_2.result", "h2_2.a")
    workflow.connect("h1_3.result", "h2_2.b")

    # Output layer: combine both hidden layer 2 outputs
    workflow.add_node("output", "multiply", {})
    workflow.connect("h2_1.result", "output.a")
    workflow.connect("h2_2.result", "output.b")

    result = await workflow.run(inputs={"x": 5})

    # Layer 1
    assert result["h1_1"]["result"] == 10  # 5 * 2
    assert result["h1_2"]["result"] == 6  # 5 + 1
    assert result["h1_3"]["result"] == 15  # 5 * 3

    # Layer 2
    assert result["h2_1"]["result"] == 16  # 10 + 6
    assert result["h2_2"]["result"] == 21  # 6 + 15

    # Output
    assert result["output"]["result"] == 336  # 16 * 21
