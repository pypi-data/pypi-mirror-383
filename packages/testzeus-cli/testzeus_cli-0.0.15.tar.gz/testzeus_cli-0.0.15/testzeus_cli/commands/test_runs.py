"""
Commands for managing test runs in TestZeus CLI.
"""

import asyncio
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress
from datetime import datetime

from testzeus_sdk import TestZeusClient
from testzeus_cli.config import get_client_config
from testzeus_cli.utils.formatters import format_output, print_message
from testzeus_cli.utils.validators import validate_id, parse_key_value_pairs
from testzeus_cli.utils.auth import initialize_client_with_token

console = Console()


@click.group(name="test-runs")
def test_runs_group():
    """Manage TestZeus test runs"""
    pass


@test_runs_group.command(name="list")
@click.option(
    "--filters", "-f", multiple=True, help="Filter results (format: key=value)"
)
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities")
@click.pass_context
def list_test_runs(ctx, filters, sort, expand):
    """List test runs with optional filters and sorting"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        # Parse filters
        filter_dict = parse_key_value_pairs(filters) if filters else {}

        async with client:
            # Apply token from config if available
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            test_runs = await client.test_runs.get_list(
                expand=expand, sort=sort, filters=filter_dict
            )
            return test_runs

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_runs_group.command(name="get")
@click.argument("test_run_id")
@click.option("--expand", help="Expand related entities")
@click.pass_context
def get_test_run(ctx, test_run_id, expand):
    """Get a single test run by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_id_validated = validate_id(test_run_id, "test run")

        async with client:
            # Apply token from config if available
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            test_run = await client.test_runs.get_one(
                test_run_id_validated, expand=expand
            )
            return test_run.data

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_runs_group.command(name="get-expanded")
@click.argument("test_run_id")
@click.pass_context
def get_expanded_test_run(ctx, test_run_id):
    """Get expanded details for a test run including all outputs and steps"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_id_validated = validate_id(test_run_id, "test run")

        async with client:
            # Apply token from config if available
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            expanded_test_run = await client.test_runs.get_expanded(
                test_run_id_validated
            )
            return expanded_test_run

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_runs_group.command(name="watch")
@click.argument("test_run_id")
@click.option("--interval", default=5, help="Check interval in seconds")
@click.pass_context
def watch_test_run(ctx, test_run_id, interval):
    """Watch a test run until completion"""

    async def _monitor_test_run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_id_validated = validate_id(test_run_id, "test run")

        with Progress() as progress:
            task = progress.add_task("[cyan]Running test...", total=None)

            async with client:
                # Apply token from config if available
                if token:
                    initialize_client_with_token(client, token)
                else:
                    await client.ensure_authenticated()

                while True:
                    # get_one doesn't support modified_by parameter
                    test_run = await client.test_runs.get_one(test_run_id_validated)
                    # Update progress description with status
                    progress.update(
                        task, description=f"[cyan]Test status: {test_run.status}[/cyan]"
                    )

                    if test_run.is_completed():
                        progress.update(task, completed=100, total=100)
                        print_message("[green]Test run completed successfully![/green]", ctx.obj["FORMAT"])
                        return test_run.data
                    elif test_run.is_failed():
                        progress.update(task, completed=100, total=100)
                        print_message("[red]Test run failed![/red]", ctx.obj["FORMAT"])
                        return test_run.data
                    elif test_run.is_crashed():
                        progress.update(task, completed=100, total=100)
                        print_message("[red]Test run crashed![/red]", ctx.obj["FORMAT"])
                        return test_run.data
                    elif test_run.is_cancelled():
                        progress.update(task, completed=100, total=100)
                        print_message("[yellow]Test run was cancelled![/yellow]", ctx.obj["FORMAT"])
                        return test_run.data

                    # Sleep for the specified interval
                    await asyncio.sleep(interval)

    try:
        result = asyncio.run(_monitor_test_run())
        duration = (
            datetime.fromisoformat(result["end_time"].replace("Z", "+00:00"))
            - datetime.fromisoformat(result["start_time"].replace("Z", "+00:00"))
            if "end_time" in result and "start_time" in result
            else None
        )
        print_message(f"Test run duration: {duration.total_seconds()} seconds", ctx.obj["FORMAT"])
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        print_message(f"[red]Error watching test run:[/red] {str(e)}", ctx.obj["FORMAT"])
        exit(1)


@test_runs_group.command(name="download-attachments")
@click.argument("test_run_id")
@click.option(
    "--output-dir", default="./attachments", help="Directory to save attachments"
)
@click.pass_context
def download_attachments(ctx, test_run_id, output_dir):
    """Download all attachments for a test run"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_id_validated = validate_id(test_run_id, "test run")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        async with client:
            # Apply token from config if available
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            # Download all attachments for the test run using positional parameters
            result = await client.test_runs.download_all_attachments(
                test_run_id_validated, str(output_path)
            )
            return result

    try:
        result = asyncio.run(_run())

        if not result:
            print_message(
                "[yellow]No attachments found or downloaded for this test run[/yellow]", ctx.obj["FORMAT"]
            )
            return

        print_message(
            f"[green]Downloaded {len(result)} attachments to {output_dir}[/green]", ctx.obj["FORMAT"]
        )
        for attachment in result:
            print_message(f"- {attachment}", ctx.obj["FORMAT"])
    except Exception as e:
        if ctx.obj.get("VERBOSE"):
            print_message("[red]Failed to download attachments:[/red]", ctx.obj["FORMAT"])
            import traceback

            print_message(traceback.format_exc(), ctx.obj["FORMAT"])
        else:
            print_message(f"[red]Failed to download attachments:[/red] {str(e)}", ctx.obj["FORMAT"])
        exit(1)


@test_runs_group.command(name="status")
@click.argument("test_run_id")
@click.pass_context
def get_test_run_status(ctx, test_run_id):
    """Get the status of a test run"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_id_validated = validate_id(test_run_id, "test run")

        async with client:
            # Apply token from config if available
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            test_run = await client.test_runs.get_one(test_run_id_validated)
            return {
                "id": test_run.data["id"],
                "name": test_run.data["name"],
                "status": test_run.data["status"],
                "result": test_run.data.get("test_status"),
                "starttime": test_run.data["start_time"],
                "endtime": test_run.data["end_time"],
            }

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])