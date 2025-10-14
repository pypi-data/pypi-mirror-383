"""
Commands for managing test run groups in TestZeus CLI.
"""

import asyncio
import json
from pathlib import Path
import click
from rich.console import Console
from datetime import datetime
from testzeus_sdk import TestZeusClient
from testzeus_cli.config import get_client_config
from testzeus_cli.utils.formatters import format_output, print_message
from testzeus_cli.utils.validators import validate_id, parse_key_value_pairs
from testzeus_cli.utils.auth import initialize_client_with_token

console = Console()


@click.group(name="test-run-group")
def test_run_groups_group():
    """Manage TestZeus test run groups"""
    pass


@test_run_groups_group.command(name="list")
@click.option(
    "--filters", "-f", multiple=True, help="Filter results (format: key=value)"
)
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=50, help="Items per page")
@click.pass_context
def list_test_run_groups(ctx, filters, sort, expand, page, per_page):
    """List test run groups with optional filters and sorting"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        # Parse filters
        filter_dict = parse_key_value_pairs(filters) if filters else {}

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            test_run_groups = await client.test_run_groups.get_list(
                expand=expand, sort=sort, filters=filter_dict, page=page, per_page=per_page
            )
            return test_run_groups

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_run_groups_group.command(name="get")
@click.argument("test_run_group_id")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.pass_context
def get_test_run_group(ctx, test_run_group_id, expand):
    """Get a single test run group by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_group_id_validated = validate_id(test_run_group_id, "test run group")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            test_run_group = await client.test_run_groups.get_one(
                test_run_group_id_validated, expand=expand
            )
            return test_run_group.data

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_run_groups_group.command(name="execute")
@click.option("--name", required=True, help="Test run group name (unique identifier)")
@click.option(
    "--execution-mode",
    type=click.Choice(["lenient", "strict"]),
    default="lenient",
    help="Execution mode (default: lenient)",
)
@click.option("--tags", help="Tag IDs to associate with the group (comma-separated)")
@click.option("--test-ids", help="Test IDs to include in the group (comma-separated)")
@click.option("--environment", help="Environment ID")
@click.option("--notification-channels", help="Notification channel IDs (comma-separated)")
@click.pass_context
def execute_test_run_group(
    ctx,
    name,
    execution_mode,
    tags,
    test_ids,
    environment,
    notification_channels,
):
    """Execute a new test run group"""

    # Validation: either tags or test_ids, not both
    if tags and test_ids:
        raise click.UsageError("Cannot use both --tags and --test-ids. Use only one.")
    
    if not tags and not test_ids:
        raise click.UsageError("Either --tags or --test-ids is required.")

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        # Parse comma-separated test_ids or tags into list
        if test_ids:
            test_ids_list = [test_id.strip() for test_id in test_ids.split(",") if test_id.strip()]
            if not test_ids_list:
                raise click.BadParameter("At least one test ID is required")
        
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if not tags_list:
                raise click.BadParameter("At least one tag is required")

        # Prepare parameters
        test_run_group_data = {
            "name": f"{name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "display_name": name,
            "execution_mode": execution_mode,
            "tenant": stored_tenant_id,
            "created_by": stored_user_id,
            "modified_by": stored_user_id,
        }

        # Add either test_ids or tags to the data
        if test_ids:
            test_run_group_data["test_ids"] = test_ids_list
        
        if tags:
            test_run_group_data["tags"] = tags_list

        if environment:
            test_run_group_data["environment"] = environment

        # Parse comma-separated notification channels into list
        if notification_channels:
            test_run_group_data["notification_channels"] = [ch.strip() for ch in notification_channels.split(",") if ch.strip()]

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Creating test run group with parameters: {test_run_group_data}[/blue]"
                )

            new_test_run_group = await client.test_run_groups.create(
                test_run_group_data
            )
            return new_test_run_group.data

    result = asyncio.run(_run())
    print_message(
        f"[green]Test run group created successfully with ID: {result['id']}[/green]",
        ctx.obj["FORMAT"],
    )
    format_output(result, ctx.obj["FORMAT"])


