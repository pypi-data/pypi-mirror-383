"""Common completion providers."""

from __future__ import annotations

from copy import copy
import inspect
import os
from typing import TYPE_CHECKING, Any


try:
    from upath import UPath as Path
except ImportError:
    from pathlib import Path  # type: ignore[assignment]

from collections.abc import Awaitable, Iterable
from typing import TypeGuard, cast

from slashed import utils
from slashed.completion import CompletionItem, CompletionProvider
from slashed.log import get_logger


type PathType = str | os.PathLike[str]


if TYPE_CHECKING:
    from collections.abc import (
        AsyncIterator,
        Awaitable,
        Callable,
        Sequence,
    )

    from slashed.completion import CompletionContext
    from slashed.slashed_types import CompletionKind

logger = get_logger(__name__)


def is_awaitable[T](obj: Awaitable[T] | T) -> TypeGuard[Awaitable[T]]:
    """Type guard to check if object is awaitable."""
    return inspect.isawaitable(obj)


class PathCompleter(CompletionProvider):
    """Provides filesystem path completions."""

    def __init__(
        self,
        file_patterns: list[str] | None = None,
        *,
        directories: bool = True,
        files: bool = True,
        show_hidden: bool = False,
        expanduser: bool = True,
        base_path: str | os.PathLike[str] | None = None,
    ):
        """Initialize path completer.

        Args:
            file_patterns: Optional glob patterns to filter files
            directories: Whether to include directories
            files: Whether to include files
            show_hidden: Whether to show hidden files
            expanduser: Whether to expand user directory (~)
            base_path: Optional base path to resolve relative paths against
        """
        self.file_patterns = file_patterns
        self.directories = directories
        self.files = files
        self.show_hidden = show_hidden
        self.expanduser = expanduser
        self.base_path = Path(base_path).resolve() if base_path else None

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get path completions."""
        word = context.current_word or "."

        try:
            # Handle absolute paths
            if Path(word).is_absolute():
                path = Path(word)
            # Handle user paths
            elif self.expanduser and word.startswith("~"):
                path = Path(word).expanduser()
            # Handle relative paths
            else:
                # If base_path is set, resolve relative to it
                base = self.base_path or Path.cwd()
                path = (base / word).resolve()

            # If path doesn't exist, use its parent for listing
            if not path.exists():
                completion_dir = path.parent
                prefix = path.name
            else:
                completion_dir = path
                prefix = ""

            # List directory contents
            for entry in completion_dir.iterdir():
                # Skip hidden unless enabled
                if not self.show_hidden and entry.name.startswith("."):
                    continue

                # Skip if doesn't match prefix
                if prefix and not entry.name.startswith(prefix):
                    continue

                # Apply type filters
                if entry.is_dir():
                    if not self.directories:
                        continue
                elif entry.is_file():
                    if not self.files:
                        continue
                    if self.file_patterns and not any(
                        entry.match(pattern) for pattern in self.file_patterns
                    ):
                        continue

                # Get relative path if using base_path
                if self.base_path:
                    try:
                        display = str(entry.relative_to(self.base_path))
                    except ValueError:
                        display = str(entry)
                else:
                    display = str(entry)

                # Create completion
                name = str(entry)
                if entry.is_dir():
                    name = f"{name}{os.sep}"
                    kind = "directory"
                else:
                    kind = utils.get_file_kind(entry)
                meta = utils.get_metadata(entry)
                yield CompletionItem(text=name, display=display, kind=kind, metadata=meta)  # type: ignore[arg-type]

        except Exception as e:  # noqa: BLE001
            # Log error but don't raise
            logger.debug("Path completion error: %s", e)


class EnvVarCompleter(CompletionProvider):
    """Environment variable completion."""

    def __init__(
        self,
        prefixes: Sequence[str] | None = None,
        include_values: bool = True,
    ):
        """Initialize environment variable completer.

        Args:
            prefixes: Optional prefixes to filter variables
            include_values: Whether to show current values
        """
        self.prefixes = prefixes
        self.include_values = include_values

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get environment variable completions."""
        word = context.current_word.lstrip("$")

        for key, value in os.environ.items():
            if self.prefixes and not any(key.startswith(p) for p in self.prefixes):
                continue

            if key.startswith(word):
                meta = value[:50] + "..." if self.include_values else None
                yield CompletionItem(text=f"${key}", metadata=meta, kind="env")  # type: ignore[arg-type]


