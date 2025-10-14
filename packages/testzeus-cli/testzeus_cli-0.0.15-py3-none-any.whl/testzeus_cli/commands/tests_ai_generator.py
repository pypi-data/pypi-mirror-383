"""
Commands for managing AI test generator in TestZeus CLI.
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


@click.group(name="testcase-generator")
def tests_ai_generator_group():
    """Manage TestZeus AI test generator"""
    pass


@tests_ai_generator_group.command(name="list")
@click.option(
    "--filters", "-f", multiple=True, help="Filter results (format: key=value)"
)
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=50, help="Items per page")
@click.pass_context
def list_ai_generators(ctx, filters, sort, expand, page, per_page):
    """List AI test generators with optional filters and sorting"""

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

            generators = await client.tests_ai_generator.get_list(
                expand=expand, sort=sort, filters=filter_dict, page=page, per_page=per_page
            )
            return generators

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@tests_ai_generator_group.command(name="get")
@click.argument("generator_id")
@click.option("--expand", help="Expand related entities (comma-separated)")
@click.pass_context
def get_ai_generator(ctx, generator_id, expand):
    """Get a single AI test generator by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        generator_id_validated = validate_id(generator_id, "AI test generator")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            generator = await client.tests_ai_generator.get_one(
                generator_id_validated, expand=expand
            )
            return generator.data

    result = asyncio.run(_run())
    format_output(result, ctx.obj["FORMAT"])


@tests_ai_generator_group.command(name="create")
@click.option("--test-id", required=True, help="Test ID to generate for")
@click.option("--test-data", multiple=True, help="Test data IDs")
@click.option("--environment", help="Environment ID")
@click.option("--test-feature", help="Test feature text")
@click.option("--test-feature-file", help="Path to file containing test feature")
@click.option("--user-prompt", required=True, help="User prompt for AI generation")
@click.option("--user-prompt-file", help="Path to file containing user prompt")
@click.option(
    "--reasoning-effort",
    type=click.Choice(["low", "medium", "high"]),
    default="low",
    help="AI reasoning effort level (default: low)",
)
@click.option("--num-testcases", type=click.IntRange(1, 20), default=3, help="Number of test cases to generate (1-20, default: 3)")
@click.pass_context
def create_ai_generator(
    ctx,
    test_id,
    test_data,
    environment,
    test_feature,
    test_feature_file,
    user_prompt,
    user_prompt_file,
    reasoning_effort,
    num_testcases,
):
    """Create a new AI test generator request"""

    if test_feature and test_feature_file:
        raise click.UsageError("Cannot use both --test-feature and --test-feature-file")

    if user_prompt and user_prompt_file:
        raise click.UsageError("Cannot use both --user-prompt and --user-prompt-file")

    # Validate that user_prompt is not empty
    if not user_prompt and not user_prompt_file:
        raise click.UsageError("Either --user-prompt or --user-prompt-file is required")
    
    if user_prompt and not user_prompt.strip():
        raise click.UsageError("User prompt cannot be empty")

    # Read test feature from file if provided
    if test_feature_file:
        feature_path = Path(test_feature_file)
        if not feature_path.exists():
            raise click.BadParameter(f"Test feature file not found: {test_feature_file}")
        try:
            with open(feature_path, "r", encoding="utf-8") as f:
                test_feature = f.read()
        except Exception as e:
            raise click.BadParameter(f"Failed to read test feature file: {str(e)}")

    # Read user prompt from file if provided
    if user_prompt_file:
        prompt_path = Path(user_prompt_file)
        if not prompt_path.exists():
            raise click.BadParameter(f"User prompt file not found: {user_prompt_file}")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                user_prompt = f.read()
        except Exception as e:
            raise click.BadParameter(f"Failed to read user prompt file: {str(e)}")

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        generator_data = {
            "test": test_id,
            "tenant": stored_tenant_id,
            "modified_by": stored_user_id,
        }

        if test_data:
            generator_data["test_data"] = list(test_data)

        if environment:
            generator_data["environment"] = environment

        if test_feature:
            generator_data["test_feature"] = test_feature

        if user_prompt:
            generator_data["user_prompt"] = user_prompt

        if reasoning_effort:
            generator_data["reasoning_effort"] = reasoning_effort

        if num_testcases is not None:
            generator_data["num_of_testcases"] = num_testcases

        # Always set submit to true
        generator_data["submit"] = True

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            if ctx.obj.get("VERBOSE"):
                console.print(
                    f"[blue]Creating AI test generator with parameters: {generator_data}[/blue]"
                )

            new_generator = await client.tests_ai_generator.create(generator_data)
            return new_generator.data

    result = asyncio.run(_run())
    print_message(
        f"[green]AI test generator created successfully with ID: {result['id']}[/green]",
        ctx.obj["FORMAT"],
    )
    format_output(result, ctx.obj["FORMAT"])


@tests_ai_generator_group.command(name="delete")
@click.argument("generator_id")
@click.confirmation_option(
    prompt="Are you sure you want to delete this AI test generator?"
)
@click.pass_context
def delete_ai_generator(ctx, generator_id):
    """Delete an AI test generator"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        generator_id_validated = validate_id(generator_id, "AI test generator")

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()

            success = await client.tests_ai_generator.delete(generator_id_validated)
            return {"success": success, "id": generator_id_validated}

    try:
        result = asyncio.run(_run())
        print_message(
            f"[green]AI test generator deleted successfully: {result['id']}[/green]",
            ctx.obj["FORMAT"],
        )
    except Exception as e:
        print_message(
            f"[red]Error deleting AI test generator:[/red] {str(e)}",
            ctx.obj["FORMAT"],
        )
        exit(1)

