"""Help command implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from slashed.base import Command, CommandContext  # noqa: TC001
from slashed.completers import CallbackCompleter
from slashed.completion import CompletionItem
from slashed.exceptions import ExitCommandError


if TYPE_CHECKING:
    from collections.abc import Iterator

    from slashed.completion import CompletionContext, CompletionProvider


HELP_HELP = """\
Display help information about commands.

Usage:
  /help           List all available commands
  /help <command> Show detailed help for a command

Example: /help exit
"""


async def help_command(
    ctx: CommandContext,
    args: list[str],
    kwargs: dict[str, str],
):
    """Show available commands or detailed help for a specific command."""
    store = ctx.command_store
    output_lines = []

    if args:  # Detail for specific command
        name = args[0]
        if cmd := store.get_command(name):
            sections = [
                f"**Command:** /{cmd.name}",
                f"**Category:** {cmd.category}",
                "",
                "**Description:**",
                cmd.description,
                "",
            ]
            if cmd.usage:
                sections.extend(["**Usage:**", f"/{cmd.name} {cmd.usage}", ""])
            if cmd.help_text:
                sections.extend(["**Help:**", cmd.help_text])

            output_lines.extend(sections)
        else:
            output_lines.append(f"**Unknown command:** {name}")
    else:
        # List all commands grouped by category
        categories = store.get_commands_by_category()
        output_lines.append("\n**Available commands:**")
        for category, commands in categories.items():
            output_lines.extend([
                f"\n{category.title()}:",
                *[f"  /{cmd.name:<16} - *{cmd.description}*" for cmd in commands],
            ])

    await ctx.output.print("\n\n".join(output_lines))


def create_help_completer() -> CompletionProvider:
    """Create completer for help command that suggests command names."""

    def get_choices(context: CompletionContext) -> Iterator[CompletionItem]:
        store = context.command_context.command_store
        for cmd in store.list_commands():
            yield CompletionItem(text=cmd.name, metadata=cmd.description, kind="command")

    return CallbackCompleter(get_choices)


help_cmd = Command(
    name="help",
    description="Show help about commands",
    execute_func=help_command,
    usage="[command]",
    help_text=HELP_HELP,
    category="system",
    completer=create_help_completer,
)


async def exit_command(
    ctx: CommandContext,
    args: list[str],
    kwargs: dict[str, str],
):
    """Exit the chat session."""
    msg = "Session ended."
    raise ExitCommandError(msg)


exit_cmd = Command(
    name="exit",
    description="Exit chat session",
    execute_func=exit_command,
    category="system",
)
