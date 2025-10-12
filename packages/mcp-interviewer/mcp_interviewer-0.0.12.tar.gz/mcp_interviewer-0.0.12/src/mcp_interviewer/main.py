import asyncio
import logging
from pathlib import Path

from .constraints import get_selected_constraints
from .constraints.base import Severity
from .interviewer import MCPInterviewer
from .models import Client, ServerParameters
from .reports import FullReport
from .reports.base import BaseReportOptions
from .reports.custom import CustomReport

logger = logging.getLogger(__name__)


async def amain(
    client: Client | None,
    model: str | None,
    params: ServerParameters,
    out_dir=Path("."),
    should_judge_tool: bool = False,
    should_judge_functional_test: bool = False,
    should_run_functional_test: bool = False,
    custom_reports: list[str] | None = None,
    no_collapse: bool = False,
    selected_constraints: list[str] | None = None,
    fail_on_warnings: bool = False,
) -> int:
    """Asynchronous main function to evaluate an MCP server and generate reports.

    Performs a complete server evaluation and saves the results in multiple formats:
    - Full markdown report (mcp-interview.md) or custom report based on options
    - Raw JSON data (mcp-interview.json)

    Args:
        client: OpenAI client for LLM-based evaluation
        model: Model name to use for evaluation (e.g., "gpt-4")
        params: ServerParameters for the MCP server to evaluate
        out_dir: Directory to save output files (default: current directory)
        should_judge_tool: Whether to perform expensive experimental LLM judging of tools (default: False)
        should_judge_functional_test: Whether to perform expensive experimental LLM judging of functional tests (default: False)
        should_run_functional_test: Whether to run functional tests (default: False)
        custom_reports: List of specific report names to include
        no_collapse: If True, don't use collapsible sections in the report (default: False)
        selected_constraints: List of constraint names or codes to check (all if None)
        fail_on_warnings: Return a non-zero exit code if any constraint violations with WARNING severity are encountered. (default: False)
    """
    exit_code = 0

    # Only create interviewer with client/model if LLM features are needed
    if should_run_functional_test or should_judge_tool or should_judge_functional_test:
        if client is None or model is None:
            raise ValueError("Client and model are required for LLM-based features")
        interviewer = MCPInterviewer(
            client,
            model,
            should_run_functional_test,
            should_judge_tool,
            should_judge_functional_test,
        )
    else:
        # Create a minimal interviewer that only does server inspection
        interviewer = MCPInterviewer(
            None,  # Will need to modify MCPInterviewer to handle this
            None,  # Will need to modify MCPInterviewer to handle this
            False,
            False,
            False,
        )
    interview = await interviewer.interview_server(params)

    # Get constraint violations based on selected constraints
    logger.info("=" * 60)
    logger.info("PHASE 4: Constraint Checking")
    logger.info("=" * 60)
    violations = []
    constraint_classes = get_selected_constraints(selected_constraints)
    for constraint_class in constraint_classes:
        constraint = constraint_class()
        violations.extend(list(constraint.test(interview)))

    if violations:
        for violation in violations:
            if violation.severity == Severity.WARNING:
                exit_code = 1 if fail_on_warnings else exit_code
                logger.warning(
                    f"{type(violation.constraint).__name__}: {violation.message}"
                )
            elif violation.severity == Severity.CRITICAL:
                exit_code = 1
                logger.critical(
                    f"{type(violation.constraint).__name__}: {violation.message}"
                )
    else:
        logger.info("All constraints passed successfully")

    # Create report options
    options = BaseReportOptions(
        use_collapsible=not no_collapse,
        score_tools=should_judge_tool,
        score_functional_test=should_judge_functional_test,
    )

    # Generate the appropriate report based on options
    if custom_reports:
        # Custom report with selected components
        path = out_dir / Path("mcp-interview.md")
        logger.info(
            f"Saving custom interview with reports: {', '.join(custom_reports)} to {path}"
        )
        with open(path, "w") as fd:
            report = CustomReport(
                interview, custom_reports, violations, options, selected_constraints
            )
            fd.write(report.build())
    else:
        # Full report (default)
        path = out_dir / Path("mcp-interview.md")
        logger.info(f"Saving full interview to {path}")
        with open(path, "w") as fd:
            report = FullReport(interview, violations, options, selected_constraints)
            fd.write(report.build())

    path = out_dir / Path("mcp-interview.json")
    logger.info(f"Saving interview json data to {path}")
    with open(path, "w") as fd:
        fd.write(interview.model_dump_json(indent=2))

    return exit_code


def main(
    client: Client | None,
    model: str | None,
    params: ServerParameters,
    out_dir=Path("."),
    should_judge_tool: bool = False,
    should_judge_functional_test: bool = False,
    should_run_functional_test: bool = False,
    custom_reports: list[str] | None = None,
    no_collapse: bool = False,
    selected_constraints: list[str] | None = None,
    fail_on_warnings: bool = False,
) -> int:
    """Synchronous wrapper for the main evaluation function.

    Args:
        client: OpenAI client for LLM-based evaluation
        model: Model name to use for evaluation (e.g., "gpt-4")
        params: ServerParameters for the MCP server to evaluate
        out_dir: Directory to save output files (default: current directory)
        should_judge_tool: Whether to perform expensive experimental LLM judging of tools (default: False)
        should_judge_functional_test: Whether to perform expensive experimental LLM judging of functional tests (default: False)
        should_run_functional_test: Whether to run functional tests (default: False)
        custom_reports: List of specific report names to include
        no_collapse: If True, don't use collapsible sections in the report (default: False)
        selected_constraints: List of constraint names or codes to check (all if None)
    """
    return asyncio.run(
        amain(
            client,
            model,
            params,
            out_dir,
            should_judge_tool,
            should_judge_functional_test,
            should_run_functional_test,
            custom_reports,
            no_collapse,
            selected_constraints,
        )
    )
