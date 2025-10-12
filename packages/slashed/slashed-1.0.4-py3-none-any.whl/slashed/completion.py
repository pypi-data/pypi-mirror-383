"""Command completion system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar

from slashed.log import get_logger


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from prompt_toolkit.document import Document

    from slashed.base import BaseCommand, CommandContext
    from slashed.slashed_types import CompletionKind

TCommandData = TypeVar("TCommandData", default=Any)

logger = get_logger(__name__)


@dataclass
class CompletionItem:
    """Single completion suggestion."""

    text: str
    """Text to insert"""

    display: str | None = None
    """Optional display text (defaults to text)"""

    metadata: str | None = None
    """Additional information to show"""

    kind: CompletionKind | None = None
    """Type of completion item"""

    sort_text: str | None = None
    """Optional text to use for sorting (defaults to text)"""


class CompletionContext[TCommandData]:
    """Context for completion operations.

    Type Parameters:
        TCommandData: Type of the data in the associated CommandContext. Used when
                     completions need to access the command context data.
    """

    def __init__(
        self,
        document: Document,
        command_context: CommandContext[TCommandData] | None = None,
    ):
        """Initialize completion context.

        Args:
            document: Current document being completed
            command_context: Optional command execution context
        """
        self._document = document
        self._command_context = command_context
        self._command_name: str | None = None
        self._args: list[str] = []
        self._current_word: str = ""
        self._arg_position: int = 0
        self._parse_document()

    @property
    def command_context(self) -> CommandContext[TCommandData]:
        """Get command execution context.

        Returns:
            Command context

        Raises:
            RuntimeError: If command context is not set
        """
        if self._command_context is None:
            msg = "No command context available"
            raise RuntimeError(msg)
        return self._command_context

    def has_command_context(self) -> bool:
        """Check if command context is available."""
        return self._command_context is not None

    def _parse_document(self):
        """Parse document into command and arguments."""
        text = self._document.text.lstrip()

        if not text.startswith("/"):
            self._command_name = None
            self._args = []
            self._current_word = self._document.get_word_before_cursor()
            self._arg_position = 0
            return

        parts = text[1:].split()
        self._command_name = parts[0] if parts else None
        self._args = parts[1:]
        self._current_word = self._document.get_word_before_cursor()
        self._arg_position = len(text[: self._document.cursor_position].split()) - 1
        logger.info(
            "Parsed command %s with args %s. Current word: %s (position %d)",
            self._command_name,
            self._args,
            self._current_word,
            self._arg_position,
        )

    @property
    def command_name(self) -> str | None:
        """Get current command name if any."""
        return self._command_name

    @property
    def current_word(self) -> str:
        """Get word being completed."""
        return self._current_word

    @property
    def arg_position(self) -> int:
        """Get current argument position."""
        return self._arg_position

    @property
    def command_args(self) -> list[str]:
        """Get current command arguments."""
        return self._args


class CompletionProvider(ABC):
    """Base class for completion providers."""

    @abstractmethod
    def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get completion suggestions."""


class CommandCompleter:
    """Main command completion implementation."""

    def __init__(self, commands: dict[str, BaseCommand]):
        """Initialize command completer.

        Args:
            commands: Mapping of command names to command instances
        """
        self._commands = commands
        self._global_providers: list[CompletionProvider] = []

    def add_global_provider(self, provider: CompletionProvider):
        """Add a global completion provider."""
        self._global_providers.append(provider)

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get completions for the current context."""
        # If at start of command, complete command names
        logger.debug("Getting completions for command %s", context.command_name)
        if not context.command_name:
            word = context.current_word.lstrip("/")  # Remove slash for matching
            matching_commands = [name for name in self._commands if name.startswith(word)]

            # If exactly one match, complete it
            if len(matching_commands) == 1:
                meta = self._commands[matching_commands[0]].description
                cmd = matching_commands[0]
                yield CompletionItem(text=cmd, metadata=meta, kind="command")
            # If multiple matches, show all
            elif len(matching_commands) > 1:
                for name in matching_commands:
                    meta = self._commands[name].description
                    yield CompletionItem(text=name, metadata=meta, kind="command")
            return
        # Get command-specific completions
        # Get command-specific completions
        command = self._commands.get(context.command_name)
        if command and (completer := command.get_completer()):
            logger.debug("Fetching completions for command %s", command.name)
            async for item in completer.get_completions(context):
                yield item

        # Get global completions
        for provider in self._global_providers:
            logger.debug("Fetching completions for provider %r", provider)
            async for item in provider.get_completions(context):
                yield item