@test_run_groups_group.command(name="delete")
@click.argument("test_run_group_id")
@click.confirmation_option(
    prompt="Are you sure you want to delete this test run group?"
)
@click.pass_context
def delete_test_run_group(ctx, test_run_group_id):
    """Delete a test run group"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_group_id_validated = validate_id(
            test_run_group_id, "test run group"
        )

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            success = await client.test_run_groups.delete(test_run_group_id_validated)
            return {"success": success, "id": test_run_group_id_validated}

    try:
        result = asyncio.run(_run())
        print_message(
            f"[green]Test run group deleted successfully: {result['id']}[/green]",
            ctx.obj["FORMAT"],
        )
    except Exception as e:
        print_message(
            f"[red]Error deleting test run group:[/red] {str(e)}", ctx.obj["FORMAT"]
        )
        exit(1)


@test_run_groups_group.command(name="cancel")
@click.argument("test_run_group_id")
@click.pass_context
def cancel_test_run_group(ctx, test_run_group_id):
    """Cancel a running test run group"""

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_group_id_validated = validate_id(
            test_run_group_id, "test run group"
        )

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Cancelling test run group: {test_run_group_id_validated}[/blue]"
                )

            result = await client.test_run_groups.cancel(
                test_run_group_id_validated,
                tenant=stored_tenant_id,
                modified_by=stored_user_id,
            )
            return result.data if hasattr(result, "data") else result

    try:
        result = asyncio.run(_run())
        print_message(
            f"[green]Test run group cancelled successfully[/green]", ctx.obj["FORMAT"]
        )
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        print_message(
            f"[red]Error cancelling test run group:[/red] {str(e)}", ctx.obj["FORMAT"]
        )
        exit(1)


@test_run_groups_group.command(name="get-status")
@click.argument("test_run_group_id")
@click.pass_context
def get_test_run_group_status(ctx, test_run_group_id):
    """Get the status summary of a test run group"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_group_id_validated = validate_id(
            test_run_group_id, "test run group"
        )

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            test_run_group = await client.test_run_groups.get_one(
                test_run_group_id_validated
            )

            # Extract status information
            data = test_run_group.data
            status_summary = {
                "id": data.get("id"),
                "name": data.get("name"),
                "display_name": data.get("display_name"),
                "status": data.get("status"),
                "ctrf_status": data.get("ctrf_status"),
                "isCtrf_generated": data.get("isCtrf_generated"),
                "test_runs_status": data.get("test_runs_status"),
                "test_runs_ctrf_status": data.get("test_runs_ctrf_status"),
                "created": data.get("created"),
                "updated": data.get("updated"),
            }

            return status_summary

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_run_groups_group.command(name="download-report")
@click.argument("test_run_group_id")
@click.option("--output-dir", default="downloads", help="Output directory for downloaded report (default: downloads)")
@click.option("--format", "report_format", type=click.Choice(["ctrf", "pdf", "csv", "zip"]), default="pdf", help="Report format (default: pdf)")
@click.pass_context
def download_test_run_group_report(ctx, test_run_group_id, output_dir, report_format):
    """Download the report for a test run group"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_group_id_validated = validate_id(
            test_run_group_id, "test run group"
        )

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Downloading {report_format} report for test run group: {test_run_group_id_validated}[/blue]"
                )

            downloaded_file = await client.test_run_groups.download_report(
                test_run_group_id_validated,
                output_dir=output_dir,
                format=report_format
            )
            
            if downloaded_file:
                return {
                    "test_run_group_id": test_run_group_id_validated,
                    "format": report_format,
                    "output_dir": output_dir,
                    "file_path": str(downloaded_file),
                    "success": True
                }
            else:
                return {
                    "test_run_group_id": test_run_group_id_validated,
                    "format": report_format,
                    "output_dir": output_dir,
                    "file_path": None,
                    "success": False
                }

    try:
        result = asyncio.run(_run())
        if result["success"]:
            print_message(
                f"[green]Report downloaded successfully to: {result['file_path']}[/green]",
                ctx.obj["FORMAT"],
            )
        else:
            print_message(
                f"[yellow]Report download failed for test run group: {result['test_run_group_id']}[/yellow]",
                ctx.obj["FORMAT"],
            )
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        if ctx.obj.get("VERBOSE"):
            print_message("[red]Error downloading report:[/red]", ctx.obj["FORMAT"])
            import traceback
            print_message(traceback.format_exc(), ctx.obj["FORMAT"])
        else:
            print_message(
                f"[red]Error downloading report:[/red] {str(e)}",
                ctx.obj["FORMAT"],
            )
        exit(1)


@test_run_groups_group.command(name="download-attachments")
@click.argument("test_run_group_id")
@click.option("--output-dir", default="downloads", help="Base directory to save attachments (default: downloads)")
@click.pass_context
def download_test_run_group_attachments(ctx, test_run_group_id, output_dir):
    """Download all attachments for all test runs in a test run group"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        test_run_group_id_validated = validate_id(
            test_run_group_id, "test run group"
        )

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Downloading attachments for test run group: {test_run_group_id_validated}[/blue]"
                )

            downloaded_attachments = await client.test_run_groups.download_all_attachments(
                test_run_group_id_validated,
                output_dir=output_dir
            )
            
            # Calculate total attachments downloaded
            total_attachments = sum(len(files) for files in downloaded_attachments.values())
            
            return {
                "test_run_group_id": test_run_group_id_validated,
                "output_dir": output_dir,
                "downloaded_attachments": downloaded_attachments,
                "total_test_runs": len(downloaded_attachments),
                "total_attachments": total_attachments,
                "success": True
            }

    try:
        result = asyncio.run(_run())
        if result["total_attachments"] > 0:
            print_message(
                f"[green]Downloaded {result['total_attachments']} attachments from {result['total_test_runs']} test runs to: {result['output_dir']}[/green]",
                ctx.obj["FORMAT"],
            )
        else:
            print_message(
                f"[yellow]No attachments found for test run group: {result['test_run_group_id']}[/yellow]",
                ctx.obj["FORMAT"],
            )
        
        # Show detailed breakdown if verbose
        if ctx.obj.get("VERBOSE") and result["downloaded_attachments"]:
            console.print("\n[blue]Attachment breakdown by test run:[/blue]")
            for test_run_name, files in result["downloaded_attachments"].items():
                console.print(f"  • {test_run_name}: {len(files)} files")
        
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        if ctx.obj.get("VERBOSE"):
            print_message("[red]Error downloading attachments:[/red]", ctx.obj["FORMAT"])
            import traceback
            print_message(traceback.format_exc(), ctx.obj["FORMAT"])
        else:
            print_message(
                f"[red]Error downloading attachments:[/red] {str(e)}",
                ctx.obj["FORMAT"],
            )
        exit(1)