class ChoiceCompleter(CompletionProvider):
    """Provides completion from a fixed set of choices."""

    def __init__(
        self,
        choices: Sequence[str] | dict[str, str],
        ignore_case: bool = True,
    ):
        """Initialize choice completer.

        Args:
            choices: Sequence of choices or mapping of choice -> description
            ignore_case: Whether to do case-insensitive matching
        """
        self.ignore_case = ignore_case
        if isinstance(choices, dict):
            self.choices = list(choices.keys())
            self.descriptions = choices
        else:
            self.choices = list(choices)
            self.descriptions = {}

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get matching choices."""
        word = context.current_word
        if self.ignore_case:
            word = word.lower()
            matches = (c for c in self.choices if c.lower().startswith(word))
        else:
            matches = (c for c in self.choices if c.startswith(word))

        for choice in matches:
            meta = self.descriptions.get(choice)
            yield CompletionItem(text=choice, metadata=meta, kind="choice")  # type: ignore[arg-type]


class MultiValueCompleter(CompletionProvider):
    """Completes multiple values separated by a delimiter."""

    def __init__(
        self,
        provider: CompletionProvider,
        delimiter: str = ",",
        strip: bool = True,
    ):
        """Initialize multi-value completer.

        Args:
            provider: Base provider for individual values
            delimiter: Value separator
            strip: Whether to strip whitespace from values
        """
        self.provider = provider
        self.delimiter = delimiter
        self.strip = strip

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get completions for current value."""
        # Use full text instead of just current_word for splitting
        full_text = context._document.text
        values = full_text.split(self.delimiter)

        # Current value is what's being typed
        current = context.current_word
        if self.strip:
            current = current.strip()

        # Create modified context with just the current value
        mod_context = copy(context)
        mod_context._current_word = current  # type: ignore[attr-defined]

        # Build prefix from previous values if we have more than one value
        prefix = ""
        if len(values) > 1:
            prefix = self.delimiter.join(values[:-1])
            prefix = f"{prefix}{self.delimiter}"
            if self.strip:
                prefix = f"{prefix} "

        # Get completions and add prefix
        async for item in self.provider.get_completions(mod_context):
            item = copy(item)  # Don't modify original item
            if prefix:
                item.text = f"{prefix}{item.text}"
            yield item


class KeywordCompleter(CompletionProvider):
    """Completes keyword arguments."""

    def __init__(
        self,
        keywords: dict[str, Any],
        value_provider: CompletionProvider | None = None,
    ):
        """Initialize keyword completer.

        Args:
            keywords: Mapping of keyword names to descriptions/types
            value_provider: Optional provider for keyword values
        """
        self.keywords = keywords
        self.value_provider = value_provider

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get keyword completions."""
        word = context.current_word

        # Complete keyword names
        if word.startswith("--"):
            prefix = word[2:]
            for name, desc in self.keywords.items():
                if name.startswith(prefix):
                    yield CompletionItem(f"--{name}", metadata=str(desc), kind="keyword")  # type: ignore[arg-type]
            return

        # Complete keyword values if provider exists
        if self.value_provider and context.arg_position > 0:
            prev_arg = context.command_args[context.arg_position - 1]
            if prev_arg.startswith("--"):
                async for item in self.value_provider.get_completions(context):
                    yield item


class ChainedCompleter(CompletionProvider):
    """Combines multiple completers."""

    def __init__(self, *providers: CompletionProvider):
        """Initialize chained completer.

        Args:
            providers: Completion providers to chain
        """
        self.providers = providers

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        """Get completions from all providers."""
        for provider in self.providers:
            async for item in provider.get_completions(context):
                yield item


class CallbackCompleter(CompletionProvider):
    """Completer that calls a function to get completions dynamically.

    The callback can return either strings or CompletionItems.

    Example:
        def complete_tools(ctx: CompletionContext) -> Iterator[str]:
            tools = ["hammer", "screwdriver", "wrench"]
            return (t for t in tools if t.startswith(ctx.current_word))

        command = Command(
            name="use-tool",
            description="Use a tool",
            completer=CallbackCompleter(complete_tools)
        )
    """

    def __init__(
        self,
        callback: (
            Callable[[CompletionContext], Iterable[str | CompletionItem]]
            | Callable[[CompletionContext], Awaitable[Iterable[str | CompletionItem]]]
        ),
        kind: CompletionKind | None = None,
    ):
        self._callback = callback
        self._kind = kind
        self._is_async = inspect.iscoroutinefunction(callback)

    async def get_completions(
        self,
        context: CompletionContext,
    ) -> AsyncIterator[CompletionItem]:
        try:
            result = self._callback(context)

            # Narrow type and handle async/sync appropriately
            if is_awaitable(result):
                items = await result
            else:
                items = cast(Iterable[str | CompletionItem], result)

            for item in items:
                if isinstance(item, str):
                    yield CompletionItem(text=item, kind=self._kind)  # type: ignore
                else:
                    yield item
        except Exception as e:  # noqa: BLE001
            logger.debug("Completion callback error: %s", e)
