"""
Commands for managing test report schedules in TestZeus CLI.
"""

import asyncio
import json
import click
from rich.console import Console
from datetime import datetime
from testzeus_sdk import TestZeusClient
from testzeus_cli.config import get_client_config
from testzeus_cli.utils.formatters import format_output, print_message
from testzeus_cli.utils.validators import validate_id, parse_key_value_pairs
from testzeus_cli.utils.auth import initialize_client_with_token

console = Console()


@click.group(name="schedule")
def test_report_schedules_group():
    """Manage TestZeus test report schedules"""
    pass


@test_report_schedules_group.command(name="list")
@click.option(
    "--filters", "-f", multiple=True, help="Filter results (format: key=value)"
)
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=50, help="Items per page")
@click.pass_context
def list_schedules(ctx, filters, sort, expand, page, per_page):
    """List test report schedules with optional filters and sorting"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        filter_dict = parse_key_value_pairs(filters) if filters else {}

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            schedules = await client.test_report_schedules.get_list(
                expand=expand, sort=sort, filters=filter_dict, page=page, per_page=per_page
            )
            return schedules

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_report_schedules_group.command(name="get")
@click.argument("schedule_id")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.pass_context
def get_schedule(ctx, schedule_id, expand):
    """Get a single test report schedule by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        schedule_id_validated = validate_id(schedule_id, "test report schedule")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            schedule = await client.test_report_schedules.get_one(
                schedule_id_validated, expand=expand
            )
            return schedule.data

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@test_report_schedules_group.command(name="create")
@click.option("--name", required=True, help="Schedule name")
@click.option("--is-active", type=bool, help="Set schedule as active (true/false)")
@click.option("--cron-expression", help="Cron expression for scheduling")
@click.option("--filter-name-pattern", help="Filter by test name pattern")
@click.option("--filter-tag-pattern", help="Filter by tag pattern")
@click.option("--filter-env-pattern", help="Filter by environment pattern")
@click.option("--filter-test-data-pattern", help="Filter by test data pattern")
@click.option("--filter-tags", help="Filter by specific tag IDs (comma-separated)")
@click.option("--filter-env", help="Filter by specific environment IDs (comma-separated)")
@click.option("--filter-test-data", help="Filter by specific test data IDs (comma-separated)")
@click.option("--filter-time-intervals", help="Time intervals in format 'start_time,end_time' (e.g., '2025-01-01 00:00:00,2025-01-01 01:00:00')")
@click.option("--notification-channels", help="Notification channel IDs (comma-separated)")
@click.pass_context
def create_schedule(
    ctx,
    name,
    is_active,
    cron_expression,
    filter_name_pattern,
    filter_tag_pattern,
    filter_env_pattern,
    filter_test_data_pattern,
    filter_tags,
    filter_env,
    filter_test_data,
    filter_time_intervals,
    notification_channels,
):
    """Create a new test report schedule"""

    # Validation: either filter_time_intervals or cron_expression
    if filter_time_intervals and cron_expression:
        raise click.UsageError("Cannot use both --filter-time-intervals and --cron-expression")

    # Validation: either filter_tags or filter_tag_pattern
    if filter_tags and filter_tag_pattern:
        raise click.UsageError("Cannot use both --filter-tags and --filter-tag-pattern")

    # Validation: either filter_env or filter_env_pattern
    if filter_env and filter_env_pattern:
        raise click.UsageError("Cannot use both --filter-env and --filter-env-pattern")

    # Validation: either filter_test_data or filter_test_data_pattern
    if filter_test_data and filter_test_data_pattern:
        raise click.UsageError("Cannot use both --filter-test-data and --filter-test-data-pattern")

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        schedule_data = {
            "name": f"{name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "display_name": name,
            "tenant": stored_tenant_id,
            "created_by": stored_user_id,
            "modified_by": stored_user_id,
        }

        if is_active is not None:
            schedule_data["is_active"] = is_active

        if cron_expression:
            schedule_data["cron_expression"] = cron_expression

        if filter_name_pattern:
            schedule_data["filter_name_pattern"] = filter_name_pattern

        if filter_tag_pattern:
            schedule_data["filter_tag_pattern"] = filter_tag_pattern

        if filter_env_pattern:
            schedule_data["filter_env_pattern"] = filter_env_pattern

        if filter_test_data_pattern:
            schedule_data["filter_test_data_pattern"] = filter_test_data_pattern

        # Parse comma-separated strings into lists
        if filter_tags:
            schedule_data["filter_tags"] = [tag.strip() for tag in filter_tags.split(",") if tag.strip()]

        if filter_env:
            schedule_data["filter_env"] = [env.strip() for env in filter_env.split(",") if env.strip()]

        if filter_test_data:
            schedule_data["filter_test_data"] = [data.strip() for data in filter_test_data.split(",") if data.strip()]

        # Parse time intervals into structured format
        if filter_time_intervals:
            try:
                parts = filter_time_intervals.split(",")
                if len(parts) != 2:
                    raise ValueError("Time intervals must be in format 'start_time,end_time'")
                
                start_time = parts[0].strip()
                end_time = parts[1].strip()
                
                schedule_data["filter_time_intervals"] = {
                    "start_time": start_time,
                    "end_time": end_time
                }
            except Exception as e:
                raise click.BadParameter(f"Invalid format for filter_time_intervals: {str(e)}. Expected format: 'start_time,end_time'")

        if notification_channels:
            schedule_data["notification_channels"] = [ch.strip() for ch in notification_channels.split(",") if ch.strip()]

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Creating test report schedule with parameters: {schedule_data}[/blue]"
                )

            new_schedule = await client.test_report_schedules.create(schedule_data)
            return new_schedule.data

    result = asyncio.run(_run())
    print_message(
        f"[green]Test report schedule created successfully with ID: {result['id']}[/green]",
        ctx.obj["FORMAT"],
    )
    format_output(result, ctx.obj["FORMAT"])


