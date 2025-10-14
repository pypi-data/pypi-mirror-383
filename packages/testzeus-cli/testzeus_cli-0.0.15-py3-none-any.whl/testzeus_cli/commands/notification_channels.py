"""
Commands for managing notification channels in TestZeus CLI.
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


@click.group(name="notification")
def notification_channels_group():
    """Manage TestZeus notification channels"""
    pass


@notification_channels_group.command(name="list")
@click.option(
    "--filters", "-f", multiple=True, help="Filter results (format: key=value)"
)
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=50, help="Items per page")
@click.pass_context
def list_channels(ctx, filters, sort, expand, page, per_page):
    """List notification channels with optional filters and sorting"""

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

            channels = await client.notification_channels.get_list(
                expand=expand, sort=sort, filters=filter_dict, page=page, per_page=per_page
            )
            return channels

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@notification_channels_group.command(name="get")
@click.argument("channel_id")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.pass_context
def get_channel(ctx, channel_id, expand):
    """Get a single notification channel by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        channel_id_validated = validate_id(channel_id, "notification channel")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            channel = await client.notification_channels.get_one(
                channel_id_validated, expand=expand
            )
            return channel.data

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@notification_channels_group.command(name="create")
@click.option("--name", help="Channel name")
@click.option("--emails", required=True, help="Email addresses (comma-separated)")
@click.option("--webhooks", help="Webhook URLs (comma-separated)")
@click.option("--is-active", type=bool, help="Set channel as active (true/false)")
@click.option("--is-default", type=bool, help="Set as default channel (true/false)")
@click.pass_context
def create_channel(
    ctx,
    name,
    emails,
    webhooks,
    is_active,
    is_default,
):
    """Create a new notification channel"""

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        # Parse comma-separated emails into list
        emails_list = [email.strip() for email in emails.split(",") if email.strip()]
        if not emails_list:
            raise click.BadParameter("At least one email address is required")

        channel_data = {
            "emails": emails_list,
            "tenant": stored_tenant_id,
            "created_by": stored_user_id,
            "modified_by": stored_user_id,
        }

        if name:
            channel_data["name"] = f'{name}-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
            channel_data["display_name"] = name

        # Parse comma-separated webhooks into list
        if webhooks:
            channel_data["webhooks"] = [webhook.strip() for webhook in webhooks.split(",") if webhook.strip()]

        if is_active is not None:
            channel_data["is_active"] = is_active

        if is_default is not None:
            channel_data["is_default"] = is_default

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Creating notification channel with parameters: {channel_data}[/blue]"
                )

            new_channel = await client.notification_channels.create(channel_data)
            return new_channel.data

    result = asyncio.run(_run())
    print_message(
        f"[green]Notification channel created successfully with ID: {result['id']}[/green]",
        ctx.obj["FORMAT"],
    )
    format_output(result, ctx.obj["FORMAT"])


@notification_channels_group.command(name="update")
@click.argument("channel_id")
@click.option("--name", help="New channel name")
@click.option("--emails", help="Email addresses (comma-separated)")
@click.option("--webhooks", help="Webhook URLs (comma-separated)")
@click.option("--is-active", type=bool, help="Set channel as active (true/false)")
@click.option("--is-default", type=bool, help="Set as default channel (true/false)")
@click.pass_context
def update_channel(
    ctx,
    channel_id,
    name,
    emails,
    webhooks,
    is_active,
    is_default,
):
    """Update an existing notification channel"""

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        channel_id_validated = validate_id(channel_id, "notification channel")

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

            if emails:
                update_data["emails"] = [email.strip() for email in emails.split(",") if email.strip()]
                has_updates = True

            if webhooks:
                update_data["webhooks"] = [webhook.strip() for webhook in webhooks.split(",") if webhook.strip()]
                has_updates = True

            if is_active is not None:
                update_data["is_active"] = is_active
                has_updates = True

            if is_default is not None:
                update_data["is_default"] = is_default
                has_updates = True

            if not has_updates:
                print_message("[yellow]No updates provided[/yellow]", ctx.obj["FORMAT"])
                return None

            if ctx.obj.get("VERBOSE"):
                console.print(f"[blue]Updating notification channel with: {update_data}[/blue]")

            updated_channel = await client.notification_channels.update(
                channel_id_validated, update_data
            )
            return updated_channel.data

    try:
        result = asyncio.run(_run())
        if result:
            print_message(
                f"[green]Notification channel updated successfully: {result.get('name', result['id'])}[/green]",
                ctx.obj["FORMAT"],
            )
            format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        if ctx.obj.get("VERBOSE"):
            print_message("[red]Error updating notification channel:[/red]", ctx.obj["FORMAT"])
            import traceback
            print_message(traceback.format_exc(), ctx.obj["FORMAT"])
        else:
            print_message(
                f"[red]Error updating notification channel:[/red] {str(e)}",
                ctx.obj["FORMAT"],
            )
        exit(1)


@notification_channels_group.command(name="delete")
@click.argument("channel_id")
@click.confirmation_option(
    prompt="Are you sure you want to delete this notification channel?"
)
@click.pass_context
def delete_channel(ctx, channel_id):
    """Delete a notification channel"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        channel_id_validated = validate_id(channel_id, "notification channel")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            success = await client.notification_channels.delete(channel_id_validated)
            return {"success": success, "id": channel_id_validated}

    try:
        result = asyncio.run(_run())
        print_message(
            f"[green]Notification channel deleted successfully: {result['id']}[/green]",
            ctx.obj["FORMAT"],
        )
    except Exception as e:
        print_message(
            f"[red]Error deleting notification channel:[/red] {str(e)}",
            ctx.obj["FORMAT"],
        )
        exit(1)

