# TDD Workflow Templates - Usage Guide

Two composable workflow templates have been created for Python testing and quality checking, designed specifically for TDD workflows.

## Workflows Created

### 1. python-run-tests
**Location**: `src/workflows_mcp/templates/python/python-run-tests.yaml`

**Purpose**: Execute pytest with coverage measurement and return structured results for TDD workflow logic.

**Features**:
- Runs pytest with coverage reporting
- Parses test results (passed, failed, skipped counts)
- Extracts coverage percentage from coverage.json
- Compares coverage against threshold
- Returns structured outputs for conditional workflow logic

**Inputs**:
```yaml
test_path: "tests/"                    # Path to test directory or file
source_path: "src/"                     # Path to source code for coverage
coverage_threshold: 80                  # Minimum coverage percentage (0-100)
pytest_args: "-v"                       # Additional pytest arguments
working_dir: "."                        # Working directory for execution
venv_path: ""                           # Optional virtual environment path
```

**Example Usage**:
```yaml
- id: run_tests
  type: ExecuteWorkflow
  inputs:
    workflow: python-run-tests
    inputs:
      test_path: "tests/test_module.py"
      source_path: "src/my_module"
      coverage_threshold: 85
      pytest_args: "-v --tb=short"
```

**Accessing Outputs** (via blocks namespace):
```python
result = await executor.execute_workflow("python-run-tests", {...})
blocks = result.value.get("blocks", {})

# Extract test results
exit_code = blocks.get("run_pytest", {}).get("exit_code")
tests_passed = blocks.get("extract_passed_count", {}).get("stdout", "").strip()
tests_failed = blocks.get("extract_failed_count", {}).get("stdout", "").strip()
tests_skipped = blocks.get("extract_skipped_count", {}).get("stdout", "").strip()

# Extract coverage information
coverage_percent = blocks.get("extract_coverage", {}).get("stdout", "").strip()
coverage_threshold_met = blocks.get("check_coverage_threshold", {}).get("stdout", "").strip()

# Get formatted summary
summary = blocks.get("generate_summary", {}).get("echoed", "")
```

**Key Outputs**:
- `run_pytest.exit_code`: pytest exit code (0 = success)
- `extract_passed_count.stdout`: Number of tests passed
- `extract_failed_count.stdout`: Number of tests failed
- `extract_skipped_count.stdout`: Number of tests skipped
- `extract_coverage.stdout`: Coverage percentage (e.g., "87.50")
- `check_coverage_threshold.stdout`: "true" if threshold met, "false" or "" otherwise
- `generate_summary.echoed`: Formatted test execution summary

---

### 2. python-quality-check
**Location**: `src/workflows_mcp/templates/python/python-quality-check.yaml`

**Purpose**: Run comprehensive Python quality checks (ruff, mypy, format validation) with aggregated results.

