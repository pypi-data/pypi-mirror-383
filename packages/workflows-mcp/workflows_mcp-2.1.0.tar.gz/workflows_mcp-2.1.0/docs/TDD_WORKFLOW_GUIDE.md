# TDD Workflow System - Complete User Guide

**Version:** 1.0
**Last Updated:** 2025-10-10

Complete guide to using the MCP Workflows TDD (Test-Driven Development) system for building production-ready applications from PRD to deployment.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Workflow Components](#workflow-components)
- [Phase Guides](#phase-guides)
  - [Phase 1: Analysis & Specification](#phase-1-analysis--specification)
  - [Phase 2: Architecture & Design](#phase-2-architecture--design)
  - [Phase 3: Scaffolding](#phase-3-scaffolding)
  - [Phase 4: TDD Module Implementation](#phase-4-tdd-module-implementation)
  - [Phase 5: Integration Testing](#phase-5-integration-testing)
  - [Phase 6: Validation & Quality Gates](#phase-6-validation--quality-gates)
  - [Phase 7: Finalization & Documentation](#phase-7-finalization--documentation)
- [Helper Workflows](#helper-workflows)
- [State Management](#state-management)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Reference](#reference)

---

## Overview

### What is the TDD Workflow System?

The TDD Workflow System is a comprehensive, multi-phase development pipeline that guides you from a Product Requirements Document (PRD) to a production-ready application using Test-Driven Development principles.

**Key Principles:**
- **Test-First Development**: Write tests before implementation (RED-GREEN-REFACTOR)
- **Quality Gates**: Automated validation at each phase
- **State Management**: Resume workflows from checkpoints
- **Interactive Guidance**: LLM-driven analysis and implementation
- **Production Ready**: Complete documentation and deployment preparation

### Why Use Workflow-Based TDD?

**Traditional Development Challenges:**
- Requirements drift and missed specifications
- Incomplete test coverage
- Undocumented architecture decisions
- Missing deployment procedures
- Inconsistent quality standards

**Workflow-Based TDD Benefits:**
- **Systematic Progress**: 7 structured phases with clear deliverables
- **Enforced Quality**: Built-in quality gates prevent shortcuts
- **State Persistence**: Resume from any checkpoint
- **Complete Documentation**: Generated alongside code
- **Production Readiness**: Validated deployment procedures

### Key Features

- **7-Phase Pipeline**: Structured progression from PRD to deployment
- **Interactive Checkpoints**: Human approval at critical decision points
- **State Management**: `.tdd-state.json` tracks progress
- **Test-First Discipline**: Enforced RED-GREEN-REFACTOR cycles
- **Quality Validation**: Automated linting, type checking, security scanning
- **Complete Documentation**: Deployment guides, user docs, API specs, runbooks
- **Deployment Ready**: Checklists and procedures for production

---

## Architecture

### Multi-Workflow Orchestration

The TDD system uses **workflow composition** - multiple specialized workflows coordinated by a master orchestrator.

```text
tdd-orchestrator (Orchestrator)
├── Phase 1: tdd-phase1-analysis
├── Phase 2: tdd-phase2-architecture
├── Phase 3: tdd-phase3-scaffolding
├── Phase 4: tdd-phase4-module-tdd (iterative, per module)
├── Phase 5: tdd-phase5-integration
├── Phase 6: tdd-phase6-validation
└── Phase 7: tdd-phase7-finalization

Helper Workflows:
├── python-run-tests (test execution + coverage)
└── python-quality-check (linting + types + formatting)
```

### State Management with `.tdd-state.json`

The system maintains a **persistent state file** that tracks:
- Current phase and completion status
- Module lists and implementation progress
- Test metrics and coverage data
- Quality gate results
- Checkpoint approvals

**State File Location**: `<project_root>/.tdd-state.json`

**Benefits:**
- Resume from any checkpoint
- Track progress across sessions
- Validate phase prerequisites
- Coordinate multi-module implementation

### Interactive Pause/Resume Pattern

Workflows **pause for LLM interaction** at critical points:

1. **Pause**: Workflow saves checkpoint with `ConfirmOperation` or `GetInput`
2. **LLM Response**: Human or LLM provides input
3. **Resume**: Workflow continues with response incorporated

**Example Flow:**
```python
# Workflow pauses at test implementation
result = execute_workflow("tdd-phase4-module-tdd", {...})
# result["status"] == "paused"
# result["checkpoint_id"] == "pause_abc123"

# Resume with LLM-provided test code
resume_result = resume_workflow(
    checkpoint_id="pause_abc123",
    llm_response="<complete test code>"
)
```

### Phase-Based Progression

Each phase builds on previous phases:

```text
Phase 1 → Phase 2 → Phase 3 → Phase 4* → Phase 5 → Phase 6 → Phase 7
   ↓         ↓         ↓         ↓          ↓         ↓         ↓
 SPEC      ARCH     SETUP     TDD       INTEGRATE  VALIDATE  FINALIZE

* Phase 4 is iterative: execute once per module
```

**Validation**: Each phase verifies previous phase completion before starting.

---

## Quick Start

### Prerequisites

- **Python 3.12+**
- **MCP Workflows server running**
- **PRD document prepared** (`PRD.md` in project directory)

### Basic Usage: Complete Pipeline

Execute the full TDD pipeline from PRD to deployment:

```python
result = execute_workflow("tdd-orchestrator", {
    "project_name": "user-management-api",
    "project_path": "/path/to/project",
    "prd_path": "PRD.md",
    "version": "1.0.0",
    "author": "Development Team"
})
```

**What Happens:**
1. Workflow initializes state
2. Executes Phase 1 (Analysis) → pauses for approval
3. Executes Phase 2 (Architecture) → pauses for approval
4. Executes Phase 3 (Scaffolding) → pauses for approval
5. **Phase 4 requires manual iteration** (see below)
6. Executes Phase 5 (Integration) → pauses for approval
7. Executes Phase 6 (Validation) → pauses for approval
8. Executes Phase 7 (Finalization) → completion checkpoint

### Phase 4 Special Instructions

**Phase 4 is ITERATIVE** - you must execute it once per module:

```python
# Read modules from state
state = read_json_state(".tdd-state.json")
modules = state["modules"]  # ["user_service", "task_service", "auth_service"]

# Implement each module with TDD
for module in modules:
    if module not in state["completed_modules"]:
        result = execute_workflow("tdd-phase4-module-tdd", {
            "project_path": "/path/to/project",
            "module_name": module
        })
        # Workflow pauses 8 times per module for RED-GREEN-REFACTOR
```

**After all modules complete**, proceed to Phase 5.

---

## Workflow Components

### Workflow Blocks

The TDD workflows use specialized blocks:

#### JSONStateManager Blocks

**Purpose**: Manage `.tdd-state.json` for progress tracking

- **ReadJSONState**: Load current state
  ```yaml
  - id: read_state
    type: ReadJSONState
    inputs:
      path: "${project_path}/.tdd-state.json"
  ```

- **WriteJSONState**: Initialize or overwrite state
  ```yaml
  - id: initialize_state
    type: WriteJSONState
    inputs:
      path: "${project_path}/.tdd-state.json"
      state:
        workflow_version: "1.0"
        current_phase: "phase1_started"
  ```

- **MergeJSONState**: Update specific keys
  ```yaml
  - id: update_state
    type: MergeJSONState
    inputs:
      path: "${project_path}/.tdd-state.json"
      updates:
        current_phase: "phase1_complete"
  ```

#### Interactive Blocks

**Purpose**: Pause workflows for human/LLM input

- **ConfirmOperation**: Yes/No confirmation
  ```yaml
  - id: confirm_phase1
    type: ConfirmOperation
    inputs:
      message: "Approve Phase 1 and proceed to Phase 2?"
      operation: "approve_phase1"
  ```

- **GetInput**: Free-form text response
  ```yaml
  - id: request_tests
    type: GetInput
    inputs:
      prompt: "Write unit tests for ${module_name}..."
  ```

- **AskChoice**: Multiple-choice selection
  ```yaml
  - id: ask_continue
    type: AskChoice
    inputs:
      question: "Continue to next module?"
      choices:
        - "Continue to next module"
        - "Review current module"
        - "Exit TDD workflow"
  ```

#### File Operation Blocks

- **CreateFile**: Write file content
- **ReadFile**: Read file content into context
- **PopulateTemplate**: Render Jinja2 templates

#### Command Execution

- **Shell**: Execute shell commands
  ```yaml
  - id: run_tests
    type: Shell
    inputs:
      command: "pytest tests/ --cov=src/"
      timeout: 300
  ```

#### Workflow Composition

- **ExecuteWorkflow**: Call another workflow
  ```yaml
  - id: run_quality_checks
    type: ExecuteWorkflow
    inputs:
      workflow: python-quality-check
      inputs:
        source_path: "src/"
  ```

---

## Phase Guides

### Phase 1: Analysis & Specification

**Purpose**: Transform PRD into clear, unambiguous technical specification

**Inputs:**
- `project_path` (default: "."): Project root directory
- `prd_path` (default: "PRD.md"): Path to PRD document
- `state_file` (default: ".tdd-state.json"): State file path

**Interactive Pauses (6 total):**
1. **Identify Ambiguities**: LLM analyzes PRD for gaps and unclear requirements
2. **Confirm Clarifications**: Decide if clarifications are needed
3. **Get Clarifications**: Provide answers to ambiguities (if yes above)
4. **Define Success Criteria**: LLM creates measurable success criteria
5. **Identify Constraints**: LLM lists technical constraints
6. **Write Technical Spec**: LLM generates complete specification document
7. **Checkpoint Review**: Approve Phase 1 completion

**Outputs:**
- `TECHNICAL_SPEC.md`: Complete technical specification with:
  - Requirements (unique IDs: REQ-001, REQ-002, ...)
  - Success criteria (measurable and testable)
  - Technical constraints (performance, security, compatibility)
  - Assumptions & dependencies
  - Out of scope items
- `.tdd-state.json`: Initialized with Phase 1 completion

**State Changes:**
```json
{
  "current_phase": "phase1_complete",
  "phases_completed": ["phase1"],
  "phase1": {
    "technical_spec_path": "TECHNICAL_SPEC.md",
    "requirements_count": 15,
    "requirements_list": ["REQ-001", "REQ-002", ...],
    "completed_at": "2025-10-10T12:00:00",
    "ambiguities_resolved": true
  }
}
```

**Common Issues:**
- **PRD not found**: Ensure `PRD.md` exists in `project_path`
- **Ambiguous requirements**: Work through clarification prompts carefully
- **Incomplete spec**: Review success criteria before approving checkpoint

**Example:**
```python
result = execute_workflow("tdd-phase1-analysis", {
    "project_path": "/projects/user-api",
    "prd_path": "PRD.md"
})
# Workflow pauses 6 times for LLM interaction
# Creates TECHNICAL_SPEC.md with 15 requirements
```

---

### Phase 2: Architecture & Design

**Purpose**: Design system architecture, define modules, plan test strategy

**Inputs:**
- `project_path` (default: "."): Project root directory
- `state_file` (default: ".tdd-state.json"): State file path
- `spec_path` (default: "TECHNICAL_SPEC.md"): Technical spec from Phase 1
- `architecture_output_path` (default: "ARCHITECTURE.md"): Output file path

**Interactive Pauses (6 total):**
1. **Design Architecture**: LLM creates high-level system design
2. **Define Data Models**: LLM specifies database schemas and relationships
3. **Identify Modules**: LLM breaks system into modules with single responsibilities
4. **Define Interfaces**: LLM specifies module APIs and contracts
5. **Plan Test Strategy**: LLM creates unit/integration/E2E test plan
6. **Document Architecture**: LLM combines into comprehensive document
7. **Checkpoint Review**: Approve Phase 2 completion

**Outputs:**
- `ARCHITECTURE.md`: Complete architecture document with:
  - System overview and patterns
  - Data models with fields, relationships, constraints
  - Module definitions with responsibilities and dependencies
  - Module interfaces (function signatures, inputs, outputs)
  - Test strategy (unit, integration, E2E coverage)
- `.tdd-state.json`: Updated with modules list

**State Changes:**
```json
{
  "current_phase": "phase2_complete",
  "phases_completed": ["phase1", "phase2"],
  "modules": ["user_service", "task_service", "auth_service"],
  "completed_modules": [],
  "phase2": {
    "architecture_path": "ARCHITECTURE.md",
    "module_count": 3,
    "modules": ["user_service", "task_service", "auth_service"],
    "completed_at": "2025-10-10T13:00:00",
    "test_strategy_defined": true
  }
}
```

**Common Issues:**
- **Circular dependencies**: Ensure modules depend on lower layers only
- **Unclear interfaces**: Define explicit parameter types and return values
- **Missing test strategy**: Ensure unit/integration/E2E tests are all planned

**Example:**
```python
result = execute_workflow("tdd-phase2-architecture", {
    "project_path": "/projects/user-api"
})
# Workflow pauses 6 times for architectural design
# Creates ARCHITECTURE.md with 3 modules identified
```

---

### Phase 3: Scaffolding

**Purpose**: Create project structure, setup dependencies, initialize test framework

**Inputs:**
- `project_path` (default: "."): Project root directory
- `state_file` (default: ".tdd-state.json"): State file path
- `python_version` (default: "3.12"): Python version requirement
- `test_framework` (default: "pytest"): Test framework to use
- `project_name` (default: ""): Project name (auto-detected if empty)

**Interactive Pauses (1 total):**
1. **Checkpoint Review**: Confirm scaffolding complete

**What Phase 3 Creates:**
```text
project-root/
├── src/
│   └── <project_name>/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── conftest.py (pytest fixtures)
├── docs/
├── pyproject.toml (Python project config)
├── .gitignore
├── README.md
└── .tdd-state.json
```

**Dependencies Installed:**
- `pytest>=8.0.0` - Test framework
- `pytest-cov>=4.1.0` - Coverage measurement
- `ruff>=0.1.0` - Linting and formatting
- `mypy>=1.7.0` - Type checking

**Outputs:**
- Complete project structure
- Dependencies installed via `uv sync --dev` (or `pip install -e ".[dev]"`)
- Test framework configured and verified
- `.tdd-state.json`: Updated with Phase 3 completion

**State Changes:**
```json
{
  "current_phase": "phase3_complete",
  "phases_completed": ["phase1", "phase2", "phase3"],
  "setup_ready": true,
  "phase3": {
    "project_name": "user-api",
    "setup_successful": true,
    "dependencies_installed": true,
    "test_framework_ready": true,
    "install_method": "uv",
    "completed_at": "2025-10-10T14:00:00"
  }
}
```

**Common Issues:**
- **uv not installed**: Falls back to pip, but uv is recommended
- **Dependency installation fails**: Check Python version and network connectivity
- **pytest not found**: Verify dependencies installed correctly

**Example:**
```python
result = execute_workflow("tdd-phase3-scaffolding", {
    "project_path": "/projects/user-api",
    "python_version": "3.12",
    "project_name": "user_api"
})
# Creates complete project structure
# Installs dependencies
# Verifies pytest setup
```

---

### Phase 4: TDD Module Implementation

**Purpose**: Implement modules using RED-GREEN-REFACTOR TDD cycle

**⚠️ CRITICAL**: Phase 4 must be executed **ONCE PER MODULE**

**Inputs:**
- `module_name` (required): Name of module to implement
- `project_path` (default: "."): Project root directory
- `state_file` (default: ".tdd-state.json"): State file path
- `test_path` (default: "tests"): Test directory
- `source_path` (default: "src"): Source code directory
- `coverage_threshold` (default: 80): Minimum coverage percentage
- `python_command` (default: "python"): Python executable

**Interactive Pauses (8 total per module):**
1. **Confirm Start**: Approve starting module implementation
2. **Request Tests** (RED): Provide complete test code (AAA pattern)
3. **Confirm RED Phase**: Verify tests fail correctly
4. **Request Implementation** (GREEN): Provide minimum implementation code
5. **Confirm GREEN Phase**: Verify tests now pass
6. **Request Refactor** (REFACTOR): Provide refactored code
7. **Confirm Refactor**: Verify tests still pass after refactor
8. **Ask Continue**: Continue to next module or finish?

**TDD Cycle Enforced:**

```text
┌─────────────────────────────────────┐
│  RED: Write Tests First             │
│  - Tests MUST fail initially        │
│  - Workflow validates failure       │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  GREEN: Implement Minimum Code      │
│  - Tests MUST pass after impl       │
│  - Workflow validates success       │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  REFACTOR: Improve Code Quality     │
│  - Tests MUST still pass            │
│  - Workflow validates refactor      │
└─────────────────────────────────────┘
```

**Outputs per Module:**
- `tests/test_<module_name>.py`: Complete unit tests
- `src/<module_name>.py`: Implemented and refactored code
- `.tdd-state.json`: Updated with module completion

**State Changes:**
```json
{
  "current_phase": "phase4_implementation",
  "completed_modules": ["user_service"],
  "modules_status": {
    "user_service": {
      "tests_count": 15,
      "coverage": 87.5,
      "refactored": true,
      "phase": "complete"
    }
  }
}
```

**Common Issues:**
- **Tests pass before implementation**: ERROR - tests weren't written correctly
- **Tests fail after implementation**: Review implementation against test requirements
- **Coverage below threshold**: Add edge case tests
- **Tests fail after refactor**: Refactoring changed behavior - fix or revert

**Example:**
```python
# Read modules from state
state = read_json_state("/projects/user-api/.tdd-state.json")
modules = state["modules"]  # ["user_service", "task_service", "auth_service"]

# Implement first module
result = execute_workflow("tdd-phase4-module-tdd", {
    "project_path": "/projects/user-api",
    "module_name": "user_service"
})
# Workflow pauses 8 times for RED-GREEN-REFACTOR cycle
# Result: user_service complete with 15 passing tests, 87.5% coverage

# Continue with remaining modules...
for module in ["task_service", "auth_service"]:
    result = execute_workflow("tdd-phase4-module-tdd", {
        "project_path": "/projects/user-api",
        "module_name": module
    })
```

---

### Phase 5: Integration Testing

**Purpose**: Validate modules work correctly together through integration and E2E tests

**Inputs:**
- `project_path` (default: "."): Project root directory
- `state_file` (default: ".tdd-state.json"): State file path
- `test_path` (default: "tests"): Test directory
- `source_path` (default: "src"): Source code directory
- `python_command` (default: "python"): Python executable
- `coverage_threshold` (default: 75): Minimum integration coverage

**Interactive Pauses (4+ total):**
1. **Request Integration Tests**: LLM designs module interaction tests
2. **Request Integration Fixes** (if failures): LLM fixes integration issues
3. **Request E2E Tests**: LLM designs complete user workflow tests
4. **Request E2E Fixes** (if failures): LLM fixes E2E issues
5. **Integration Checkpoint**: Approve Phase 5 completion

**What Gets Tested:**

**Integration Tests** (`tests/integration/test_integration.py`):
- Module-to-module data flow
- Error propagation across boundaries
- Configuration dependencies
- Transaction handling
- API contract compliance

**E2E Tests** (`tests/e2e/test_e2e.py`):
- Complete user workflows
- Entry point to final output
- Realistic usage scenarios
- Configuration and environment setup
- Data persistence and state management

**Outputs:**
- `tests/integration/test_integration.py`: Integration tests
- `tests/e2e/test_e2e.py`: End-to-end tests
- `.tdd-state.json`: Updated with test metrics

**State Changes:**
```json
{
  "current_phase": "phase5_complete",
  "phases_completed": [..., "phase5_complete"],
  "phase5": {
    "integration_tests": {
      "passed": 8,
      "failed": 0,
      "total": 8
    },
    "e2e_tests": {
      "passed": 5,
      "failed": 0,
      "total": 5
    },
    "all_passing": true,
    "completed_at": "2025-10-10T16:00:00"
  }
}
```

**Common Issues:**
- **Integration tests fail**: Check module interface compatibility
- **E2E tests fail**: Verify complete workflow setup and teardown
- **Tests can't find modules**: Check PYTHONPATH and import statements

**Example:**
```python
result = execute_workflow("tdd-phase5-integration", {
    "project_path": "/projects/user-api"
})
# Workflow pauses for integration test design
# Runs integration tests (8 tests pass)
# Workflow pauses for E2E test design
# Runs E2E tests (5 tests pass)
# All integration and E2E tests passing ✓
```

---

### Phase 6: Validation & Quality Gates

**Purpose**: Comprehensive quality validation and PRD compliance verification

**Inputs:**
- `project_path` (default: "."): Project root directory
- `state_file` (default: ".tdd-state.json"): State file path
- `source_path` (default: "src"): Source code directory
- `test_path` (default: "tests"): Test directory
- `coverage_threshold` (default: 80): Minimum overall coverage
- `python_command` (default: "python"): Python executable
- `strict_quality` (default: true): Enable strict quality mode
- `enable_security_scan` (default: true): Enable security scanning

**Interactive Pauses (3+ total):**
1. **Request Quality Fixes** (if failures): LLM fixes linting/type/format issues
2. **Ask Performance Testing**: Decide if performance testing is needed
3. **Request Performance Benchmarks** (if yes): Define performance criteria
4. **Request PRD Compliance**: Verify all requirements implemented
5. **Final Quality Checkpoint**: Approve production readiness

**Quality Gates Validated:**

**1. Test Suite:**
- All tests passing (unit + integration + E2E)
- Overall coverage ≥ threshold (default 80%)

**2. Code Quality:**
- Linting (ruff): No violations
- Type checking (mypy): All types correct
- Formatting (ruff format): Code formatted consistently

**3. Security:**
- Bandit: No high/medium severity issues
- Safety: No vulnerable dependencies

**4. PRD Compliance:**
- All requirements from Phase 1 implemented
- Success criteria validated
- No missing functionality

**Outputs:**
- `QUALITY_REPORT.md`: Comprehensive quality metrics
- `.tdd-state.json`: Updated with Phase 6 validation

**State Changes:**
```json
{
  "current_phase": "phase6_complete",
  "phases_completed": [..., "phase6_complete"],
  "phase6": {
    "total_tests": 67,
    "tests_passing": 67,
    "overall_coverage": 89.5,
    "quality_metrics": {
      "linting": true,
      "type_checking": true,
      "formatting": true,
      "all_passed": true
    },
    "security_scan": {
      "bandit_exit_code": 0,
      "safety_exit_code": 0,
      "clean": true
    },
    "prd_compliance_percent": 100,
    "all_quality_gates_passed": true,
    "ready_for_deployment": true,
    "completed_at": "2025-10-10T17:00:00"
  }
}
```

**Common Issues:**
- **Coverage below threshold**: Add tests for uncovered code paths
- **Linting failures**: Fix code style issues
- **Type checking failures**: Add type hints and fix type errors
- **Security issues**: Address bandit/safety warnings
- **PRD compliance < 100%**: Implement missing requirements

**Example:**
```python
result = execute_workflow("tdd-phase6-validation", {
    "project_path": "/projects/user-api",
    "coverage_threshold": 85,
    "enable_security_scan": true
})
# Runs full test suite: 67 tests passing, 89.5% coverage ✓
# Runs quality checks: All gates passing ✓
# Runs security scans: Clean ✓
# Verifies PRD compliance: 100% ✓
# Generates QUALITY_REPORT.md
# Project is production-ready! 🎉
```

---

### Phase 7: Finalization & Documentation

**Purpose**: Generate comprehensive documentation and prepare for deployment

**Inputs:**
- `project_path` (default: "."): Project root directory
- `state_file` (default: ".tdd-state.json"): State file path
- `project_name` (required): Project name
- `version` (default: "1.0.0"): Project version
- `author` (default: "Development Team"): Author/organization
- `python_version` (default: "3.12+"): Python version requirement
- `coverage_threshold` (default: 80): Coverage from Phase 6

**Interactive Pauses (5 total):**
1. **Request Deployment Guide**: LLM generates deployment procedures
2. **Request User Guide**: LLM generates user documentation
3. **Request API Docs**: LLM generates API reference
4. **Request Operations Runbook**: LLM generates operations guide
5. **Request README Update**: LLM generates project overview
6. **Final Completion Checkpoint**: Confirm project completion

**Documentation Generated:**

**1. docs/DEPLOYMENT.md** - Deployment Guide:
- System requirements
- Installation steps
- Configuration (env vars, secrets)
- Service management
- Database setup
- Troubleshooting
- Rollback procedures

**2. docs/USER_GUIDE.md** - User Documentation:
- Getting started
- Core features with examples
- Common workflows
- Troubleshooting
- Advanced usage
- Support information

**3. docs/API.md** - API Documentation:
- API overview and versioning
- Authentication
- Endpoints (method, path, parameters, responses)
- Error handling
- Code examples (curl, Python, JavaScript)
- Data models and schemas

**4. docs/RUNBOOK.md** - Operations Runbook:
- Monitoring guidelines
- Alert response procedures
- Common issues and solutions
- Performance tuning
- Backup and restore
- Incident response playbook
- Maintenance procedures

**5. docs/DEPLOYMENT_CHECKLIST.md** - Deployment Checklist:
- Pre-deployment verification
- Staging deployment steps
- Production deployment steps
- Post-deployment validation
- Rollback plan
- Monitoring and alerts

**6. README.md** - Project Overview:
- Project description
- Features
- Quick start
- Installation
- Usage examples
- Documentation links
- Development setup

**7. CHANGELOG.md** - Version History:
- Initial release notes
- Features implemented
- Technical details

**Outputs:**
- Complete documentation suite (7 files)
- `requirements.txt` (generated from `pyproject.toml`)
- `.tdd-state.json`: Updated with `project_complete: true`

**State Changes:**
```json
{
  "current_phase": "phase7_complete",
  "project_complete": true,
  "phases_completed": [..., "phase7_complete"],
  "project_info": {
    "name": "user-management-api",
    "version": "1.0.0",
    "completion_date": "2025-10-10T18:00:00"
  },
  "phase7": {
    "documentation_complete": true,
    "deployment_guide": "docs/DEPLOYMENT.md",
    "user_guide": "docs/USER_GUIDE.md",
    "api_docs": "docs/API.md",
    "runbook": "docs/RUNBOOK.md",
    "package_verified": true,
    "ready_for_deployment": true,
    "completed_at": "2025-10-10T18:00:00"
  }
}
```

**Common Issues:**
- **Documentation incomplete**: Review and expand generated docs
- **Missing deployment steps**: Add environment-specific instructions
- **API docs lack examples**: Add code samples for common use cases

**Example:**
```python
result = execute_workflow("tdd-phase7-finalization", {
    "project_path": "/projects/user-api",
    "project_name": "User Management API",
    "version": "1.0.0",
    "author": "Backend Team"
})
# Workflow pauses 5 times for documentation generation
# Creates 7 complete documentation files
# Project is deployment-ready! 🚀
```

---

## Helper Workflows

### python-run-tests

**Purpose**: Execute pytest with coverage and return structured results

**Inputs:**
- `test_path` (default: "tests/"): Test directory or file
- `source_path` (default: "src/"): Source code for coverage
- `coverage_threshold` (default: 80): Minimum coverage percentage
- `pytest_args` (default: "-v"): Additional pytest arguments
- `working_dir` (default: "."): Execution directory
- `venv_path` (default: ""): Virtual environment path

**Outputs:**
- `exit_code`: pytest exit code (0 = success)
- `success`: boolean (true if all tests passed)
- `tests_passed`: Number of passing tests
- `tests_failed`: Number of failing tests
- `tests_skipped`: Number of skipped tests
- `coverage_percent`: Coverage percentage
- `coverage_threshold_met`: boolean
- `stdout`: Full pytest output
- `stderr`: pytest error output

**Usage:**
```python
result = execute_workflow("python-run-tests", {
    "test_path": "tests/",
    "source_path": "src/",
    "coverage_threshold": 85
})
# Returns: tests_passed=67, coverage_percent=89.5
```

---

### python-quality-check

**Purpose**: Run comprehensive Python quality checks

**Inputs:**
- `source_path` (default: "src/"): Source code directory
- `strict` (default: false): Enable strict mode
- `check_linting` (default: true): Enable ruff linting
- `check_types` (default: true): Enable mypy type checking
- `check_formatting` (default: true): Enable ruff format validation
- `working_dir` (default: "."): Execution directory
- `venv_path` (default: ""): Virtual environment path

**Outputs:**
- `linting_passed`: boolean
- `linting_exit_code`: ruff check exit code
- `typing_passed`: boolean
- `typing_exit_code`: mypy exit code
- `formatting_passed`: boolean
- `formatting_exit_code`: ruff format exit code
- `all_checks_passed`: boolean (all checks passed)
- `linting_output`: ruff output
- `typing_output`: mypy output
- `formatting_output`: ruff format output

**Usage:**
```python
result = execute_workflow("python-quality-check", {
    "source_path": "src/",
    "strict": true
})
# Returns: all_checks_passed=true (linting ✓, types ✓, format ✓)
```

---

## State Management

### State File Structure

The `.tdd-state.json` file tracks complete project state:

```json
{
  "workflow_version": "1.0",
  "created_at": "2025-10-10T11:00:00",
  "current_phase": "phase4_implementation",
  "phases_completed": ["phase1", "phase2", "phase3"],
  "project_complete": false,

  "phase1": {
    "technical_spec_path": "TECHNICAL_SPEC.md",
    "requirements_count": 15,
    "requirements_list": ["REQ-001", "REQ-002", ...],
    "completed_at": "2025-10-10T12:00:00",
    "ambiguities_resolved": true
  },

  "phase2": {
    "architecture_path": "ARCHITECTURE.md",
    "module_count": 3,
    "modules": ["user_service", "task_service", "auth_service"],
    "completed_at": "2025-10-10T13:00:00",
    "test_strategy_defined": true
  },

  "phase3": {
    "project_name": "user-api",
    "setup_successful": true,
    "dependencies_installed": true,
    "test_framework_ready": true,
    "completed_at": "2025-10-10T14:00:00"
  },

  "modules": ["user_service", "task_service", "auth_service"],
  "completed_modules": ["user_service"],
  "modules_status": {
    "user_service": {
      "tests_count": 15,
      "coverage": 87.5,
      "refactored": true,
      "phase": "complete"
    }
  }
}
```

### State File Best Practices

**1. Version Control:**
```bash
# Add .tdd-state.json to .gitignore (sensitive to workflow state)
echo ".tdd-state.json" >> .gitignore

# OR commit it to track progress (recommended for team projects)
git add .tdd-state.json
git commit -m "docs: update TDD state after Phase 2 completion"
```

**2. Backup Before Critical Operations:**
```bash
# Before starting Phase 4 (iterative)
cp .tdd-state.json .tdd-state.json.backup

# Restore if needed
mv .tdd-state.json.backup .tdd-state.json
```

**3. Manual State Inspection:**
```bash
# Pretty-print state
cat .tdd-state.json | python -m json.tool

# Check current phase
jq '.current_phase' .tdd-state.json

# List completed modules
jq '.completed_modules' .tdd-state.json
```

**4. State Validation:**
```python
import json
from pathlib import Path

state = json.loads(Path(".tdd-state.json").read_text())

# Verify Phase 3 complete before Phase 4
assert "phase3" in state["phases_completed"]
assert state["setup_ready"] == True

# Verify modules defined before implementing
assert len(state["modules"]) > 0

# Check module completion status
for module in state["modules"]:
    status = state["modules_status"].get(module, {})
    print(f"{module}: {status.get('phase', 'not started')}")
```

---

## Best Practices

### 1. State Management

**Do:**
- ✅ Commit `.tdd-state.json` to version control for team projects
- ✅ Backup state before major operations (especially Phase 4)
- ✅ Review state after each phase to verify progress
- ✅ Use state to resume interrupted workflows

**Don't:**
- ❌ Manually edit state file (use workflows to update)
- ❌ Delete state file mid-workflow (lose all progress)
- ❌ Skip phase prerequisites (workflows will error)

### 2. Phase Execution

**Phase 1 (Analysis):**
- Take time to resolve ambiguities thoroughly
- Define measurable success criteria (enables validation)
- Document all constraints (guides architecture)

**Phase 2 (Architecture):**
- Keep modules small and focused (single responsibility)
- Minimize inter-module dependencies (easier to test)
- Define clear interfaces with types (prevents integration issues)

**Phase 3 (Scaffolding):**
- Use `uv` for dependency management (faster, more reliable)
- Verify pytest setup with `pytest --collect-only`
- Review generated `pyproject.toml` for accuracy

**Phase 4 (TDD Implementation):**
- **ALWAYS write tests first** (RED phase validates this)
- Implement minimum code to pass tests (avoid over-engineering)
- Refactor with confidence (tests protect behavior)
- Complete one module fully before starting next
- Commit after each module completion

**Phase 5 (Integration):**
- Test realistic data flows between modules
- Test error propagation across boundaries
- Create E2E tests for complete user workflows

**Phase 6 (Validation):**
- Don't bypass quality gates (they catch real issues)
- Fix linting/type errors immediately (don't accumulate tech debt)
- Review security scan results carefully
- Verify 100% PRD compliance before proceeding

**Phase 7 (Finalization):**
- Review generated documentation (LLM may miss specifics)
- Test deployment procedures in staging first
- Follow deployment checklist completely

### 3. Quality Standards

**Test Coverage:**
- **Unit tests**: ≥80% per module (enforced in Phase 4)
- **Integration tests**: ≥75% of integration points
- **E2E tests**: Cover all major user workflows
- **Overall**: ≥80% combined coverage (enforced in Phase 6)

**Code Quality:**
- **Linting**: Zero ruff violations
- **Type checking**: All functions type-hinted, zero mypy errors
- **Formatting**: Consistent ruff format
- **Complexity**: Cyclomatic complexity ≤10 per function

**Security:**
- **Bandit**: Zero high/medium severity issues
- **Safety**: Zero vulnerable dependencies
- **Secrets**: Never commit credentials (use environment variables)

### 4. Documentation

**During Development:**
- Phase 1 creates TECHNICAL_SPEC.md
- Phase 2 creates ARCHITECTURE.md
- Phase 7 creates comprehensive docs

**Documentation Review Checklist:**
- ✅ Deployment guide has environment-specific instructions
- ✅ User guide has real code examples
- ✅ API docs have curl/Python/JavaScript examples
- ✅ Runbook has alert response procedures
- ✅ README has quick start that actually works

### 5. Team Workflow

**For Teams:**
1. One person runs Phase 1-3 (setup)
2. Distribute Phase 4 modules across team members:
   - Person A: `user_service` module
   - Person B: `task_service` module
   - Person C: `auth_service` module
3. Merge completed modules
4. One person runs Phase 5-7 (integration + validation + finalization)

**For Solo Developers:**
- Run complete pipeline: `tdd-orchestrator`
- Take breaks between phases (avoid fatigue)
- Review checkpoints carefully before approving

---

## Examples

### Example 1: Simple REST API

**Project**: User Management API with authentication

**PRD Summary:**
- User registration (email + password)
- User login (JWT tokens)
- User profile CRUD
- Password reset flow

**Execution:**
```python
# Full pipeline execution
result = execute_workflow("tdd-orchestrator", {
    "project_name": "user-management-api",
    "project_path": "/projects/user-api",
    "prd_path": "PRD.md",
    "version": "1.0.0",
    "author": "Backend Team",
    "python_version": "3.12",
    "coverage_threshold": 85
})

# Workflow progression:
# Phase 1: PRD → TECHNICAL_SPEC.md (12 requirements)
# Phase 2: TECHNICAL_SPEC → ARCHITECTURE.md (3 modules)
#   - user_service (registration, profile CRUD)
#   - auth_service (login, JWT, password reset)
#   - email_service (email notifications)
# Phase 3: Project structure created, dependencies installed
# Phase 4: Implement modules (requires manual iteration):
#   - user_service: 18 tests, 92% coverage
#   - auth_service: 24 tests, 89% coverage
#   - email_service: 8 tests, 85% coverage
# Phase 5: Integration tests (10 tests) + E2E tests (6 tests)
# Phase 6: Quality validation (all gates passed, 88% overall coverage)
# Phase 7: Documentation generated (deployment guide, API docs, etc.)
```

**Outcome:**
- 50 total tests (all passing)
- 88% overall coverage
- Complete documentation suite
- Production-ready deployment

---

### Example 2: Data Processing Pipeline

**Project**: CSV data processing with validation and transformation

**PRD Summary:**
- Read CSV files
- Validate data against schema
- Transform data (clean, normalize)
- Export to database

**Phase 4 Module Implementation:**
```python
# Modules identified in Phase 2:
modules = ["csv_reader", "validator", "transformer", "db_exporter"]

# Implement each module with TDD
for module in modules:
    result = execute_workflow("tdd-phase4-module-tdd", {
        "project_path": "/projects/data-pipeline",
        "module_name": module,
        "coverage_threshold": 90  # High coverage for data processing
    })

    # Module: csv_reader
    # - RED: Write tests for CSV parsing (edge cases: empty, malformed, large)
    # - GREEN: Implement CSV reading with pandas
    # - REFACTOR: Add streaming for large files
    # - Result: 12 tests, 94% coverage

    # Module: validator
    # - RED: Write tests for schema validation
    # - GREEN: Implement validation rules
    # - REFACTOR: Extract validation logic to reusable functions
    # - Result: 16 tests, 91% coverage

    # Continue for transformer and db_exporter...
```

**Outcome:**
- Robust data pipeline with 58 tests
- 92% overall coverage
- Handles edge cases (empty files, malformed data)
- Production-ready with monitoring

---

### Example 3: Resuming After Pause

**Scenario**: Phase 4 module implementation paused for test writing

```python
# Start Phase 4 for user_service
result = execute_workflow("tdd-phase4-module-tdd", {
    "project_path": "/projects/user-api",
    "module_name": "user_service"
})

# Workflow pauses at "Request Tests" step
# result["status"] == "paused"
# result["checkpoint_id"] == "pause_abc123"

# LLM or human provides test code
test_code = """
import pytest
from user_service import UserService

def test_create_user():
    service = UserService()
    user = service.create_user("test@example.com", "password123")
    assert user.email == "test@example.com"
    assert user.id is not None

def test_create_user_duplicate_email():
    service = UserService()
    service.create_user("test@example.com", "password123")
    with pytest.raises(DuplicateError):
        service.create_user("test@example.com", "password456")

# ... more tests
"""

# Resume workflow with test code
resume_result = resume_workflow(
    checkpoint_id="pause_abc123",
    llm_response=test_code
)

# Workflow continues:
# - Writes test file
# - Runs tests (expects failure - RED phase)
# - Pauses again for implementation
```

---

## Troubleshooting

### State File Issues

**Problem**: `State file not found`

**Solution**:
```bash
# Phase 1 initializes state - run it first
execute_workflow("tdd-phase1-analysis", {
    "project_path": "/projects/my-project",
    "prd_path": "PRD.md"
})
```

**Problem**: `Phase N not complete`

**Solution**: Complete previous phase before proceeding
```python
# Check state
state = read_json_state(".tdd-state.json")
print(state["phases_completed"])  # Verify phase completion

# Complete missing phase
execute_workflow("tdd-phase{N}-...", {...})
```

**Problem**: State file corrupted

**Solution**: Restore from backup or reinitialize
```bash
# Restore backup
cp .tdd-state.json.backup .tdd-state.json

# Or restart from Phase 1
rm .tdd-state.json
execute_workflow("tdd-phase1-analysis", {...})
```

---

### Phase 4 (TDD) Issues

**Problem**: Tests pass without implementation (RED phase fails)

**Cause**: Tests are not comprehensive enough

**Solution**: Write tests that actually exercise the module
```python
# Bad test (always passes)
def test_user_service():
    assert True

# Good test (requires implementation)
def test_create_user():
    service = UserService()
    user = service.create_user("test@example.com", "pass123")
    assert user.email == "test@example.com"
    assert user.password_hash != "pass123"  # Hashed
```

**Problem**: Tests fail after implementation (GREEN phase fails)

**Cause**: Implementation doesn't meet test requirements

**Solution**: Review test output and fix implementation
```bash
# Check test output
pytest tests/test_user_service.py -v

# Common issues:
# - Missing function parameters
# - Wrong return type
# - Not handling edge cases
```

**Problem**: Coverage below threshold

**Cause**: Missing edge case tests

**Solution**: Add comprehensive test coverage
```python
# Add edge cases
def test_create_user_invalid_email():
    with pytest.raises(ValidationError):
        service.create_user("invalid-email", "pass123")

def test_create_user_empty_password():
    with pytest.raises(ValidationError):
        service.create_user("test@example.com", "")
```

---

### Quality Gate Failures

**Problem**: Linting failures (ruff)

**Solution**: Fix code style issues
```bash
# See linting errors
ruff check src/

# Auto-fix many issues
ruff check src/ --fix

# Check again
ruff check src/
```

**Problem**: Type checking failures (mypy)

**Solution**: Add type hints
```python
# Before (fails mypy)
def create_user(email, password):
    return User(email, password)

# After (passes mypy)
def create_user(email: str, password: str) -> User:
    return User(email, password)
```

**Problem**: Formatting failures (ruff format)

**Solution**: Format code
```bash
# Format all code
ruff format src/ tests/

# Verify
ruff format --check src/ tests/
```

---

### Security Scan Issues

**Problem**: Bandit finds security issues

**Common Issues**:
- Hardcoded passwords
- SQL injection vulnerability
- Unsafe YAML loading

**Solution**: Address each issue
```python
# Bad: Hardcoded password
password = "admin123"

# Good: Environment variable
import os
password = os.environ["ADMIN_PASSWORD"]

# Bad: SQL injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Good: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Problem**: Safety finds vulnerable dependencies

**Solution**: Update dependencies
```bash
# See vulnerabilities
safety check

# Update specific package
pip install --upgrade <package-name>

# Or update all dependencies
pip install --upgrade -r requirements.txt
```

---

### Integration Test Issues

**Problem**: Integration tests can't find modules

**Solution**: Fix Python path
```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# Or install package in editable mode
pip install -e .
```

**Problem**: Integration tests fail but unit tests pass

**Cause**: Module interface mismatch

**Solution**: Check module interfaces
```python
# Verify interface contracts
# Module A expects User object
def process_user(user: User) -> Result:
    ...

# Module B must return User object
def get_user(id: str) -> User:
    ...
```

---

## Reference

### Workflow Summary Table

| Workflow | Purpose | Interactive Pauses | Primary Outputs |
|----------|---------|-------------------|-----------------|
| `tdd-orchestrator` | Complete pipeline | 25+ (all phases) | Complete project |
| `tdd-phase1-analysis` | PRD → Technical Spec | 6 | TECHNICAL_SPEC.md |
| `tdd-phase2-architecture` | Architecture design | 6 | ARCHITECTURE.md |
| `tdd-phase3-scaffolding` | Project setup | 1 | Project structure |
| `tdd-phase4-module-tdd` | TDD implementation | 8 per module | Module + tests |
| `tdd-phase5-integration` | Integration testing | 4+ | Integration + E2E tests |
| `tdd-phase6-validation` | Quality validation | 3+ | QUALITY_REPORT.md |
| `tdd-phase7-finalization` | Documentation | 5 | Docs + deployment |
| `python-run-tests` | Test execution | 0 | Test results |
| `python-quality-check` | Quality checks | 0 | Quality metrics |

---

### Key Files and Locations

**Project Structure:**
```text
project-root/
├── .tdd-state.json                 # State tracking (may be gitignored)
├── PRD.md                           # Product Requirements (Phase 1 input)
├── TECHNICAL_SPEC.md                # Technical Spec (Phase 1 output)
├── ARCHITECTURE.md                  # Architecture (Phase 2 output)
├── QUALITY_REPORT.md                # Quality Report (Phase 6 output)
├── README.md                        # Project Overview (Phase 7 output)
├── CHANGELOG.md                     # Version History (Phase 7 output)
├── pyproject.toml                   # Python config (Phase 3)
├── requirements.txt                 # Deployment deps (Phase 7)
├── .gitignore                       # Git ignore (Phase 3)
├── src/                             # Source code
│   └── <project_name>/
│       ├── __init__.py
│       ├── <module1>.py             # Phase 4 output
│       └── <module2>.py             # Phase 4 output
├── tests/                           # Tests
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures (Phase 3)
│   ├── test_<module1>.py            # Unit tests (Phase 4)
│   ├── integration/
│   │   └── test_integration.py     # Integration tests (Phase 5)
│   └── e2e/
│       └── test_e2e.py              # E2E tests (Phase 5)
└── docs/                            # Documentation (Phase 7)
    ├── DEPLOYMENT.md
    ├── USER_GUIDE.md
    ├── API.md
    ├── RUNBOOK.md
    └── DEPLOYMENT_CHECKLIST.md
```

---

### Command Quick Reference

**Start Complete Pipeline:**
```python
execute_workflow("tdd-orchestrator", {
    "project_name": "my-project",
    "project_path": "/path/to/project",
    "prd_path": "PRD.md",
    "version": "1.0.0"
})
```

**Execute Individual Phases:**
```python
# Phase 1: Analysis
execute_workflow("tdd-phase1-analysis", {"project_path": "/path"})

# Phase 2: Architecture
execute_workflow("tdd-phase2-architecture", {"project_path": "/path"})

# Phase 3: Scaffolding
execute_workflow("tdd-phase3-scaffolding", {
    "project_path": "/path",
    "python_version": "3.12"
})

# Phase 4: TDD (per module)
execute_workflow("tdd-phase4-module-tdd", {
    "project_path": "/path",
    "module_name": "user_service"
})

# Phase 5: Integration
execute_workflow("tdd-phase5-integration", {"project_path": "/path"})

# Phase 6: Validation
execute_workflow("tdd-phase6-validation", {
    "project_path": "/path",
    "coverage_threshold": 85
})

# Phase 7: Finalization
execute_workflow("tdd-phase7-finalization", {
    "project_path": "/path",
    "project_name": "my-project",
    "version": "1.0.0"
})
```

**Helper Workflows:**
```python
# Run tests with coverage
execute_workflow("python-run-tests", {
    "test_path": "tests/",
    "source_path": "src/",
    "coverage_threshold": 80
})

# Run quality checks
execute_workflow("python-quality-check", {
    "source_path": "src/",
    "strict": true
})
```

**Resume Paused Workflow:**
```python
# Resume with LLM response
resume_workflow(
    checkpoint_id="pause_abc123",
    llm_response="<your response>"
)
```

**Check State:**
```python
# Read current state
state = read_json_state("/path/to/.tdd-state.json")
print(state["current_phase"])
print(state["phases_completed"])
print(state["modules"])
print(state["completed_modules"])
```

---

### Additional Resources

**Related Documentation:**
- [Workflow Engine Architecture](../ARCHITECTURE.md) - System design
- [MCP Server Guide](../CLAUDE.md) - Server conventions and patterns
- [Workflow Block Reference](../README.md) - Available workflow blocks

**External Resources:**
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development) - TDD methodology
- [Pytest Documentation](https://docs.pytest.org/) - Test framework
- [Ruff Documentation](https://docs.astral.sh/ruff/) - Linting and formatting
- [Mypy Documentation](https://mypy.readthedocs.io/) - Type checking

---

## Summary

The TDD Workflow System provides a **comprehensive, structured approach** to building production-ready applications:

**7 Phases:**
1. **Analysis**: PRD → Technical Spec
2. **Architecture**: Design system and modules
3. **Scaffolding**: Setup project structure
4. **TDD Implementation**: RED-GREEN-REFACTOR per module
5. **Integration**: Module integration + E2E tests
6. **Validation**: Quality gates + PRD compliance
7. **Finalization**: Complete documentation

**Key Benefits:**
- Test-first discipline enforced
- Quality gates prevent shortcuts
- State management enables resumability
- Complete documentation generated
- Production-ready deployment procedures

**Next Steps:**
1. Prepare your PRD document
2. Run `tdd-orchestrator` or start with Phase 1
3. Follow interactive prompts
4. Iterate Phase 4 for each module
5. Deploy with confidence

**Questions or Issues?**
- Check [Troubleshooting](#troubleshooting) section
- Review state file for progress
- Consult workflow YAML files for detailed behavior

---

*Generated by MCP Workflows Documentation System*
*Version 1.0 | Last Updated: 2025-10-10*
