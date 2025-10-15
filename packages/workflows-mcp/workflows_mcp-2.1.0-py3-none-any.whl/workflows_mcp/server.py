"""FastMCP server initialization for workflows-mcp.

This module initializes the MCP server and registers workflow execution tools
following the official Anthropic Python SDK patterns.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .engine import (
    WorkflowExecutor,
    WorkflowRegistry,
    load_workflow_from_yaml,
)

logger = logging.getLogger(__name__)

# Initialize MCP server with descriptive name
mcp = FastMCP("workflows")

# Initialize workflow registry
workflow_registry = WorkflowRegistry()

# Initialize workflow executor (will be loaded with registry workflows)
executor = WorkflowExecutor()


# =============================================================================
# Workflow Loading and Initialization
# =============================================================================


def load_workflows() -> None:
    """
    Load workflows from built-in templates and optional user-provided directories.

    This function:
    1. Parses WORKFLOWS_TEMPLATE_PATHS environment variable (comma-separated paths)
    2. Builds directory list: [built_in_templates, ...user_template_paths]
    3. Uses workflow_registry.load_from_directories() with on_duplicate="overwrite"
    4. Loads workflows from registry into executor
    5. Logs clearly which templates are built-in vs user-provided

    Priority: User templates OVERRIDE built-in templates by name.

    Environment Variables:
        WORKFLOWS_TEMPLATE_PATHS: Comma-separated list of additional template directories.
            Paths can use ~ for home directory. Empty or missing variable is handled gracefully.

    Example:
        WORKFLOWS_TEMPLATE_PATHS="~/my-workflows,/opt/company-workflows"
        # Load order:
        # 1. Built-in: src/workflows_mcp/templates/
        # 2. User: ~/my-workflows (overrides built-in by name)
        # 3. User: /opt/company-workflows (overrides both by name)
    """
    # Built-in templates directory
    built_in_templates = Path(__file__).parent / "templates"

    # Parse WORKFLOWS_TEMPLATE_PATHS environment variable
    env_paths_str = os.getenv("WORKFLOWS_TEMPLATE_PATHS", "")
    user_template_paths: list[Path] = []

    if env_paths_str.strip():
        # Split by comma, strip whitespace, expand ~, and convert to Path
        for path_str in env_paths_str.split(","):
            path_str = path_str.strip()
            if path_str:
                # Expand ~ for home directory
                expanded_path = Path(path_str).expanduser()
                user_template_paths.append(expanded_path)

        logger.info(f"User template paths from WORKFLOWS_TEMPLATE_PATHS: {user_template_paths}")

    # Build directory list: built-in first, then user paths (user paths override)
    # Cast to list[Path | str] for type compatibility with load_from_directories
    directories_to_load: list[Path | str] = [built_in_templates]
    directories_to_load.extend(user_template_paths)

    logger.info(f"Loading workflows from {len(directories_to_load)} directories")
    logger.info(f"  Built-in: {built_in_templates}")
    for idx, user_path in enumerate(user_template_paths, 1):
        logger.info(f"  User {idx}: {user_path}")

    # Load workflows from all directories with overwrite policy (user templates override)
    result = workflow_registry.load_from_directories(directories_to_load, on_duplicate="overwrite")

    if not result.is_success:
        logger.error(f"Failed to load workflows: {result.error}")
        return

    # Log loading results per directory
    load_counts = result.value
    if load_counts:
        logger.info("Workflow loading summary:")
        built_in_count = load_counts.get(str(built_in_templates), 0)
        logger.info(f"  Built-in templates: {built_in_count} workflows")

        for user_path in user_template_paths:
            user_count = load_counts.get(str(user_path), 0)
            logger.info(f"  User templates ({user_path}): {user_count} workflows")

    # Load all registry workflows into executor
    total_workflows = 0
    for workflow in workflow_registry.list_all():
        executor.load_workflow(workflow)
        total_workflows += 1

    logger.info(f"Successfully loaded {total_workflows} total workflows into executor")


# =============================================================================
# MCP Tools (following official SDK decorator pattern)
# =============================================================================


@mcp.tool()
async def execute_workflow(
    workflow: str,
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a DAG-based workflow with inputs.

    Supports git operations, bash commands, templates, and workflow composition.

    Output verbosity is controlled by WORKFLOWS_LOG_LEVEL environment variable:
    - Non-DEBUG (default): Returns empty blocks/metadata (minimal)
    - DEBUG: Returns full blocks/metadata (detailed)

    Args:
        workflow: Workflow name (e.g., 'sequential-echo', 'parallel-echo')
        inputs: Runtime inputs as key-value pairs for block variable substitution

    Returns:
        Dictionary with consistent structure:
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}
        - blocks/metadata are empty dicts when WORKFLOWS_LOG_LEVEL != DEBUG
        - blocks/metadata are fully populated when WORKFLOWS_LOG_LEVEL = DEBUG
    """
    # Execute workflow - executor returns WorkflowResponse directly
    response = await executor.execute_workflow(workflow, inputs)
    return response.model_dump()