@test_report_schedules_group.command(name="update")
@click.argument("schedule_id")
@click.option("--name", help="New schedule name")
@click.option("--is-active", type=bool, help="Set schedule as active (true/false)")
@click.option("--cron-expression", help="Cron expression for scheduling")
@click.option("--filter-name-pattern", help="Filter by test name pattern")
@click.option("--filter-tag-pattern", help="Filter by tag pattern")
@click.option("--filter-env-pattern", help="Filter by environment pattern")
@click.option("--filter-test-data-pattern", help="Filter by test data pattern")
@click.option("--filter-tags", help="Filter by specific tag IDs (comma-separated)")
@click.option("--filter-env", help="Filter by specific environment IDs (comma-separated)")
@click.option("--filter-test-data", help="Filter by specific test data IDs (comma-separated)")
@click.option("--filter-time-intervals", help="Time intervals in format 'start_time,end_time' (e.g., '2025-01-01 00:00:00,2025-01-01 01:00:00')")
@click.option("--notification-channels", help="Notification channel IDs (comma-separated)")
@click.pass_context
def update_schedule(
    ctx,
    schedule_id,
    name,
    is_active,
    cron_expression,
    filter_name_pattern,
    filter_tag_pattern,
    filter_env_pattern,
    filter_test_data_pattern,
    filter_tags,
    filter_env,
    filter_test_data,
    filter_time_intervals,
    notification_channels,
):
    """Update an existing test report schedule"""

    # Validation: either filter_time_intervals or cron_expression
    if filter_time_intervals and cron_expression:
        raise click.UsageError("Cannot use both --filter-time-intervals and --cron-expression")

    # Validation: either filter_tags or filter_tag_pattern
    if filter_tags and filter_tag_pattern:
        raise click.UsageError("Cannot use both --filter-tags and --filter-tag-pattern")

    # Validation: either filter_env or filter_env_pattern
    if filter_env and filter_env_pattern:
        raise click.UsageError("Cannot use both --filter-env and --filter-env-pattern")

    # Validation: either filter_test_data or filter_test_data_pattern
    if filter_test_data and filter_test_data_pattern:
        raise click.UsageError("Cannot use both --filter-test-data and --filter-test-data-pattern")

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        schedule_id_validated = validate_id(schedule_id, "test report schedule")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            update_data = {
                "tenant": stored_tenant_id,
                "modified_by": stored_user_id,
            }

            has_updates = False

            if name:
                update_data["display_name"] = name
                has_updates = True

            if is_active is not None:
                update_data["is_active"] = is_active
                has_updates = True

            if cron_expression:
                update_data["cron_expression"] = cron_expression
                has_updates = True

            if filter_name_pattern:
                update_data["filter_name_pattern"] = filter_name_pattern
                has_updates = True

            if filter_tag_pattern:
                update_data["filter_tag_pattern"] = filter_tag_pattern
                has_updates = True

            if filter_env_pattern:
                update_data["filter_env_pattern"] = filter_env_pattern
                has_updates = True

            if filter_test_data_pattern:
                update_data["filter_test_data_pattern"] = filter_test_data_pattern
                has_updates = True

            if filter_tags:
                update_data["filter_tags"] = [tag.strip() for tag in filter_tags.split(",") if tag.strip()]
                has_updates = True

            if filter_env:
                update_data["filter_env"] = [env.strip() for env in filter_env.split(",") if env.strip()]
                has_updates = True

            if filter_test_data:
                update_data["filter_test_data"] = [data.strip() for data in filter_test_data.split(",") if data.strip()]
                has_updates = True

            if filter_time_intervals:
                try:
                    parts = filter_time_intervals.split(",")
                    if len(parts) != 2:
                        raise ValueError("Time intervals must be in format 'start_time,end_time'")
                    
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
                    
                    update_data["filter_time_intervals"] = {
                        "start_time": start_time,
                        "end_time": end_time
                    }
                    has_updates = True
                except Exception as e:
                    raise click.BadParameter(f"Invalid format for filter_time_intervals: {str(e)}. Expected format: 'start_time,end_time'")

            if notification_channels:
                update_data["notification_channels"] = [ch.strip() for ch in notification_channels.split(",") if ch.strip()]
                has_updates = True

            if not has_updates:
                print_message("[yellow]No updates provided[/yellow]", ctx.obj["FORMAT"])
                return None

            if ctx.obj.get("VERBOSE"):
                console.print(f"[blue]Updating test report schedule with: {update_data}[/blue]")

            updated_schedule = await client.test_report_schedules.update(
                schedule_id_validated, update_data
            )
            return updated_schedule.data

    try:
        result = asyncio.run(_run())
        if result:
            print_message(
                f"[green]Test report schedule updated successfully: {result['name']}[/green]",
                ctx.obj["FORMAT"],
            )
            format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        if ctx.obj.get("VERBOSE"):
            print_message("[red]Error updating test report schedule:[/red]", ctx.obj["FORMAT"])
            import traceback
            print_message(traceback.format_exc(), ctx.obj["FORMAT"])
        else:
            print_message(
                f"[red]Error updating test report schedule:[/red] {str(e)}",
                ctx.obj["FORMAT"],
            )
        exit(1)


@test_report_schedules_group.command(name="delete")
@click.argument("schedule_id")
@click.confirmation_option(
    prompt="Are you sure you want to delete this test report schedule?"
)
@click.pass_context
def delete_schedule(ctx, schedule_id):
    """Delete a test report schedule"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        schedule_id_validated = validate_id(schedule_id, "test report schedule")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            success = await client.test_report_schedules.delete(schedule_id_validated)
            return {"success": success, "id": schedule_id_validated}

    try:
        result = asyncio.run(_run())
        print_message(
            f"[green]Test report schedule deleted successfully: {result['id']}[/green]",
            ctx.obj["FORMAT"],
        )
    except Exception as e:
        print_message(
            f"[red]Error deleting test report schedule:[/red] {str(e)}",
            ctx.obj["FORMAT"],
        )
        exit(1)

