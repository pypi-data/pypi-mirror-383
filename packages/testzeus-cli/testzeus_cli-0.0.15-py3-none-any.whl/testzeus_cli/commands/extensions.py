"""
Commands for managing extensions in TestZeus CLI.
"""

import asyncio
import json
import click
from rich.console import Console
from pathlib import Path

from testzeus_sdk import TestZeusClient
from testzeus_cli.config import get_client_config
from testzeus_cli.utils.formatters import format_output, print_message
from testzeus_cli.utils.validators import validate_id, parse_key_value_pairs
from testzeus_cli.utils.auth import initialize_client_with_token

console = Console()


@click.group(name="extension")
def extensions_group():
    """Manage TestZeus extensions"""
    pass


@extensions_group.command(name="list")
@click.option(
    "--filters", "-f", multiple=True, help="Filter results (format: key=value)"
)
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=50, help="Items per page")
@click.pass_context
def list_extensions(ctx, filters, sort, expand, page, per_page):
    """List extensions with optional filters and sorting"""

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

            extensions = await client.extensions.get_list(
                expand=expand, sort=sort, filters=filter_dict, page=page, per_page=per_page
            )
            return extensions

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@extensions_group.command(name="get")
@click.argument("extension_id")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.pass_context
def get_extension(ctx, extension_id, expand):
    """Get a single extension by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        extension_id_validated = validate_id(extension_id, "extension")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            extension = await client.extensions.get_one(
                extension_id_validated, expand=expand
            )
            return extension.data

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@extensions_group.command(name="create")
@click.option("--name", help="Extension name")
@click.option("--data-content", help="Data content as text")
@click.option("--data-file", help="Path to file containing data content")
@click.pass_context
def create_extension(
    ctx,
    name,
    data_content,
    data_file,
):
    """Create a new extension"""

    if data_content and data_file:
        raise click.UsageError("Cannot use both --data-content and --data-file")

    # Read data from file if provided
    if data_file:
        data_path = Path(data_file)
        if not data_path.exists():
            raise click.BadParameter(f"Data file not found: {data_file}")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data_content = f.read()
        except Exception as e:
            raise click.BadParameter(f"Failed to read data file: {str(e)}")

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        extension_data = {}

        if stored_tenant_id:
            extension_data["tenant"] = stored_tenant_id

        if stored_user_id:
            extension_data["modified_by"] = stored_user_id

        if name:
            extension_data["name"] = name

        if data_content:
            extension_data["data_content"] = data_content

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Creating extension with parameters: {extension_data}[/blue]"
                )

            new_extension = await client.extensions.create(extension_data)
            return new_extension.data

    result = asyncio.run(_run())
    print_message(
        f"[green]Extension created successfully with ID: {result['id']}[/green]",
        ctx.obj["FORMAT"],
    )
    format_output(result, ctx.obj["FORMAT"])


@extensions_group.command(name="delete")
@click.argument("extension_id")
@click.confirmation_option(
    prompt="Are you sure you want to delete this extension?"
)
@click.pass_context
def delete_extension(ctx, extension_id):
    """Delete an extension"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        extension_id_validated = validate_id(extension_id, "extension")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            success = await client.extensions.delete(extension_id_validated)
            return {"success": success, "id": extension_id_validated}

    try:
        result = asyncio.run(_run())
        print_message(
            f"[green]Extension deleted successfully: {result['id']}[/green]",
            ctx.obj["FORMAT"],
        )
    except Exception as e:
        print_message(
            f"[red]Error deleting extension:[/red] {str(e)}",
            ctx.obj["FORMAT"],
        )
        exit(1)