@mcp.tool()
async def execute_inline_workflow(
    workflow_yaml: str,
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a workflow provided as YAML string without registering it.

    Enables dynamic workflow execution without file system modifications.
    Useful for ad-hoc workflows or tests.

    Output verbosity is controlled by WORKFLOWS_LOG_LEVEL environment variable:
    - Non-DEBUG (default): Returns empty blocks/metadata (minimal)
    - DEBUG: Returns full blocks/metadata (detailed)

    Args:
        workflow_yaml: Complete workflow definition as YAML string including
                      name, description, blocks, etc.
        inputs: Runtime inputs as key-value pairs for block variable substitution

    Returns:
        Dictionary with consistent structure on success:
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}
        - blocks/metadata are empty dicts when WORKFLOWS_LOG_LEVEL != DEBUG
        - blocks/metadata are fully populated when WORKFLOWS_LOG_LEVEL = DEBUG

        On failure: {"status": "failure", "error": "..."}
        On pause: {"status": "paused", "checkpoint_id": "...", "prompt": "...", "message": "..."}

    Example:
        execute_inline_workflow(
            workflow_yaml='''
            name: rust-quality-check
            description: Quality checks for Rust projects
            tags: [rust, quality, linting]

            inputs:
              source_path:
                type: string
                default: "src/"

            blocks:
              - id: lint
                type: Shell
                inputs:
                  command: cargo clippy -- -D warnings
                  working_dir: "${source_path}"

              - id: format_check
                type: Shell
                inputs:
                  command: cargo fmt -- --check
                depends_on: [lint]

            outputs:
              linting_passed: "${lint.success}"
              formatting_passed: "${format_check.success}"
            ''',
            inputs={"source_path": "/path/to/rust/project"}
        )
    """
    # Parse YAML string to WorkflowDefinition
    load_result = load_workflow_from_yaml(workflow_yaml, source="<inline-workflow>")

    if not load_result.is_success:
        return {
            "status": "failure",
            "error": f"Failed to parse workflow YAML: {load_result.error}",
        }

    workflow_def = load_result.value
    if workflow_def is None:
        return {
            "status": "failure",
            "error": "Workflow definition parsing returned None",
        }

    # Temporarily load workflow into executor
    executor.load_workflow(workflow_def)

    # Execute workflow - executor returns WorkflowResponse directly
    response = await executor.execute_workflow(workflow_def.name, inputs)
    return response.model_dump()


@mcp.tool()
async def list_workflows(
    tags: list[str] | None = None,
    detailed: bool = False,
) -> list[dict[str, Any]]:
    """List all available workflows with descriptions.

    Discover available workflow templates filtered by tags.

    Args:
        tags: Optional list of tags to filter by. Uses AND semantics:
            workflow must have ALL specified tags.
        detailed: If True, include version, author, and outputs.
            Default (False) returns: name, description, tags, inputs.
            Detailed (True) additionally returns: version, author, outputs.

    Returns:
        List of workflow metadata dictionaries.

        Default mode (detailed=False):
        - name: Workflow name
        - description: Workflow description
        - tags: List of tags
        - inputs: Input schema with types, descriptions, required flags, defaults

        Detailed mode (detailed=True):
        Additionally includes:
        - version: Workflow version
        - author: Workflow author
        - outputs: Output mappings

    Examples:
        # All workflows (default metadata)
        list_workflows()

        # All Python-related workflows with detailed metadata
        list_workflows(tags=["python"], detailed=True)

        # All workflows with both "linting" and "python" tags
        list_workflows(tags=["python", "linting"])

        # All quality workflows
        list_workflows(tags=["quality"])
    """
    # Get workflows from registry
    if tags:
        # Use registry's filtered method with detailed parameter
        return workflow_registry.list_metadata_by_tags(tags, match_all=True, detailed=detailed)
    else:
        # Use registry's list all method with detailed parameter
        return workflow_registry.list_all_metadata(detailed=detailed)


@mcp.tool()
async def get_workflow_info(workflow: str) -> dict[str, Any]:
    """Get detailed information about a specific workflow.

    Retrieve comprehensive metadata about a workflow including block structure and dependencies.

    Args:
        workflow: Workflow name/identifier to retrieve information about

    Returns:
        Dictionary with workflow metadata: name, description, version, tags, blocks, etc.
        Returns error dict if workflow not found.
    """
    # Get workflow from registry
    if workflow not in workflow_registry:
        return {
            "error": f"Workflow not found: {workflow}",
            "available_workflows": workflow_registry.list_names(),
        }

    # Get metadata from registry
    metadata = workflow_registry.get_workflow_metadata(workflow)

    # Get workflow definition for block details
    workflow_def = workflow_registry.get(workflow)

    # Get schema if available for input/output information
    schema = workflow_registry.get_schema(workflow)

    # Build comprehensive info dictionary
    info: dict[str, Any] = {
        "name": metadata["name"],
        "description": metadata["description"],
        "version": metadata.get("version", "1.0"),
        "total_blocks": len(workflow_def.blocks),
        "blocks": [
            {
                "id": block["id"],
                "type": block["type"],
                "depends_on": block.get("depends_on", []),
            }
            for block in workflow_def.blocks
        ],
    }

    # Add optional metadata fields
    if "author" in metadata:
        info["author"] = metadata["author"]
    if "tags" in metadata:
        info["tags"] = metadata["tags"]

    # Add input/output schema if available
    if schema:
        # Convert input declarations to simple type mapping
        if schema.inputs:
            info["inputs"] = {
                name: {"type": decl.type.value, "description": decl.description}
                for name, decl in schema.inputs.items()
            }

        # Add output mappings if available
        if schema.outputs:
            info["outputs"] = schema.outputs

    return info


# =============================================================================
# Checkpoint Management Tools
# =============================================================================


@mcp.tool()
async def resume_workflow(
    checkpoint_id: str,
    llm_response: str = "",
) -> dict[str, Any]:
    """Resume a paused or checkpointed workflow.

    Use this to continue a workflow that was paused for interactive input,
    or to restart a workflow from a crash recovery checkpoint.

    Output verbosity is controlled by WORKFLOWS_LOG_LEVEL environment variable:
    - Non-DEBUG (default): Returns empty blocks/metadata (minimal)
    - DEBUG: Returns full blocks/metadata (detailed)

    Args:
        checkpoint_id: Checkpoint token from pause or list_checkpoints
        llm_response: Your response to the pause prompt (required for paused workflows)

    Returns:
        Workflow execution result with consistent structure (same format as execute_workflow):
        {"status": "success", "outputs": {...}, "blocks": {...}, "metadata": {...}}
        - blocks/metadata are empty dicts when WORKFLOWS_LOG_LEVEL != DEBUG
        - blocks/metadata are fully populated when WORKFLOWS_LOG_LEVEL = DEBUG

    Example:
        # Resume paused workflow with confirmation
        resume_workflow(
            checkpoint_id="pause_abc123",
            llm_response="yes"
        )
    """
    # Resume workflow - executor returns WorkflowResponse directly
    response = await executor.resume_workflow(checkpoint_id, llm_response)
    return response.model_dump()


@mcp.tool()
async def list_checkpoints(workflow_name: str = "") -> dict[str, Any]:
    """List available workflow checkpoints.

    Shows all checkpoints, including both automatic checkpoints (for crash recovery)
    and pause checkpoints (for interactive workflows).

    Args:
        workflow_name: Filter by workflow name (empty = all workflows)

    Returns:
        List of checkpoint metadata with creation time, pause status, etc.

    Example:
        list_checkpoints(workflow_name="python-ci-pipeline")
    """
    filter_name = workflow_name if workflow_name else None
    checkpoints = await executor.checkpoint_store.list_checkpoints(filter_name)

    return {
        "checkpoints": [
            {
                "checkpoint_id": c.checkpoint_id,
                "workflow": c.workflow_name,
                "created_at": c.created_at,
                "created_at_iso": datetime.fromtimestamp(c.created_at).isoformat(),
                "is_paused": c.paused_block_id is not None,
                "pause_prompt": c.pause_prompt,
                "type": "pause" if c.paused_block_id is not None else "automatic",
            }
            for c in checkpoints
        ],
        "total": len(checkpoints),
    }


@mcp.tool()
async def get_checkpoint_info(checkpoint_id: str) -> dict[str, Any]:
    """Get detailed information about a specific checkpoint.

    Useful for inspecting checkpoint state before resuming.

    Args:
        checkpoint_id: Checkpoint token

    Returns:
        Detailed checkpoint information
    """
    state = await executor.checkpoint_store.load_checkpoint(checkpoint_id)
    if state is None:
        return {"found": False, "error": f"Checkpoint {checkpoint_id} not found or expired"}

    # Calculate progress percentage
    total_blocks = sum(len(wave) for wave in state.execution_waves)
    if total_blocks > 0:
        progress_percentage = len(state.completed_blocks) / total_blocks * 100
    else:
        progress_percentage = 0

    return {
        "found": True,
        "checkpoint_id": state.checkpoint_id,
        "workflow_name": state.workflow_name,
        "created_at": state.created_at,
        "created_at_iso": datetime.fromtimestamp(state.created_at).isoformat(),
        "is_paused": state.paused_block_id is not None,
        "paused_block_id": state.paused_block_id,
        "pause_prompt": state.pause_prompt,
        "completed_blocks": state.completed_blocks,
        "current_wave": state.current_wave_index,
        "total_waves": len(state.execution_waves),
        "progress_percentage": round(progress_percentage, 1),
    }


@mcp.tool()
async def delete_checkpoint(checkpoint_id: str) -> dict[str, Any]:
    """Delete a checkpoint.

    Useful for cleaning up paused workflows that are no longer needed.

    Args:
        checkpoint_id: Checkpoint token to delete

    Returns:
        Deletion status
    """
    deleted = await executor.checkpoint_store.delete_checkpoint(checkpoint_id)

    return {
        "deleted": deleted,
        "checkpoint_id": checkpoint_id,
        "message": "Checkpoint deleted successfully" if deleted else "Checkpoint not found",
    }


# =============================================================================
# Server Entry Point
# =============================================================================


def main() -> None:
    """Entry point for running the MCP server.

    This function is called when the server is run directly via:
    - uv run python -m workflows_mcp
    - python -m workflows_mcp
    - uv run workflows-mcp (if entry point is configured in pyproject.toml)

    Defaults to stdio transport for MCP protocol communication.
    """
    # Get log level from environment variable, default to INFO
    log_level_str = os.getenv("WORKFLOWS_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Configure logging to stderr (MCP requirement)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Load workflows at startup
    load_workflows()

    # Run the MCP server
    mcp.run()  # Defaults to stdio transport


__all__ = [
    "mcp",
    "main",
    "execute_workflow",
    "execute_inline_workflow",
    "list_workflows",
    "get_workflow_info",
    "resume_workflow",
    "list_checkpoints",
    "get_checkpoint_info",
    "delete_checkpoint",
    "executor",
    "workflow_registry",
]