@test_run_groups_group.command(name="execute-and-monitor")
@click.option("--name", required=True, help="Test run group name (unique identifier)")
@click.option(
    "--execution-mode",
    type=click.Choice(["lenient", "strict"]),
    default="lenient",
    help="Execution mode (default: lenient)",
)
@click.option("--tags", help="Tag IDs to associate with the group (comma-separated)")
@click.option("--test-ids", help="Test IDs to include in the group (comma-separated)")
@click.option("--environment", help="Environment ID")
@click.option("--notification-channels", help="Notification channel IDs (comma-separated)")
@click.option("--interval", type=int, default=30, help="Sleep interval between status checks in seconds (default: 30)")
@click.option("--output-dir", default="downloads", help="Output directory for downloaded report (default: downloads)")
@click.option("--format", type=click.Choice(["pdf", "csv", "zip", "ctrf"]), default="ctrf", help="Report format (default: ctrf)")
@click.option("--filename", default="ctrf-report.json", help="Filename for the report (default: ctrf-report.json)")
@click.pass_context
def execute_and_monitor_test_run_group(
    ctx,
    name,
    execution_mode,
    tags,
    test_ids,
    environment,
    notification_channels,
    interval,
    output_dir,
    format,
    filename,
):
    """Execute a test run group and monitor until completion, then download the report"""
    
    # Validation: Cannot use both tags and test_ids
    if tags and test_ids:
        raise click.UsageError("Cannot use both --tags and --test-ids. Use only one.")
    if not tags and not test_ids:
        raise click.UsageError("Either --tags or --test-ids is required.")

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            # Parse comma-separated inputs
            test_ids_list = None
            tags_list = None
            notification_channels_list = None

            if test_ids:
                test_ids_list = [test_id.strip() for test_id in test_ids.split(",") if test_id.strip()]
                if not test_ids_list:
                    raise click.BadParameter("At least one test ID is required")

            if tags:
                tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                if not tags_list:
                    raise click.BadParameter("At least one tag is required")

            if notification_channels:
                notification_channels_list = [
                    channel.strip() for channel in notification_channels.split(",") if channel.strip()
                ]

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Executing and monitoring test run group: {name}[/blue]"
                )
                console.print(
                    f"[blue]Sleep interval: {interval}s, Output directory: {output_dir}[/blue]"
                )

            # Execute and monitor the test run group
            test_run_group, report_path = await client.test_run_groups.execute_and_monitor(
                name=name,
                test_ids=test_ids_list,
                execution_mode=execution_mode,
                environment=environment,
                tags=tags_list,
                notification_channels=notification_channels_list,
                tenant=stored_tenant_id,
                created_by=stored_user_id,
                sleep_interval=interval,
                output_dir=output_dir,
                format=format,
                filename=filename,
            )

            return {
                "test_run_group": test_run_group.data,
                "report_path": str(report_path) if report_path else None,
                "success": True,
            }

    try:
        result = asyncio.run(_run())
        if result["success"]:
            print_message(
                f"[green]Test run group executed and completed successfully![/green]",
                ctx.obj["FORMAT"],
            )
            print_message(
                f"[green]Test run group ID: {result['test_run_group']['id']}[/green]",
                ctx.obj["FORMAT"],
            )
            if result["report_path"]:
                print_message(
                    f"[green]Report downloaded to: {result['report_path']}[/green]",
                    ctx.obj["FORMAT"],
                )
        else:
            print_message(
                f"[yellow]Test run group execution completed but report download failed[/yellow]",
                ctx.obj["FORMAT"],
            )
        
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        if ctx.obj.get("VERBOSE"):
            print_message("[red]Error executing and monitoring test run group:[/red]", ctx.obj["FORMAT"])
            import traceback
            print_message(traceback.format_exc(), ctx.obj["FORMAT"])
        else:
            print_message(
                f"[red]Error executing and monitoring test run group:[/red] {str(e)}",
                ctx.obj["FORMAT"],
            )
        exit(1)