**Features**:
- Runs ruff linting (configurable)
- Runs mypy type checking (configurable)
- Runs ruff format validation (configurable)
- Continues on error (doesn't stop at first failure)
- Returns structured pass/fail status for each check

**Inputs**:
```yaml
source_path: "src/"                     # Path to source code to check
strict: false                            # Enable strict mode (fail on warnings)
check_linting: true                      # Enable ruff linting
check_types: true                        # Enable mypy type checking
check_formatting: true                   # Enable format validation
working_dir: "."                         # Working directory
venv_path: ""                            # Optional virtual environment path
```

**Example Usage**:
```yaml
- id: quality_check
  type: ExecuteWorkflow
  inputs:
    workflow: python-quality-check
    inputs:
      source_path: "src/workflows_mcp"
      strict: true
      check_linting: true
      check_types: true
      check_formatting: true
```

**Accessing Outputs** (via blocks namespace):
```python
result = await executor.execute_workflow("python-quality-check", {...})
blocks = result.value.get("blocks", {})

# Extract quality check results
linting_status = blocks.get("get_linting_status", {}).get("stdout", "").strip()
typing_status = blocks.get("get_typing_status", {}).get("stdout", "").strip()
formatting_status = blocks.get("get_formatting_status", {}).get("stdout", "").strip()
overall_status = blocks.get("calculate_overall_status", {}).get("stdout", "").strip()

# Status values: "passed", "failed", or "skipped"
linting_passed = linting_status == "passed"
typing_passed = typing_status == "passed"
formatting_passed = formatting_status == "passed"
all_checks_passed = overall_status == "passed"

# Get detailed outputs
linting_output = blocks.get("run_ruff_linting", {}).get("stdout", "")
typing_output = blocks.get("run_mypy_checking", {}).get("stdout", "")
formatting_output = blocks.get("run_format_check", {}).get("stdout", "")

# Get formatted summary
summary = blocks.get("generate_summary", {}).get("echoed", "")
```

**Key Outputs**:
- `get_linting_status.stdout`: "passed", "failed", or "skipped"
- `get_typing_status.stdout`: "passed", "failed", or "skipped"
- `get_formatting_status.stdout`: "passed", "failed", or "skipped"
- `calculate_overall_status.stdout`: "passed" or "failed"
- `run_ruff_linting.exit_code`: ruff linting exit code
- `run_mypy_checking.exit_code`: mypy exit code
- `run_format_check.exit_code`: ruff format exit code
- `generate_summary.echoed`: Formatted quality check summary

---

## Integration with TDD Workflows

### Conditional Execution Based on Test Results

```yaml
# Run tests first
- id: run_tests
  type: ExecuteWorkflow
  inputs:
    workflow: python-run-tests
    inputs:
      test_path: "tests/"
      source_path: "src/"
      coverage_threshold: 80

# Only proceed to quality checks if tests pass
- id: quality_check
  type: ExecuteWorkflow
  inputs:
    workflow: python-quality-check
    inputs:
      source_path: "src/"
  condition: "${run_tests.blocks.run_pytest.exit_code} == 0"
  depends_on:
    - run_tests

# Deploy only if all checks pass
- id: deploy
  type: Shell
  inputs:
    command: "echo 'Deploying...'"
  condition: |
    ${run_tests.blocks.run_pytest.exit_code} == 0 and
    ${quality_check.blocks.calculate_overall_status.stdout} == "passed"
  depends_on:
    - quality_check
```

### TDD Red-Green-Refactor Cycle

```yaml
# RED: Write failing test and verify it fails
- id: verify_red_phase
  type: ExecuteWorkflow
  inputs:
    workflow: python-run-tests
    inputs:
      test_path: "tests/test_new_feature.py"

# GREEN: Implement feature (external step)
# User implements minimal code to pass test

# Run tests again to verify green
- id: verify_green_phase
  type: ExecuteWorkflow
  inputs:
    workflow: python-run-tests
    inputs:
      test_path: "tests/test_new_feature.py"

# REFACTOR: Run quality checks before refactoring
- id: quality_before_refactor
  type: ExecuteWorkflow
  inputs:
    workflow: python-quality-check
    inputs:
      source_path: "src/new_feature.py"

# After refactoring, verify tests still pass
- id: verify_refactor
  type: ExecuteWorkflow
  inputs:
    workflow: python-run-tests
    inputs:
      test_path: "tests/test_new_feature.py"
```

---

## Notes on Output Resolution

**Current Implementation**: The workflow executor returns block outputs under the `blocks` namespace. While the workflows define top-level `outputs` sections for convenience, these are not currently resolved by the executor.

**Accessing Results**: Use the blocks namespace as shown in the examples above:
```python
blocks = result.value.get("blocks", {})
value = blocks.get("block_id", {}).get("field_name")
```

**Future Enhancement**: Workflow-level output resolution could be added to the executor to simplify access patterns.

---

## Testing the Workflows

### Via Python
```python
import asyncio
from workflows_mcp.engine.registry import WorkflowRegistry
from workflows_mcp.engine.executor import WorkflowExecutor

async def test():
    registry = WorkflowRegistry()
    registry.load_from_directory('src/workflows_mcp/templates')

    executor = WorkflowExecutor()
    for workflow in registry.list_all():
        executor.load_workflow(workflow)

    result = await executor.execute_workflow(
        'python-run-tests',
        runtime_inputs={
            'test_path': 'tests/',
            'source_path': 'src/',
            'coverage_threshold': 80
        }
    )

    if result.is_success:
        blocks = result.value.get('blocks', {})
        print(f"Exit code: {blocks.get('run_pytest', {}).get('exit_code')}")

asyncio.run(test())
```

### Via MCP Tools
```javascript
// Via Claude Code or MCP client
execute_workflow({
  workflow: "python-run-tests",
  inputs: {
    test_path: "tests/",
    source_path: "src/",
    coverage_threshold: 80
  }
})
```

---

## Workflow Composition Examples

### Combined Test + Quality Pipeline
```yaml
name: test-and-quality-pipeline
description: Run tests followed by quality checks
blocks:
  - id: run_tests
    type: ExecuteWorkflow
    inputs:
      workflow: python-run-tests
      inputs:
        test_path: "${test_path}"
        source_path: "${source_path}"
        coverage_threshold: "${coverage_threshold}"

  - id: run_quality
    type: ExecuteWorkflow
    inputs:
      workflow: python-quality-check
      inputs:
        source_path: "${source_path}"
    depends_on:
      - run_tests
    condition: "${run_tests.blocks.run_pytest.exit_code} == 0"

  - id: final_status
    type: EchoBlock
    inputs:
      message: |
        Pipeline Complete:
        Tests: ${run_tests.blocks.run_pytest.exit_code} == 0
        Quality: ${run_quality.blocks.calculate_overall_status.stdout} == "passed"
    depends_on:
      - run_quality
```

---

## Design Principles

1. **Composability**: Use Shell blocks (not custom Python blocks) for maximum reusability
2. **Structured Outputs**: Parse results into discrete fields for workflow logic
3. **Continue on Error**: Don't fail entire workflow on test/lint failures - collect all results
4. **Clear Summaries**: Provide formatted summaries via EchoBlock for human readability
5. **Conditional Logic**: Support workflow branching based on test/quality results
6. **Tool Integration**: Works seamlessly with existing tools (pytest, ruff, mypy, coverage)
