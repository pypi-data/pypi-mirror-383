#!/usr/bin/env python3
"""
Test execution CLI commands: run
"""

import sys

import click

from ..config.config_manager import ConfigManager
from ..shared.console_shared import get_console
from .completion import complete_server_ids, complete_suite_ids
from .post_command_hooks import trigger_post_command_hooks
from .suggestions import enhanced_error_handler
from .test_execution import (
    run_test_suite,
)


def validate_server_id_enhanced(ctx, param, value):
    """Enhanced server ID validation with suggestions"""
    return enhanced_error_handler(ctx, param, value, "server")


def validate_suite_id_enhanced(ctx, param, value):
    """Enhanced suite ID validation with suggestions"""
    return enhanced_error_handler(ctx, param, value, "suite")


def create_run_command():
    """Create the run command"""

    @click.command(name="run")
    @click.argument(
        "suite_id",
        callback=validate_suite_id_enhanced,
        shell_complete=complete_suite_ids,
    )
    @click.argument(
        "server_id",
        callback=validate_server_id_enhanced,
        shell_complete=complete_server_ids,
    )
    @click.option("--verbose", "-v", is_flag=True, help="Detailed output")
    @click.option(
        "--global",
        "use_global_dir",
        is_flag=True,
        help="Save results to global directory (~/.local/share/mcp-t) instead of local ./test_results/",
    )
    @click.pass_context
    def mcpt_run_complete(
        ctx, suite_id: str, server_id: str, verbose: bool, use_global_dir: bool
    ):
        """Run test suite against MCP server with enhanced validation and suggestions

        Examples (with tab completion):
          mcp-t run basic-tests dev-server
          mcp-t run compliance-suite prod-server -v

        Tip: Use 'mcp-t help run' for detailed examples and troubleshooting
        """
        # Enhanced implementation with better error handling
        config_manager = ConfigManager()
        console = get_console()

        try:
            # Load configs using type-safe methods
            suite = config_manager.load_test_suite(suite_id)
            server_config = config_manager.get_server_by_id(server_id)

            console.print_info(f"Running {suite.name} against {server_config.name}")

            # Use type-safe execution dispatcher with better error handling
            from .utils import safe_run_async

            results = safe_run_async(
                run_test_suite(
                    suite, server_config.model_dump(), verbose, use_global_dir
                ),
                error_context="test suite execution",
                server_url=server_config.url if hasattr(server_config, "url") else None,
                verbose=verbose,
            )

            # Extract actual success status from results dict
            if isinstance(results, dict):
                success = results.get("overall_success", False)
                successful_tests = results.get("successful_tests", 0)
                total_tests = results.get("total_tests", 0)
            else:
                # Fallback for boolean return (shouldn't happen but safety check)
                success = bool(results)
                successful_tests = 0
                total_tests = 0

            if success:
                console.print_success("All tests completed successfully!")
                # Add post-command hook before exit
                trigger_post_command_hooks(ctx)
                sys.exit(0)
            else:
                # Show detailed failure information
                console.print_error(
                    f"Test run failed: {successful_tests}/{total_tests} tests passed"
                )

                if isinstance(results, dict) and "test_results" in results:
                    console.print("\n[bold red]Failed Tests:[/bold red]")
                    failed_count = 0
                    for result in results["test_results"]:
                        if not result.get("success", True):  # Show failed tests
                            failed_count += 1
                            test_id = result.get("test_id", "unknown")
                            error_msg = result.get(
                                "error", result.get("message", "Unknown error")
                            )

                            # Clean up and shorten error messages
                            if len(error_msg) > 100:
                                error_msg = error_msg[:100] + "..."

                            console.print(f"  ❌ [red]{test_id}[/red]: {error_msg}")

                    if failed_count == 0:
                        console.print(
                            "  [yellow]No specific test failures found - check test execution logs[/yellow]"
                        )

                console.print(
                    "\n[dim]Use --verbose flag for more detailed output[/dim]"
                )
                trigger_post_command_hooks(ctx)
                sys.exit(1)

        except Exception as e:
            console.print_error(
                f"Unexpected error: {e!s}", ["Use 'mcp-t COMMAND --help' for help"]
            )
            trigger_post_command_hooks(ctx)  # Ensure hooks run even on error
            sys.exit(1)

    return mcpt_run_complete
